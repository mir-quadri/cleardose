"""CLI tests: live-mode photo refusal (S9) and missing-file handling."""

import os

from cleardose.cli import main


def _clear_rekognition(monkeypatch):
    monkeypatch.delenv("REKOGNITION_ENABLED", raising=False)
    # Ensure no env var can flip the provider on for these tests.
    assert os.environ.get("REKOGNITION_ENABLED", "").lower() != "true"


def test_live_photo_refused_without_rekognition(monkeypatch, capsys, tmp_path):
    # S9 fix pass: live mode must REFUSE the photo command when
    # Rekognition is not configured — never substitute the mock.
    _clear_rekognition(monkeypatch)
    image = tmp_path / "label.png"
    image.write_bytes(b"bytes")
    code = main(["photo", str(image), "warfarin"])
    assert code != 0
    captured = capsys.readouterr()
    assert "Rekognition" in captured.err
    assert "not configured" in captured.err.lower() or "requires Rekognition" in captured.err
    # No JSON result may be printed on stdout for a refused command.
    assert "mock-ocr" not in captured.out
    assert "synthetic" not in captured.out


def test_demo_photo_missing_file_clean_error(monkeypatch, capsys):
    # Missing-file traceback fix: --demo photo on a nonexistent
    # path prints a clean stderr error and exits 2, no traceback.
    code = main(["--demo", "photo", "/nonexistent/cleardose-label.png", "warfarin"])
    assert code == 2
    err = capsys.readouterr().err
    assert "could not read photo file" in err
    assert "Traceback" not in err


def test_demo_photo_existing_file_still_works(capsys, tmp_path):
    image = tmp_path / "label.png"
    image.write_bytes(b"bytes")
    code = main(["--demo", "photo", str(image), "warfarin"])
    assert code == 0
    out = capsys.readouterr().out
    assert '"matched_medicine": "ibuprofen"' in out
