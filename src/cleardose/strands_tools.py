"""Strands @tool wrappers around the deterministic tools in tools.py.

The Strands Agent calls these; the safety and provenance logic lives
in tools.py so it is testable without a model. Tool docstrings are
the contract the model sees — they state the advisory limits plainly.
"""
from __future__ import annotations

from strands import tool

from .labels import OpenFDALabelClient
from .ocr import OCRProvider, ocr_provider_from_env
from .safety import with_disclaimer
from .tools import (
    check_label_photo as _check_label_photo,
)
from .tools import (
    explain_prescription as _explain_prescription,
)
from .tools import (
    flag_interactions as _flag_interactions,
)
from .tools import (
    generate_pharmacist_questions as _generate_pharmacist_questions,
)

_label_client = OpenFDALabelClient()


def _fetch(medicine: str):
    return _label_client.fetch(medicine)


@tool
def explain_prescription(medicine: str) -> dict:
    """Explain a prescription from its FDA label, under plain-language
    headings with verbatim label excerpts. The label text itself is
    not rewritten or simplified. Returns the advisory disclaimer.
    Advisory only, never medical advice.
    """
    return _explain_prescription(medicine, _fetch)


@tool
def flag_interactions(candidate: str, current_medicines: list[str]) -> dict:
    """Flag label interactions between a new medicine and medicines already
    taken, checking both labels. Never calls a combination safe.
    """
    return _flag_interactions(candidate, current_medicines, _fetch)


@tool
def generate_pharmacist_questions(medicine: str, current_medicines: list[str]) -> dict:
    """Generate questions to ask a pharmacist about a new medicine."""
    return _generate_pharmacist_questions(medicine, current_medicines, _fetch)


def make_check_label_photo_tool(ocr: OCRProvider | None = None):
    """Build the photo tool bound to one OCR provider (mock by default)."""

    provider = ocr or ocr_provider_from_env()

    @tool
    def check_label_photo(image_base64: str, current_medicines: list[str]) -> dict:
        """Read a bottle-label photo, match the medicine, and run the
        interaction check. Photo bytes are sent to the OCR provider only;
        they are never stored. If no single medicine is matched, no
        check runs and no guess is made. Advisory only.
        """
        import base64

        try:
            image_bytes = base64.b64decode(image_base64, validate=True)
        except Exception:
            return with_disclaimer(
                {
                    "photo_read": False,
                    "summary": "The photo data was not valid base64.",
                }
            )
        return _check_label_photo(image_bytes, current_medicines, _fetch, provider)

    return check_label_photo


__all__ = [
    "explain_prescription",
    "flag_interactions",
    "generate_pharmacist_questions",
    "make_check_label_photo_tool",
]
