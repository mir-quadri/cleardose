# Live verification — ClearDose (evidence, not claims)

Date run: **2026-10-30, approx 01:03–01:10 EDT (America/New_York)**.
Runner: existing `.venv` in `~/workspace/strands-cleardose/`.
Commands below are the CLI in **live mode** (no `--demo` flag), except
where a run is explicitly labelled demo. Every result below was
observed in this run; nothing here is carried over from an earlier
session's notes.

## 1. Live explain — openFDA, no API key

Command: `.venv/bin/cleardose explain ibuprofen`

Observed outcome: exit 0, `label_found: true`,
`matched_label: "IBUPROFEN"`, `brand_names: ["Ibuprofen Dye Free"]`,
`generic_names: ["IBUPROFEN"]`, `data_source: "live openFDA"`.
`plain_language_sections` returned 2 sections:

- "What it is used for" (`indications_and_usage`) — excerpt begins
  "Uses temporarily relieves minor aches and pains due to: headache
  toothache backache menstrual cramps the common cold muscular aches
  minor pain of arthritis temporarily reduces fever".
- "Important warnings" (`warnings`) — excerpt begins "Warnings
  Allergy alert: Ibuprofen may cause a severe allergic reaction,
  especially in people allergic to aspirin."

No dosing section was returned (there is no dosing section in
ClearDose by design). Full disclaimer present on the result.

## 2. Live flag — openFDA, both directions checked

Command: `.venv/bin/cleardose flag ibuprofen warfarin`

Observed outcome: exit 0, `flag_count: 1`,
`labels_not_found: []`, full disclaimer present.
The single flag came from **one direction only**: the
`WARFARIN SODIUM` label's `drug_interactions` section mentions
ibuprofen (excerpt lists ibuprofen among non-steroidal
anti-inflammatory agents). The ibuprofen label returned by openFDA
in this run did **not** mention "warfarin" by name in its scanned
sections (its warnings refer to a "blood thinning (anticoagulant)"
drug by class, not by the name warfarin) — so no flag came from
the ibuprofen-label direction. This is the asymmetry the
both-directions check exists for, and it is exactly what the live
run showed: 1 flag, warfarin-label direction only. Do not describe
this live run as "flags from both directions."

Summary text returned (verbatim in substance): "Checked in both
directions. 1 label mention(s) were found for ibuprofen against
warfarin. Treat each mention as a label flag to discuss with your
pharmacist or doctor before taking it — a mention is the label
raising the combination, not proof of harm, and ClearDose never
calls a combination safe."

## 3. Live pharmacist questions — openFDA

Command: `.venv/bin/cleardose questions ibuprofen warfarin`

Observed outcome: exit 0, `flag_count: 1`, 5 questions, full
disclaimer present. Question 2 is the flag question, naming the
`WARFARIN SODIUM` label's `drug_interactions` section. The other
questions are the standard list (right to take alongside current
medicines, warning signs, time of day/food, missed dose) — phrased
as questions to ask a pharmacist, not as advice.

## 4. Live not-found behaviour — honest failure, no fallback text

Command: `.venv/bin/cleardose explain notamedicinexyz`

Observed outcome: exit 0, `label_found: false`,
`reason: "No FDA label found for 'notamedicinexyz'."`,
`data_source: "none — label not retrieved"`. No label text was
invented and no flag was produced from bundled prose, consistent
with the no-bundled-fallback rule.

## 5. Photo in live mode — mock OCR, NOT Rekognition

Command: `.venv/bin/cleardose photo demo/sample-label-ibuprofen-200mg.png warfarin`
(no `--demo`, no Rekognition environment set)

Observed outcome: exit 0, `photo_read: true`,
`ocr_provider: "mock-ocr"`, `synthetic_sample: true`,
`matched_medicine: "ibuprofen"`, `dose_on_label: "200 mg"`,
`interaction_check.flag_count: 1`, full disclaimer present.
This is the environment-default mock provider, not a live OCR
service. **Never present this run as a live photo read.**

