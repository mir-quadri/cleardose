# FINAL demo-video script (proposal) — SCRIPT ONLY. Video NOT recorded, NOT published. Awaiting Mir's approval of exact wording.

Target: ~2:20 spoken. Hard cap: 3:00. At a natural speaking pace
this script is about 350 words; do not ad-lib beyond the cap.
No music, no stock footage, no third-party logos, no copyrighted
material.

On-screen line throughout the whole video, bottom of frame:
"Advisory only — not medical advice."

## 0:00–0:20 — The problem (presenter, direct to camera)

"My neighbour is 78. Her doctor changed a prescription, and the
leaflet that came with it was written for a clinician, not for her.
She could not spell the generic name, so a text checker was no help
at all. This is ClearDose: a prescription, explained in plain
language."

## 0:20–0:45 — Before (screen: clinician label, typed checker)

"Before: type the name exactly right, then read this label alone.
Long words, warnings in three different sections, and the other
drug's label says something different. That is the gap ClearDose
closes."

## 0:45–1:15 — After, live: explain (screen: CLI, LIVE banner)

"After — and this is live, not a mockup. ClearDose asks openFDA
for ibuprofen's label and shows it under plain-language headings,
in the label's own words, with the section each excerpt came from.
No dosing section, ever. Every answer ends with the advisory
disclaimer."

## 1:15–1:50 — After, live: flag + questions (screen: CLI, LIVE banner)

"Now the check, live: ibuprofen against warfarin, both labels.
There is the flag, in the label's own words — the warfarin label
mentions ibuprofen. The ibuprofen label did not mention warfarin
by name. That asymmetry is why ClearDose checks both directions.
And it hands her questions to take to her pharmacist — including
the flag, in plain words. ClearDose never says a combination is
safe."

## 1:50–2:10 — Photo, demo data only (screen: web/CLI demo, DEMO DATA banner)

"The photo path, shown with demo data: this is a synthetic demo
label, not a real bottle. ClearDose reads it, matches ibuprofen,
and runs the same check. If no medicine is matched, it does not
guess. Live photo reading is not shown here — it is not yet
verified, and this video does not claim it."

## 2:10–2:20 — Close (presenter)

"ClearDose: built with the Strands Agents SDK, for the moment
before a new medicine is taken. Advisory only — ask your
pharmacist first. Thank you."

## Recording plan

What to show, in order (match the banners exactly — never present
demo data as a live label, and never present the mock photo read
as a live OCR service):

1. Presenter segments (0:00–0:20, 2:10–2:20): direct to camera,
   plain background. No religious items, symbols, texts, or figures
   anywhere in frame.
2. Before segment (0:20–0:45): screen capture of a clinician label
   page and a typed checker. On-screen caption: "Before: text-only
   checker". No third-party logos in frame if avoidable; if a site
   header is visible, crop it out.
3. Live segments (0:45–1:50): terminal running the installed CLI
   with NO `--demo` flag, network on. Run, in order:
   `.venv/bin/cleardose explain ibuprofen`, then
   `.venv/bin/cleardose flag ibuprofen warfarin`, then
   `.venv/bin/cleardose questions ibuprofen warfarin`. On-screen
   banner for the whole live block: "LIVE — openFDA, no API key".
   Expected live results (verified 2026-10-30, re-check at record
   time; if openFDA returns a different label revision, narrate
   what is actually on screen, do not read this script's flag
   wording over different output): explain returns IBUPROFEN with
   indications + warnings excerpts; flag returns 1 flag from the
   WARFARIN SODIUM label's drug-interactions section; questions
   returns 5 questions. If the live run fails on the day, say so
   on camera and fall back to the demo run with the DEMO DATA
   banner — never fake a live result.
4. Photo segment (1:50–2:10): run with `--demo` (DEMO DATA banner
   visible) or the web demo with its "synthetic simulation" label
   visible: photo of the synthetic sample label, matched ibuprofen
   200 mg, flag check shown. Narration must say "synthetic demo
   label, not a real bottle" (it does, above). Do NOT say the word
   Rekognition as a working feature; the script's line is "live
   photo reading is not shown here — it is not yet verified."
5. Advisory lines on screen: the standing "Advisory only — not
   medical advice" line throughout; "LIVE — openFDA, no API key"
   on the live block; "DEMO DATA — synthetic sample, not a real
   bottle" on the photo block; closing frame repeats "Advisory
   only — ask your pharmacist first."
6. Audio: voice only, no music bed. Captions: burn in or upload
   accurate captions with the final video.
7. Length check before publishing: time the final cut; if it
   exceeds 3:00, cut from the Before segment first, never from the
   disclaimer or the demo-data labelling.
8. Publishing: only after Mir approves this exact script AND the
   finished cut. The published video must be public and under
   3 minutes; the link goes into the Builder Center article only
   after Mir approves it.

Differences from `docs/DEMO-SCRIPT.md`: the live and demo segments
are now split explicitly (live openFDA explain/flag/questions, then
a separately bannered demo-data photo segment); the live flag is
described truthfully as one flag from the warfarin label, not as
flags from both directions; the Rekognition non-claim is spoken
on camera instead of left to recording notes.
