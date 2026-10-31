from cleardose.agent import (
    DeterministicAgent,
    create_strands_agent,
    filter_model_text,
)
from cleardose.cli import _demo_fetch
from cleardose.ocr import MockOCRProvider


def test_deterministic_router_explain_and_flag():
    agent = DeterministicAgent(fetch=_demo_fetch, ocr=MockOCRProvider())
    explained = agent.answer("Explain ibuprofen")
    assert explained["label_found"] is True
    flagged = agent.answer("Check ibuprofen together with warfarin", ["warfarin"])
    assert flagged["flag_count"] >= 1


def test_deterministic_router_photo_needs_bytes():
    agent = DeterministicAgent(fetch=_demo_fetch, ocr=MockOCRProvider())
    result = agent.answer("Read my bottle photo")
    assert "image bytes" in result["summary"]


def test_filter_model_text_rejects_unsafe():
    assert filter_model_text("It is safe to take.") is None
    assert filter_model_text("Here are your questions.") is not None


def test_strands_agent_constructs_without_invoking_model():
    # Construction only, with a stub Model — no model call, no
    # credentials, no network. A real Bedrock model id would make the
    # Agent resolve AWS credentials at construction time in this
    # environment, so the stub is the offline-proof construction path.
    from strands.models.model import Model

    class StubModel(Model):
        def get_config(self):
            return {}

        def update_config(self, **kwargs):
            pass

        async def stream(self, *args, **kwargs):
            if False:
                yield None

        async def structured_output(self, *args, **kwargs):
            return None

    agent = create_strands_agent(model=StubModel())
    tool_names = [
        tool.tool_name for tool in agent.tool_registry.registry.values()
    ]
    assert "explain_prescription" in tool_names
    assert "flag_interactions" in tool_names
    assert "generate_pharmacist_questions" in tool_names
    assert "check_label_photo" in tool_names


def _unsafe_stub_model():
    """Stub model that emits exactly one unsafe assistant message."""
    from strands.models.model import Model

    class UnsafeStubModel(Model):
        def get_config(self):
            return {}

        def update_config(self, **kwargs):
            pass

        async def stream(self, *args, **kwargs):
            yield {"messageStart": {"role": "assistant"}}
            yield {"contentBlockStart": {"contentBlockIndex": 0, "start": {}}}
            yield {
                "contentBlockDelta": {
                    "contentBlockIndex": 0,
                    "delta": {"text": "This combination is safe to take."},
                }
            }
            yield {"contentBlockStop": {"contentBlockIndex": 0}}
            yield {"messageStop": {"stopReason": "end_turn"}}

        async def structured_output(self, *args, **kwargs):
            return None

    return UnsafeStubModel()


def test_strands_hook_discards_unsafe_model_text_on_invocation():
    # The SafetyHook in create_strands_agent must replace unsafe
    # model text before the caller ever sees it — in the returned
    # result AND in the stored conversation history — and the no-op
    # callback handler means it is never printed mid-stream either.
    from cleardose.safety import DISCLAIMER

    agent = create_strands_agent(model=_unsafe_stub_model())
    result = agent("Is ibuprofen safe with warfarin?")
    texts = [
        block.get("text", "")
        for block in result.message.get("content", [])
        if isinstance(block, dict)
    ]
    joined = " ".join(texts)
    assert "safe to take" not in joined
    assert "withheld" in joined
    assert DISCLAIMER in joined
    history_texts = [
        block.get("text", "")
        for message in agent.messages
        for block in message.get("content", [])
        if isinstance(block, dict)
    ]
    assert "safe to take" not in " ".join(history_texts)
