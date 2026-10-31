# ClearDose

**What it is, in plain language:** ClearDose is an AI agent that explains
a prescription. You tell it a medicine name, or show
it a photo of a bottle label, and it explains what the medicine is for,
shows the warnings from its FDA label in the label's own words, flags
when that label mentions another medicine you already take, and writes
questions you can take to your pharmacist. Precision on the
plain-language claim: ClearDose presents the label's own words under
plain-language headings — it does **not** rewrite or simplify the
label text itself (no simplification layer yet). Every answer ends with
the full advisory disclaimer in `src/cleardose/safety.py`.

**Who it helps:** Older adults, and people with low health literacy, in
underserved communities — people who are most likely to be harmed by a
prescription they do not fully understand, and least likely to have a
pharmacist on call to explain it. The agent is built for the moment
before a new medicine is taken, when a five-minute check can prevent a bad combination from ever starting.

**What problem it solves:** FDA labels are written for clinicians, not
patients. They are long, use medical words, and bury interaction
warnings in different sections — and the warnings are asymmetric: one
drug's label may warn about the other while the other drug's label is
terse. A person who cannot read or spell a generic drug name reliably
cannot use a text-only checker at all. ClearDose reads the label, reads
the bottle photo, checks both labels, and shows the result under
plain-language headings, in the label's own words.

**How it works:** ClearDose is built with the **Strands Agents SDK**
(Python, `strands-agents==1.62.0`). A Strands `Agent` (`src/cleardose/agent.py`,
`create_strands_agent`) carries four tools (`src/cleardose/strands_tools.py`):

| Tool | What it does |
|---|---|
| `explain_prescription` | Fetches the medicine's FDA label from openFDA and returns its sections under plain-language headings, with verbatim excerpts (label text is not rewritten). |
| `flag_interactions` | Checks the candidate's label for each medicine already taken, **and** each of those medicines' labels for the candidate. |
| `check_label_photo` | Reads a bottle-label photo through a pluggable OCR provider, matches one medicine name, then runs `flag_interactions`. |
| `generate_pharmacist_questions` | Builds questions for a pharmacist from the flag check. |

The deterministic logic lives in `src/cleardose/tools.py`, so it is
testable without a model: flags in tool results come only from
`find_mentions` over label text (`src/cleardose/labels.py`); model
narration is not independently grounded. A model-free `DeterministicAgent`
(`src/cleardose/agent.py`) routes requests to the same tools and is
what the tests and the offline demo use. Model-generated text, when a
model is used, is filtered by a Strands `MessageAddedEvent` hook
(`SafetyHook` in `src/cleardose/agent.py`, running
`src/cleardose/safety.py:check_output_safety`) before the result is
returned: any text that calls a combination safe or gives dosing
advice is replaced wholesale with a withheld-answer message, and live
streaming output is suppressed so unfiltered text is never printed
mid-stream.

**Data sources:** (1) FDA drug labels, live from openFDA
(`https://api.fda.gov/drug/label.json`, no API key) via
`OpenFDALabelClient`. Every result states its data source. (2) Photo
text, via a pluggable OCR provider (`src/cleardose/ocr.py`): a mock
provider for tests/demo, and Amazon Rekognition DetectText, env-gated
(`REKOGNITION_ENABLED=true`, DetectText permission only). Photo bytes
are never stored or logged.

**What it does NOT do:** ClearDose is not a reminder app, not an
adherence tracker, and not a diagnosis tool. It never declares a
combination safe. It never gives dosing advice — it shows **no**
dosing section at all, and tells you to follow your prescription, not
this tool. It has **no bundled fallback label text**: if the live
openFDA lookup fails, it says the label could not be retrieved and
does not flag or clear anything from stale prose. Demo scenarios use
explicitly marked demo data (`src/cleardose/demo_data.py`), never
disguised as a live label.

**Safety limits (read first):** FDA label text is not a complete
interaction database. Labels omit interactions, use class names, and
vary by manufacturer. Finding no mention is **not** a guarantee of
safety, and ClearDose says exactly that every time. A flag is not
proof of harm — it means the label itself raises the combination, so
discuss it with a pharmacist or doctor before taking the medicine.
This is a hackathon demo, not medical advice and not a medical device.

## Before / After

- **Before:** a text-only checker required typing a drug name
  correctly, then reading a clinician-written label alone.
- **After:** photograph the bottle, or type the name, and ClearDose
  shows the label under plain-language headings, checks both labels for
  interactions, and hands you questions for your pharmacist — in
  one conversation, with the label's own words and sections shown.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
.venv/bin/cleardose --demo explain ibuprofen
.venv/bin/cleardose --demo flag ibuprofen warfarin
.venv/bin/cleardose --demo photo demo/sample-label-ibuprofen-200mg.png warfarin
.venv/bin/python demo/run_demo.py        # three offline scenarios, demo data only
.venv/bin/python demo/server.py          # web demo at http://127.0.0.1:8765/
```

Live mode (no `--demo`) uses openFDA. With a model configured, the
Strands agent is built by `create_strands_agent(model=...)`; without
one, the deterministic agent runs the same tools with no model call.

Photo reading via Rekognition requires a fully activated AWS account
and `REKOGNITION_ENABLED=true` plus credentials with
`rekognition:DetectText` only (see `.env.example`). Until credentials
**and** activation are verified, the provider raises
`OCRNotConfigured` and no photo reading is attempted. **No live
Rekognition result is claimed in this repository.**

## Verify it

```bash
.venv/bin/python -m pytest -q   # 76 tests: safety, names, labels, OCR, tools, agent, CLI
```

Test counts are the counts actually run in this workspace on
2026-10-26 (36 passed, after the independent-review fix pass),
re-run 2026-10-30 (36 passed, 0 failed), and after the 2026-10-30
fix pass (76 passed, 0 failed — B1–B4, S9, S2, S6, CLI fixes plus
their tests, including B1/B2/S2 round-2 fixes). Live openFDA verification
from 2026-10-30 is recorded in `docs/LIVE-VERIFICATION.md`; live
Rekognition remains unverified (verified NOT configured). The Strands-agent construction test uses a
stub model so it runs with no credentials and no network, and a
stub-model invocation test proves the SafetyHook replaces unsafe
model text in both the result and the stored history.

## Originality

ClearDose is a new agent written from scratch for the Strands
Workshop to Ship hackathon, in a new codebase, under a new name, with
new Strands tools. It shares a *concept* with an earlier, separately
submitted project (checking FDA labels for interactions), but no code,
repository, article, or video from that project was reused or
submitted here. One disclosed overlap: the alias map in
`src/cleardose/names.py` covers the same public brand/generic facts
as the earlier project's map (same 10 canonical names), recreated in
Python, except the multi-word alias "bayer aspirin" was dropped.
See `docs/ORIGINALITY.md`.

## Remaining gates (not done — see docs/WORKSHOP-GATE.md)

- Strands workshop completion, Oct 28–Nov 4, 2026 — required to
  qualify; cannot be completed before Oct 28.
- Public repository link, public demo video under 3 minutes, and
  Builder Center article — drafts in `docs/`; nothing published yet.
- Mir's approval of the exact article and video wording before
  anything is submitted or published.

## License

MIT — see `LICENSE`.
