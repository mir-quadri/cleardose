"""ClearDose command-line demo. `python -m cleardose.cli --help`."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import DeterministicAgent
from .demo_data import demo_label
from .labels import LabelLookup
from .ocr import MockOCRProvider, RekognitionOCRProvider


def _demo_fetch(medicine: str) -> LabelLookup:
    record = demo_label(medicine)
    if record is None:
        return LabelLookup(found=False, reason="No demo record for this medicine.")
    return LabelLookup(found=True, record=record)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cleardose",
        description="ClearDose — plain-language prescription explanations. Advisory only.",
    )
    parser.add_argument("--demo", action="store_true",
                        help="Use explicitly-marked DEMO DATA instead of live openFDA.")
    sub = parser.add_subparsers(dest="command", required=True)

    explain = sub.add_parser("explain", help="Explain one medicine in plain language.")
    explain.add_argument("medicine")

    flag = sub.add_parser("flag", help="Check one medicine against medicines already taken.")
    flag.add_argument("candidate")
    flag.add_argument("current", nargs="+", help="Medicines already taken.")

    photo = sub.add_parser("photo", help="Read a bottle-label photo and check it.")
    photo.add_argument("image", help="Path to a photo/sample file (bytes are read, not stored).")
    photo.add_argument("current", nargs="*", help="Medicines already taken.")
    photo.add_argument("--sample", default="ibuprofen-200mg",
                       help="Synthetic sample name for the mock OCR provider.")

    questions = sub.add_parser("questions", help="Questions to ask a pharmacist.")
    questions.add_argument("medicine")
    questions.add_argument("current", nargs="*", help="Medicines already taken.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.demo:
        print("DEMO MODE — results use DEMO DATA, not FDA labels.", file=sys.stderr)
        ocr = (
            MockOCRProvider(sample_name=args.sample)
            if args.command == "photo"
            else MockOCRProvider()
        )
        agent = DeterministicAgent(fetch=_demo_fetch, ocr=ocr)
    else:
        # S9 fix pass (2026-10-30): live-mode photo REFUSES when
        # Rekognition is not configured — it never silently falls
        # back to the synthetic mock. S9 scope: this refusal is CLI-scoped only — direct DeterministicAgent.photo() calls still default to ocr_provider_from_env() (env mock when unconfigured).
        # --demo photo still uses the
        # mock explicitly (branch above). Other live commands
        # (explain/flag/questions) do not use OCR and are unaffected.
        if args.command == "photo" and not RekognitionOCRProvider.is_configured():
            print(
                "ERROR: live-mode photo reading requires Rekognition: "
                "set REKOGNITION_ENABLED=true with AWS credentials "
                "holding rekognition:DetectText permission only. "
                "No photo was read and no synthetic mock was used. "
                "Use --demo for the explicitly-marked synthetic sample.",
                file=sys.stderr,
            )
            return 2
        agent = DeterministicAgent()
    if args.command == "explain":
        result = agent.explain(args.medicine)
    elif args.command == "flag":
        result = agent.flag(args.candidate, args.current)
    elif args.command == "photo":
        try:
            image_bytes = Path(args.image).read_bytes()
        except OSError as exc:
            print(
                f"ERROR: could not read photo file {args.image!r}: {exc}",
                file=sys.stderr,
            )
            return 2
        result = agent.photo(image_bytes, args.current)
    elif args.command == "questions":
        result = agent.questions(args.medicine, args.current)
    else:  # pragma: no cover
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
