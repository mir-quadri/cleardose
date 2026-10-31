# PROPOSAL — Builder Center article, final proposed text — NOT PUBLISHED. Awaiting Mir's approval of exact wording.

This file is the proposed final article text for the Strands
Workshop to Ship submission. It is a staging file only: nothing
here has been published, no repository link or video link has been
added yet (both are placeholders below), and workshop completion
is NOT claimed. Do not publish this text until Mir approves this
exact wording and the open gates in `SUBMISSION-PACKAGE.md` are
closed.

---

# ClearDose: a prescription, explained in plain language

## The problem

A new prescription arrives, and the leaflet that comes with it is
written for a clinician, not for the person who has to take it. The
warnings are long, the words are medical, and the interaction
warnings do not sit in one place: one drug's label may warn about
the other while the other drug's label says little. For an older
adult, or someone with low health literacy, that leaflet can be
unreadable — and a text-only checker that demands a correctly
spelled generic name does not help at all.

## What ClearDose does

ClearDose is an agent built with the Strands Agents SDK. Tell it a
medicine name, or show it a photo of a bottle label, and it:

1. Shows the prescription under plain-language headings, from its
   FDA label, with the label's own words and section names shown.
   The label text itself is not rewritten or simplified — no
   simplification layer yet; only the headings are plain-language
   help.
2. Checks the new medicine's label for every medicine you already
   take — and checks each of those medicines' labels for the new
   one, because warnings are asymmetric.
3. Writes questions you can take to your pharmacist.

Every answer ends with the same line: advisory only, not medical
advice. ClearDose never calls a combination safe, and never tells
anyone how much to take. It shows no dosing section at all.

## How it is built

ClearDose is a Python Strands agent. Four tools do the work:
`explain_prescription`, `flag_interactions`, `check_label_photo`,
and `generate_pharmacist_questions`. The tools are deterministic —
flags in tool results come only from `find_mentions` over label
text; model narration is not independently grounded —
and model-generated text is filtered by a Strands hook (see README)
so safety claims and dosing advice are replaced before they reach a
user.

Labels come live from openFDA, and every result states its data
source. If a label cannot be retrieved, ClearDose says so and flags
nothing from stale text: there is no bundled fallback label in this
agent. Photo text comes through a pluggable OCR interface. The demo
uses a clearly marked synthetic sample. Amazon Rekognition
DetectText is available behind an environment flag, but it is NOT
verified live: at the time of writing, Rekognition is not
configured in this workspace, and no live Rekognition result is
claimed. Photo bytes are never stored or logged.

## Verified live, 2026-10-30

The following was observed by running the CLI in live mode
(no demo flag) against openFDA, with no API key; full evidence is
in `docs/LIVE-VERIFICATION.md`:

- `explain ibuprofen` returned a live openFDA label (IBUPROFEN,
  brand "Ibuprofen Dye Free") under plain-language headings, with
  verbatim excerpts and the full disclaimer, and no dosing section.
- `flag ibuprofen warfarin` checked both directions and returned
  1 flag: the WARFARIN SODIUM label's drug-interactions section
  mentions ibuprofen. The ibuprofen label in that run did not
  mention warfarin by name — the asymmetry the both-directions
  check exists for.
- `questions ibuprofen warfarin` returned 5 pharmacist questions,
  including one naming the warfarin-label flag.
- An unknown medicine name returned an honest not-found result
  with no invented label text.
- Tests: 76 passed, 0 failed, re-run 2026-10-30 (fix pass).

No pilot, user study, or outcome measurement has been run, and no
impact numbers are claimed. No reading-level reduction is claimed,
because the label text itself is not rewritten.

Intended measurable improvement (design goal, NOT a measured
result): the design aims to measurably reduce the steps and time
from receiving a prescription to understanding its warnings and
interaction flags, and to increase the share of users who arrive
at the pharmacist with the right questions. That improvement has
not been measured yet — no pilot has run — and this article
claims no measured outcome, only the design goal above.

## Who it helps, and what it does not do

ClearDose is for older adults and low-health-literacy users in
underserved communities, at the moment before a new medicine is
taken. It is not a reminder app, not a diagnosis tool, and not a
replacement for a pharmacist or doctor. Finding no mention in a
label is not a guarantee of safety, and a flag is not proof of
harm — it is the label raising a combination, to be discussed
before the first dose.

## What I learned

Building with Strands taught me to keep the agent's judgment in
deterministic tools and let the model present, not decide. The
safety filter, the both-directions check, and the "no bundled
label" rule are the parts of this agent I would keep in any health
agent I build next.

## Try it

Public repository: https://github.com/mir-quadri/cleardose
[Demo video link — TO BE ADDED after the video is recorded and
published and Mir approves]

Workshop completion: NOT CLAIMED HERE. Completion during the
Oct 28–Nov 4, 2026 window is still an open gate (see
`docs/WORKSHOP-GATE.md` and `SUBMISSION-PACKAGE.md`); do not
publish this article claiming workshop completion until it is
verified by Mir.

---

End of proposed text. Changes from `docs/ARTICLE-DRAFT.md`: added
the "Verified live, 2026-10-30" section with observed results
only; made the Rekognition status explicit (not configured, no
live result claimed); added the no-dosing-section and no-impact-
numbers sentences already true of the project. No testimonials,
traction, handles, reach, or credibility claims were added, because
none exist to report.