## 6. Rekognition status — verified NOT configured (no live result)

Environment at run time: `REKOGNITION_ENABLED` unset,
`AWS_REGION` unset, no AWS credentials supplied to this task
(env var names only are recorded here; no credential values).

Direct provider check in the same `.venv`:

- `RekognitionOCRProvider.is_configured()` returned `False`.
- Calling `RekognitionOCRProvider().read_text(...)` raised
  `OCRNotConfigured` ("Rekognition is not configured. Set
  REKOGNITION_ENABLED=true and provide AWS credentials with
  rekognition:DetectText permission only. No photo reading was
  attempted.")

**Verified state: OCRNotConfigured. No live Amazon Rekognition
result is claimed anywhere in this repository.** The earlier
unresolved AWS account-activation issue is still assumed
unresolved; it was not re-tested and must not be assumed fixed.
A live Rekognition claim requires, in order: a fully activated
AWS account, `REKOGNITION_ENABLED=true`, credentials with
`rekognition:DetectText` permission only, and an observed
successful DetectText call recorded here.

## 7. Test suite re-run (same session)

`.venv/bin/python -m pytest -q` → **36 passed, 0 failed**
(3.25s). `python -m compileall -q src demo` → OK. Offline demo
(`demo/run_demo.py`) still runs with explicitly marked DEMO DATA
only.

## Addendum — fix pass, 2026-10-30 (later same day)

The Oct 30 run entry above is NOT rewritten; this addendum records
what changed in the fix pass later that day.

- Test suite: `.venv/bin/python -m pytest -q` → **58 passed,
  0 failed** (36 baseline + 22 new/updated fix-pass tests: B1
  probes, B4 disclaimer-position tests, B2/S6 summary tests, S2
  normalisation tests, CLI live-photo refusal + missing-file
  tests). `python -m compileall -q src demo` → OK.
- Live openFDA re-run (same commands, no `--demo`): explain
  ibuprofen exit 0, `label_found: true`, IBUPROFEN, live openFDA,
  2 sections, no dosing section; flag ibuprofen warfarin exit 0,
  `flag_count: 1`, WARFARIN SODIUM direction only,
  `labels_not_found: []`, summary now also carries the class-mention
  caveat (class mentions not searched, only medicine names);
  questions ibuprofen warfarin exit 0, `flag_count: 1`,
  5 questions; unknown name exit 0, `label_found: false`,
  no invented label text. No regression in honest behaviour.
- Section 5 forward-looking statement UPDATED by this addendum:
  live-mode CLI photo NO LONGER falls back to the env-default
  mock. As of the fix pass, `.venv/bin/cleardose photo ...` in
  live mode without Rekognition configured REFUSES with exit 2
  and a clear stderr error ("live-mode photo reading requires
  Rekognition... No photo was read and no synthetic mock was
  used"); observed in this re-run: exit 2, that stderr text, no
  JSON output. `--demo photo` still uses the explicitly-marked
  synthetic mock. The original section 5 observation (mock used
  in that earlier run) stands as a dated record of the old
  behaviour; do not present it as current behaviour.
- S9 scope disclosure (2026-10-30, round-2 fix): the live-photo
  refusal is CLI-scoped only — direct DeterministicAgent.photo()
  calls still default to the env mock provider (mitigated:
  results carry synthetic_sample; the Strands path also defaults
  to ocr_provider_from_env()).

## What this verification does and does not establish

- Established: live openFDA explain/flag/questions work end to end
  from the CLI with no API key; not-found handling is honest;
  safety invariants hold in live output (disclaimer on every
  result, no dosing section, no combination called safe).
- NOT established: any live Rekognition result; any Strands-model
  invocation against Bedrock (no model call was made in this run);
  workshop completion; any Builder Center submission state.
