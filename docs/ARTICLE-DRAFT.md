# DRAFT Builder Center article — NOT PUBLISHED. Awaiting Mir's approval of exact wording.

# ClearDose: a prescription, explained in plain language

## The problem

A new prescription arrives, and the leaflet that comes with it is
written for a clinician, not for the person who has to take it. The
warnings are long, the words are medical, and the interaction warnings
do not sit in one place: one drug's label may warn about the other
while the other drug's label says little. For an older adult, or
someone with low health literacy, that leaflet can be unreadable —
and a text-only checker that demands a correctly spelled generic name
does not help at all.

## What ClearDose does

ClearDose is an agent built with the Strands Agents SDK. Tell it a
medicine name, or show it a photo of a bottle label, and it:

1. Shows the prescription under plain-language headings, from its FDA
   label, with the label's own words and section names shown. The
   label text itself is not rewritten or simplified — no
   simplification layer yet; only the headings are plain-language help.
2. Checks the new medicine's label for every medicine you already
   take — and checks each of those medicines' labels for the new one,
   because warnings are asymmetric.
3. Writes questions you can take to your pharmacist.

Every answer ends with the same line: advisory only, not medical
advice. ClearDose never calls a combination safe, and never tells
anyone how much to take.

## How it is built

ClearDose is a Python Strands agent. Four tools do the work:
`explain_prescription`, `flag_interactions`, `check_label_photo`,
and `generate_pharmacist_questions`. The tools are deterministic —
flags in tool results come only from `find_mentions` over label
text; model narration is not independently grounded —
and model-generated text is filtered by a Strands hook (see README)
so safety claims and dosing advice are replaced before they reach a
user. No dosing section is shown at all.

Labels come live from openFDA, and every result states its data
source. If a label cannot be retrieved, ClearDose says so and flags
nothing from stale text: there is no bundled fallback label in this
agent. Photo text comes through a pluggable OCR interface; the demo
uses a clearly marked synthetic sample, and Amazon Rekognition
DetectText is available behind an environment flag once AWS
credentials and account activation are verified. Photo bytes are
never stored or logged.

## Who it helps, and what it does not do

ClearDose is for older adults and low-health-literacy users in
underserved communities, at the moment before a new medicine is
taken. It is not a reminder app, not a diagnosis tool, and not a
replacement for a pharmacist or doctor. Finding no mention in a label
is not a guarantee of safety, and a flag is not proof of harm — it is
the label raising a combination, to be discussed before the first dose.

## What I learned

Building with Strands taught me to keep the agent's judgment in
deterministic tools and let the model present, not decide. The safety
filter, the both-directions check, and the "no bundled label" rule
are the parts of this agent I would keep in any health agent I build
next.

## Try it

[Public repository link — TO BE ADDED after the repo is created]
[Demo video link — TO BE ADDED after the video is recorded and published]

Workshop completion: OPEN GATE — required Oct 28–Nov 4, 2026; see
docs/WORKSHOP-GATE.md. Do not publish this article claiming workshop
completion until it is verified.
