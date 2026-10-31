import os

import pytest

from cleardose.ocr import MockOCRProvider, RekognitionOCRProvider, OCRNotConfigured


def test_mock_returns_synthetic_label_marked_synthetic():
    result = MockOCRProvider("ibuprofen-200mg").read_text(b"bytes")
    assert result.synthetic is True
    assert result.provider == "mock-ocr"
    assert [ln.text for ln in result.lines][0] == "IBUPROFEN 200 mg Tablets"


def test_env_sample_uses_correct_spelling_with_legacy_fallback(monkeypatch):
    from cleardose.ocr import ocr_provider_from_env

    monkeypatch.delenv("REKOGNITION_ENABLED", raising=False)
    monkeypatch.delenv("CLEARDOS_DEMO_SAMPLE", raising=False)
    monkeypatch.setenv("CLEARDose_DEMO_SAMPLE", "acetaminophen-500mg")
    assert ocr_provider_from_env().sample_name == "acetaminophen-500mg"
    monkeypatch.delenv("CLEARDose_DEMO_SAMPLE", raising=False)
    monkeypatch.setenv("CLEARDOS_DEMO_SAMPLE", "acetaminophen-500mg")
    assert ocr_provider_from_env().sample_name == "acetaminophen-500mg"


def test_mock_unknown_sample_returns_no_lines():
    result = MockOCRProvider("nope").read_text(b"bytes")
    assert result.lines == []


def test_rekognition_not_configured_by_default(monkeypatch):
    monkeypatch.delenv("REKOGNITION_ENABLED", raising=False)
    assert RekognitionOCRProvider.is_configured() is False
    with pytest.raises(OCRNotConfigured):
        RekognitionOCRProvider().read_text(b"bytes")


def test_rekognition_rejects_oversize_image(monkeypatch):
    monkeypatch.setenv("REKOGNITION_ENABLED", "true")
    with pytest.raises(Exception):
        RekognitionOCRProvider().read_text(b"x" * 5_000_001)
