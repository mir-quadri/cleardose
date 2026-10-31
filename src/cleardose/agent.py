"""ClearDose agent: Strands Agent + a deterministic offline router.

Two paths, one safety contract:

1. Strands path (create_strands_agent): a real strands.Agent with the
   four tools, used when a model is configured — e.g. Amazon Bedrock
   in the Builder Center workshop sandbox. The system prompt forbids
   safety claims and dosing advice, and every assistant message is
   filtered by a Strands hook (see SafetyHook) running
   safety.check_output_safety before the result is returned: any
   text that calls a combination safe or gives dosing advice is
   replaced wholesale with a withheld-answer message. Live streaming
   output is suppressed (callback_handler discards streamed chunks),
   so unfiltered model text is never printed while it streams — the
   caller only ever sees the filtered final message.

2. Deterministic path (DeterministicAgent): no model call at all.
   It routes an explicit request to the right tool and formats the
   tool result. This is the path tests and the offline demo use, so
   a demo can never hallucinate a label flag.
"""
from __future__ import annotations

import base64
from typing import Any

from .labels import LabelLookup, OpenFDALabelClient
from .ocr import OCRProvider, ocr_provider_from_env
from .safety import DISCLAIMER, check_output_safety, with_disclaimer
from .tools import (
    check_label_photo,
    explain_prescription,
    flag_interactions,
    generate_pharmacist_questions,
)

SAFE_WITHHELD = (
    "That answer was withheld because it contained a claim or "
    "instruction ClearDose cannot show. Please ask your pharmacist "
    "or doctor about this medicine.\n\n" + DISCLAIMER
)


class SafetyHook:
    """Strands hook that enforces the safety filter on model text.

    Registered on MessageAddedEvent: when the framework adds an
    assistant message to the conversation, each text block is run
    through check_output_safety. Unsafe blocks are replaced wholesale
    (never edited into shape); safe blocks get the full disclaimer
    appended if it is missing. Because Strands mutates the same
    message dict that becomes the invocation result and the stored
    history, this replacement reaches both — verified by the stub
    -model invocation test in tests/test_agent.py. This hook does
    not filter tool-result blocks or user messages.
    """

    def register_hooks(self, registry, **kwargs):  # noqa: ANN001, ANN202
        from strands.hooks.events import MessageAddedEvent

        registry.add_callback(MessageAddedEvent, self.on_message_added)

    def on_message_added(self, event) -> None:  # noqa: ANN001
        message = event.message
        if message.get("role") != "assistant":
            return
        for block in message.get("content", []):
            if not isinstance(block, dict) or "text" not in block:
                continue
            text = block["text"]
            if not text.strip():
                continue
            filtered = check_output_safety(text)
            block["text"] = SAFE_WITHHELD if filtered is None else filtered

SYSTEM_PROMPT = """You are ClearDose, a plain-language prescription explainer for
older adults and people with low health literacy.

Rules you must never break:
- Advisory only, never medical advice. Never say a medicine or a
  combination is safe. Never tell anyone how much to take, or how
  to change a dose.
- Explain from FDA label text only, using the tools. Show the label
  section each excerpt came from. If a label cannot be retrieved,
  say so plainly and do not guess.
- Use short sentences and everyday words for your own summary words
  (label quotes stay verbatim). Define any medical word
  you must use.
- End every answer with the advisory disclaimer.
"""


def create_strands_agent(model: Any = None, ocr: OCRProvider | None = None):
    """Build the real Strands Agent. `model` is a model id / Model object.

    Construction does not call a model; invocation does. Callers that
    pass no model get the default Strands/Bedrock configuration, which
    requires AWS credentials at invocation time.
    """
    from strands import Agent

    from .strands_tools import (
        explain_prescription as explain_tool,
        flag_interactions as flag_tool,
        generate_pharmacist_questions as questions_tool,
        make_check_label_photo_tool,
    )

    kwargs: dict[str, Any] = {
        "tools": [
            explain_tool,
            flag_tool,
            questions_tool,
            make_check_label_photo_tool(ocr),
        ],
        "system_prompt": SYSTEM_PROMPT,
        # Safety enforcement, strands-agents==1.62.0: the hook above
        # filters assistant messages before the result is returned.
        # The no-op callback handler suppresses live streaming output
        # so unfiltered text is never printed mid-stream; callers see
        # only the filtered final message.
        "hooks": [SafetyHook()],
        "callback_handler": lambda **_kwargs: None,
    }
    if model is not None:
        kwargs["model"] = model
    return Agent(**kwargs)


class DeterministicAgent:
    """Model-free router over the same tools, for tests and offline demo."""

    def __init__(
        self,
        fetch=None,
        ocr: OCRProvider | None = None,
    ):
        self._client = OpenFDALabelClient()
        self._fetch = fetch or self._client.fetch
        self._ocr = ocr or ocr_provider_from_env()

    def explain(self, medicine: str) -> dict:
        return explain_prescription(medicine, self._fetch)

    def flag(self, candidate: str, current_medicines: list[str]) -> dict:
        return flag_interactions(candidate, current_medicines, self._fetch)

    def questions(self, medicine: str, current_medicines: list[str]) -> dict:
        return generate_pharmacist_questions(medicine, current_medicines, self._fetch)

    def photo(self, image_bytes: bytes, current_medicines: list[str]) -> dict:
        return check_label_photo(image_bytes, current_medicines, self._fetch, self._ocr)

    def photo_base64(self, image_base64: str, current_medicines: list[str]) -> dict:
        try:
            image_bytes = base64.b64decode(image_base64, validate=True)
        except Exception:
            return with_disclaimer(
                {
                    "photo_read": False,
                    "summary": "The photo data was not valid base64.",
                }
            )
        return self.photo(image_bytes, current_medicines)

    def answer(self, request: str, current_medicines: list[str] | None = None) -> dict:
        """Route a plain request string to a tool, without a model call."""
        current_medicines = current_medicines or []
        lowered = request.lower()
        if "question" in lowered:
            medicine = _first_medicine_word(request) or "medicine"
            return self.questions(medicine, current_medicines)
        if "photo" in lowered or "bottle" in lowered or "label photo" in lowered:
            return with_disclaimer(
                {
                    "summary": (
                        "Photo checks need image bytes — use the photo() method "
                        "or the CLI `photo` command with a file path."
                    ),
                }
            )
        if "interact" in lowered or "together" in lowered or "with " in lowered:
            candidate = _first_medicine_word(request)
            if candidate:
                return self.flag(candidate, current_medicines)
        medicine = _first_medicine_word(request)
        if medicine:
            return self.explain(medicine)
        return with_disclaimer(
            {
                "summary": (
                    "Tell ClearDose a medicine name, for example: "
                    "'Explain ibuprofen' or 'Check ibuprofen with warfarin'."
                ),
            }
        )


def _first_medicine_word(request: str) -> str | None:
    from .names import all_known_names

    lowered = request.lower()
    earliest: tuple[int, str] | None = None
    for name in all_known_names():
        index = lowered.find(name)
        if index >= 0 and (earliest is None or index < earliest[0]):
            earliest = (index, name)
    return earliest[1] if earliest else None


def filter_model_text(text: str) -> str | None:
    """Apply the safety filter to model-generated text. None = discard."""
    return check_output_safety(text)


__all__ = [
    "SYSTEM_PROMPT",
    "DeterministicAgent",
    "create_strands_agent",
    "filter_model_text",
    "SafetyHook",
    "SAFE_WITHHELD",
    "LabelLookup",
]
