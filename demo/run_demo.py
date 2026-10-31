"""Offline demo script: three scenarios, DEMO DATA only, no model call.

Scenario 1: explain ibuprofen in plain language.
Scenario 2: photograph a synthetic ibuprofen label, check it against
    warfarin — the flag appears in the label's own words (demo text).
Scenario 3: questions to take to the pharmacist.

Run:  .venv/bin/python demo/run_demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cleardose.agent import DeterministicAgent  # noqa: E402
from cleardose.cli import _demo_fetch  # noqa: E402
from cleardose.ocr import MockOCRProvider  # noqa: E402


def main() -> None:
    print("ClearDose demo — DEMO DATA ONLY, not FDA labels. Advisory only.")
    agent = DeterministicAgent(fetch=_demo_fetch, ocr=MockOCRProvider())
    print("\n--- 1. Explain ibuprofen ---")
    print(json.dumps(agent.explain("ibuprofen"), indent=2))
    print("\n--- 2. Photo of a synthetic ibuprofen label, checked with warfarin ---")
    print(json.dumps(agent.photo(b"synthetic-demo-bytes", ["warfarin"]), indent=2))
    print("\n--- 3. Questions for the pharmacist ---")
    print(json.dumps(agent.questions("ibuprofen", ["warfarin"]), indent=2))


if __name__ == "__main__":
    main()
