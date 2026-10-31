# Rules checklist — Strands SDK: Workshop to Ship

Source: challenge About page, re-read live from Builder Center on
2026-10-26 (page: "Strands SDK: Workshop to Ship | Hackathon | AWS
Builder Center"), plus the official Strands pages as read in a
browser on 2026-10-30 (parent's browser read, reported to this
fix pass — the deadline, eligibility, gates, and prizes below
come from that read and supersede earlier assumptions). Eligibility
items are recorded here as to-be-attested at submission, not as
agent-verified fact.

## Requirements (About page, "How to qualify" and "Your project submission must include")

| Requirement (verbatim from About page) | Status | Evidence |
|---|---|---|
| "Complete the free Strands SDK workshop on Builder Center during the hackathon window (October 28 to November 4). Workshop completion is required to qualify." | NOT IMPLEMENTED — OPEN GATE, PASS/FAIL WITH NO EXCEPTIONS | `docs/WORKSHOP-GATE.md`. Window is open (Oct 28–Nov 4); completion is NOT done and NOT claimed. Without workshop completion within the Submission Period the entry does not advance to judging. Parent/Mir must complete it and record evidence — urgently, well before the Nov 4 daytime-ET submission target. |
| "An agent built with the Strands Agents SDK that addresses a real-world social good challenge." | IMPLEMENTED | `src/cleardose/agent.py:create_strands_agent` (Strands `Agent`, 4 `@tool` tools in `src/cleardose/strands_tools.py`); Health track: medication agent. Test: `tests/test_agent.py::test_strands_agent_constructs_without_invoking_model` (stub model, all 4 tools registered). |
| "A project article on Builder Center describing the agent, what it does, and the social good problem it addresses." | PARTIALLY IMPLEMENTED — draft only, NOT published | `docs/ARTICLE-DRAFT.md` (marked DRAFT, NOT PUBLISHED). Requires Mir's approval of exact wording + workshop completion before publishing. |
| "A link to a public repository with the agent's source code." | NOT IMPLEMENTED — OPEN GATE | No repo created. Code is local only at `~/workspace/strands-cleardose/`. Requires Mir's approval + repo creation by the parent. License check (2026-10-30): top-level `LICENSE` is MIT — an OSI-approved license, so the public repo will satisfy the approved-OSI-license requirement once flipped public. |
| "A short, publicly available demo video, under three minutes, showing the agent working." | PARTIALLY IMPLEMENTED — script only, NOT recorded/published | `docs/DEMO-SCRIPT-FINAL.md` (script only, ~2:20 target — UNDER 3 minutes, compliant; `docs/DEMO-SCRIPT.md` is SUPERSEDED, do not record from it). No video recorded. Requires live/demo recording + Mir's approval. Published video must be publicly visible on YouTube/Vimeo/Facebook Video/Youku, with no third-party trademarks or copyrighted music/material without permission — the staged script uses no music, no stock footage, no third-party logos, and no copyrighted material. |
| "An original agent that has not been published before." | IMPLEMENTED (as built; submission-time claim is OPEN) | New codebase, new name, fresh files in `~/workspace/strands-cleardose/`; see `docs/ORIGINALITY.md`. No DoseWise code/repo/video reused or submitted. Final originality attestation is Mir's at submission time. |
| Health focus: "a medication agent that explains a prescription in plain language and flags drug interactions." (About, focus areas) | IMPLEMENTED | `src/cleardose/tools.py:explain_prescription`, `flag_interactions`; tests in `tests/test_tools.py`. |
| "Open to builders 18 or older with a Builder Center profile. See Rules for country and employee exclusions." (About, "Who can enter") | RECORDED FROM 2026-10-30 OFFICIAL-PAGES BROWSER READ — TO BE ATTESTED AT SUBMISSION, NOT AGENT-VERIFIED | Eligibility: 18+; builder.aws.com profile; workshop completed in period. US residence is NOT excluded. Amazon/subsidiary employees + immediate family/household excluded — no such affiliation on record (Mir is Citi). One entry per person. Attestation is Mir's at submission time. |
| Timeline: "Launch: October 28", "Projects due by: November 4", "Gate 1: Week of November 9", "Gate 2: Week of November 16", "Winners Announced: Week of November 23" (About, Timeline table) | NOTED — EXACT DEADLINE NOW RECORDED | Exact deadline (2026-10-30 official-pages browser read): November 4, 2026, 11:59pm PT = November 5, 2:59am ET. The page's PST/PDT label is inconsistent, so the target is submission Nov 4 DAYTIME ET. Safety-net check Nov 4, 8:00pm ET. |

## Judging criteria (About page, rubric — verbatim)

| Criterion (verbatim) | Status | Evidence |
|---|---|---|
| "Social impact (25%): how clearly the project delivers measurable improvement for underserved populations, and the depth of potential benefit for people or the planet." | PARTIALLY IMPLEMENTED | `docs/SOCIAL-IMPACT.md` + README social-impact section state the underserved population and the design improvement (fewer steps, both-label checking). NO impact numbers are claimed — no pilot has run; measurement plan is stated, not executed. NO reading-level reduction is claimed (label text is not rewritten). |
| "Technical execution (25%): how well the agent is built with the Strands Agents SDK and how well it works." | IMPLEMENTED (locally verified) | Strands agent + deterministic tools; 76 passed, 0 failed after the 2026-10-30 fix pass (36 baseline + B1–B4, S9, S2, S6, CLI tests, plus 14 B1 round-2 tests, plus 4 B2/S2 round-2 tests), compile check passed, CLI demo verified with demo data (see Verification below). Live openFDA verified end-to-end 2026-10-30 (see `docs/LIVE-VERIFICATION.md`); live Rekognition still unverified (see open gates). |
| "Communication quality (25%): how clearly the project article and video explain the agent, the problem, and what you learned, in a way that makes the reader or viewer want to try it." | PARTIALLY IMPLEMENTED — drafts only | `docs/ARTICLE-FINAL-PROPOSAL.md` (proposed final text, NOT published), `docs/DEMO-SCRIPT-FINAL.md` (script only, NOT recorded), README concept explanation. Neither published; both need Mir's approval. Article framing note (2026-10-30): the staged article states its intended measurable improvement as a design goal only — no pilot, no measured results, no reading-level reduction claimed — which is a scoring consideration under the 25% Social impact rubric, kept honest deliberately. |
| "Originality (25%): the originality of the agent architecture, novel use of AWS services, and how far the project extends beyond the lessons in the workshop." | PARTIALLY IMPLEMENTED | Architecture (deterministic safety layer, Strands safety hook, pluggable OCR, no bundled fallback, no dosing section) is documented in README + `docs/ORIGINALITY.md`, including the disclosed alias-map fact overlap. "Extends beyond the workshop" cannot be assessed until the workshop is taken (Oct 28–Nov 4) — OPEN. Novel AWS use: Rekognition is env-gated and UNVERIFIED live — do not claim it until a live call is recorded. |

## Verification actually run (2026-10-26, this workspace, plus 2026-10-30 live run)

- `pytest -q`: 76 passed, 0 failed (2026-10-30 fix pass: 36 baseline from the independent-review fix pass — safety hook invocation, normalisation, failed-lookup no-cache, dosage absence, multi-candidate photo, env-var spelling — plus 22 new/updated fix-pass tests for B1–B4, S9, S2, S6, and CLI photo handling, plus 14 B1 round-2 tests, plus 4 B2/S2 round-2 tests).
- `python -m compileall src demo`: OK. Editable install + CLI: `--demo explain/flag/photo` all returned demo-data results with the full disclaimer; photo run returned ibuprofen / 200 mg / 4 demo flags, synthetic_sample=true. Live-mode CLI photo (no Rekognition configured) returned the env mock provider, synthetic, ibuprofen in the 2026-10-26 run — mock is no longer forced in live mode, it is the env default. FIX PASS 2026-10-30: that behaviour is superseded — live-mode CLI photo now REFUSES (exit 2, clear stderr error) when Rekognition is not configured and never substitutes the mock; see `docs/LIVE-VERIFICATION.md` addendum. Web demo smoke: page carries the "synthetic simulation" label and the photo form returns ibuprofen.
- LIVE openFDA verified 2026-10-30 (see `docs/LIVE-VERIFICATION.md`): live `explain ibuprofen` found IBUPROFEN (live openFDA, 2 sections, no dosing section); live `flag ibuprofen warfarin` returned 1 flag from the WARFARIN SODIUM label only; live `questions ibuprofen warfarin` returned 5 questions; unknown name returned an honest not-found. Tests re-run 2026-10-30 (fix pass): 76 passed, 0 failed; live re-run shows no regression.
- No live Rekognition call is claimed: Rekognition verified NOT configured 2026-10-30 (`REKOGNITION_ENABLED` unset; direct provider call raises `OCRNotConfigured`).
- No submission, publication, repo creation, or video recording was performed. No credentials were used. No files were written to `~/workspace/dosewise` or `~/workspace/dosewise-photo-label` (the DoseWise alias map was read only to name the dropped alias accurately in the disclosure).

## Submission requirements — verified against the repo (2026-10-30 official-pages read)

Each requirement below was checked against this repository during
the fix pass; staged items are NOT claimed as submitted or
published.

- Builder Center project article: staged only, NOT published —
  `docs/ARTICLE-FINAL-PROPOSAL.md` (proposed final text, needs
  Mir's approval of exact wording).
- Public repo under an approved OSI license: NOT yet created
  (local only, no remote). License verified: top-level `LICENSE`
  is MIT (OSI-approved), so the requirement will be satisfied
  once the repo is created and flipped public with this license.
- Demo video UNDER 3 minutes, publicly visible on YouTube/Vimeo/
  Facebook Video/Youku: NOT recorded, NOT published. Staged
  script `docs/DEMO-SCRIPT-FINAL.md` targets ~2:20 — compliant
  with the under-3-minutes limit — and specifies no music, no
  stock footage, no third-party logos, and no copyrighted
  material, satisfying the no-trademarks / no-copyrighted-material-
  without-permission condition as staged. `docs/DEMO-SCRIPT.md`
  is SUPERSEDED and must not be recorded from.
- Original, not previously published: `docs/ORIGINALITY.md`
  (new codebase; disclosed alias-map fact overlap only).
- Agent addresses a real-world social-good challenge (Health
  track) delivering measurable improvement for underserved
  populations: design statement in README + `docs/SOCIAL-IMPACT.md`
  + article. Honest framing kept: NO pilot, NO measured results,
  NO reading-level reduction claimed; the article states the
  intended measurable improvement (fewer steps/time from
  prescription to understanding warnings and flags; more users
  arriving at the pharmacist with the right questions) as a
  design goal only — a scoring consideration under Social impact,
  not a measured claim.
- Judging rubric 25% each: Social impact, Technical execution,
  Communication quality, Originality.
- Judging flow: Gate 1 AI + human review (top 50 advance);
  Gate 2 AWS expert panel picks 3 winners.
- Prizes: 3 × $5,000 AWS credits + ~$600 swag + certificate.
- Deadline: November 4, 2026, 11:59pm PT = November 5, 2:59am ET;
  target submission Nov 4 DAYTIME ET; safety-net check Nov 4,
  8:00pm ET (page PST/PDT label inconsistent).

## Open gates for the parent / Mir

1. Workshop completion Oct 28–Nov 4 (required, PASS/FAIL — no exceptions).
2. Rules-tab re-check in a browser — DONE per the 2026-10-30 official-pages browser read (exact deadline Nov 4, 2026, 11:59pm PT = Nov 5, 2:59am ET; eligibility; gates; prizes — all recorded above). Eligibility itself is still to-be-attested by Mir at submission.
3. Public repo creation + link.
4. Demo video recording + publishing (under 3 minutes).
5. Mir's approval of exact article + video wording.
6. Optional live verification: openFDA live run VERIFIED 2026-10-30 (see `docs/LIVE-VERIFICATION.md`) + Rekognition DetectText (needs activated AWS account; the previously reported account activation issue is unresolved in this task and must not be assumed fixed; Rekognition verified NOT configured 2026-10-30).
