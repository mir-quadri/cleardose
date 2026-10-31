"""Bottle-label photo reading: a pluggable OCR interface.

The agent never depends on one OCR vendor. A provider returns the
text lines it saw, each with a confidence score. Two providers ship:

* MockOCRProvider — returns the lines of a named synthetic sample.
  Used by tests and the demo. Every result is marked synthetic.
* RekognitionOCRProvider — Amazon Rekognition DetectText, env-gated.
  Until AWS credentials AND account activation are verified, it
  raises OCRNotConfigured and returns nothing. It never returns mock
  data, and photo bytes are never stored or logged by ClearDose.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class TextLine:
    text: str
    confidence: float
    kind: str = "LINE"


@dataclass
class OCRResult:
    lines: list[TextLine] = field(default_factory=list)
    provider: str = ""
    synthetic: bool = False


class OCRNotConfigured(Exception):
    """Raised when the requested OCR provider is not set up."""


class OCRUnavailable(Exception):
    """Raised when the OCR service call itself fails."""


class OCRProvider(Protocol):
    def read_text(self, image_bytes: bytes) -> OCRResult: ...


# Synthetic sample labels, keyed by the sample file's stem. The demo
# and tests use these names; nothing here is a real pharmacy bottle.
SYNTHETIC_SAMPLES: dict[str, list[tuple[str, float]]] = {
    # Dose sits on the name's own line, so dose attribution (tools.py,
    # own-line only) reports it without reading another line's dose.
    "ibuprofen-200mg": [
        ("IBUPROFEN 200 mg Tablets", 99.1),
        ("SYNTHETIC DEMO LABEL - NOT A REAL BOTTLE", 97.0),
    ],
    "acetaminophen-500mg": [
        ("ACETAMINOPHEN 500 mg Tablets", 99.0),
        ("SYNTHETIC DEMO LABEL - NOT A REAL BOTTLE", 97.0),
    ],
}


class MockOCRProvider:
    """Test/demo provider. `sample_name` selects the synthetic label."""

    def __init__(self, sample_name: str = "ibuprofen-200mg"):
        self.sample_name = sample_name

    def read_text(self, image_bytes: bytes) -> OCRResult:  # noqa: ARG002
        if self.sample_name not in SYNTHETIC_SAMPLES:
            return OCRResult(lines=[], provider="mock-ocr", synthetic=True)
        lines = [
            TextLine(text=text, confidence=conf)
            for text, conf in SYNTHETIC_SAMPLES[self.sample_name]
        ]
        return OCRResult(lines=lines, provider="mock-ocr", synthetic=True)


class RekognitionOCRProvider:
    """Amazon Rekognition DetectText. Env-gated, lazy boto3 import."""

    def __init__(self, region: str | None = None):
        self.region = region or os.environ.get("AWS_REGION", "us-east-1")

    @staticmethod
    def is_configured() -> bool:
        return os.environ.get("REKOGNITION_ENABLED", "").lower() == "true"

    def read_text(self, image_bytes: bytes) -> OCRResult:
        if not self.is_configured():
            raise OCRNotConfigured(
                "Rekognition is not configured. Set REKOGNITION_ENABLED=true "
                "and provide AWS credentials with rekognition:DetectText "
                "permission only. No photo reading was attempted."
            )
        if len(image_bytes) > 5_000_000:
            raise OCRUnavailable("Image is larger than the 5 MB Rekognition limit.")
        try:
            import boto3  # lazy: the core agent runs with no AWS account
        except ImportError as exc:
            raise OCRNotConfigured("boto3 is not installed.") from exc
        try:
            client = boto3.client("rekognition", region_name=self.region)
            response = client.detect_text(Image={"Bytes": image_bytes})
        except Exception as exc:  # AWS errors surface as a result, never a guess
            raise OCRUnavailable(f"Rekognition DetectText failed: {exc}") from exc
        lines = [
            TextLine(
                text=str(d["DetectedText"]),
                confidence=float(d.get("Confidence", 0.0)),
                kind=str(d.get("Type", "LINE")),
            )
            for d in response.get("TextDetections", [])
            if d.get("Type") == "LINE" and float(d.get("Confidence", 0.0)) >= 50
        ]
        return OCRResult(lines=lines, provider="amazon-rekognition", synthetic=False)


def ocr_provider_from_env() -> OCRProvider:
    """Choose a provider from the environment, mock by default.

    The correct variable is CLEARDose_DEMO_SAMPLE; the earlier
    misspelling CLEARDOS_DEMO_SAMPLE is still honoured as a fallback
    so existing setups do not silently change provider.
    """
    if RekognitionOCRProvider.is_configured():
        return RekognitionOCRProvider()
    sample = os.environ.get(
        "CLEARDose_DEMO_SAMPLE",
        os.environ.get("CLEARDOS_DEMO_SAMPLE", "ibuprofen-200mg"),
    )
    return MockOCRProvider(sample_name=sample)
