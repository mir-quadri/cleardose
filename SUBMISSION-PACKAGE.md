# Submission package — Strands Workshop to Ship (ClearDose) — STAGED, NOT SUBMITTED

Status as of 2026-10-30 (implementer run): everything below is
staged for Mir's review. Nothing has been submitted, published,
pushed, or recorded. Items marked "needs Mir approval" or
"blocked" cannot be closed by this agent.

## Requirement → artifact → status

| Builder Center requirement | Staged artifact | Status |
|---|---|---|
| Complete the free Strands SDK workshop on Builder Center during Oct 28–Nov 4, 2026 (required to qualify) | `docs/WORKSHOP-GATE.md` (steps + evidence slot) | BLOCKED — only Mir/parent-browser can close. Window is open (Oct 28–Nov 4); completion is NOT done and NOT claimed. PASS/FAIL with no exceptions: without workshop completion in the Submission Period the entry does not advance to judging. Do not submit until verified. |
| Submission deadline: November 4, 2026, 11:59pm PT = November 5, 2:59am ET (official pages, browser-read 2026-10-30; the page's PST/PDT label is inconsistent) | `docs/RULES-CHECKLIST.md`, `docs/WORKSHOP-GATE.md` | TARGET: submit Nov 4 DAYTIME ET. Safety-net check Nov 4, 8:00pm ET. Do not plan for the last hours — submit in daytime ET. |
| Eligibility (to be attested at submission, NOT agent-verified fact) | `docs/RULES-CHECKLIST.md` | 18+; builder.aws.com profile; workshop completed in period. US residence is NOT excluded. Amazon/subsidiary employees + immediate family/household excluded — no such affiliation on record (Mir is Citi). One entry per person. Attestation is Mir's at submission time. |
| An agent built with the Strands Agents SDK addressing a real-world social good challenge | `src/cleardose/agent.py:create_strands_agent`, `src/cleardose/strands_tools.py` (4 tools); health track: medication agent | READY (locally verified). Tests: 76 passed, 0 failed, re-run 2026-10-30 (fix pass). |
| A project article on Builder Center describing the agent, what it does, and the social good problem | `docs/ARTICLE-FINAL-PROPOSAL.md` (proposed final text, updated with live-verification results); earlier draft at `docs/ARTICLE-DRAFT.md` (narrowed in the B3 fix pass — the overstated "never from a model guessing" claim was replaced with find_mentions-only wording) | NEEDS MIR APPROVAL of exact wording, then publishing by Mir/parent-browser. NOT published. |
| A link to a public repository with the agent's source code | Local repo `~/workspace/strands-cleardose/` (1 commit, NO remote configured) | BLOCKED — repo creation + flip to public + link require Mir's approval and parent-browser/connector action. Do NOT create or push from this task. |
| A short, publicly available demo video, under 3 minutes, showing the agent working | `docs/DEMO-SCRIPT-FINAL.md` (~2:20 target, hard cap 3:00) + recording plan (live vs demo segments, on-screen advisory lines) | NEEDS MIR APPROVAL of script, then recording + publishing. Video NOT recorded. |
| An original agent not published before | `docs/ORIGINALITY.md` (new codebase, disclosed alias-map fact overlap, no DoseWise code/repo/video reused) | READY as built; final originality attestation at submission time is Mir's. |
| Health focus: medication agent explaining a prescription in plain language and flagging interactions | `src/cleardose/tools.py` (`explain_prescription`, `flag_interactions`); live evidence in `docs/LIVE-VERIFICATION.md` | READY (live openFDA verified 2026-10-30). |
| Eligibility: 18+, Builder Center profile, country/employee exclusions (Rules tab) | `docs/RULES-CHECKLIST.md` (About-page requirements + 2026-10-30 official-pages browser read) | RECORDED — exact deadline Nov 4, 2026, 11:59pm PT = Nov 5, 2:59am ET; eligibility to be attested by Mir at submission (see eligibility row above). Workshop completion itself remains BLOCKED on Mir's own step. |
| Judging: social impact 25% | `docs/SOCIAL-IMPACT.md` + README | READY as a design statement; NO impact numbers claimed (no pilot run). |
| Judging: technical execution 25% | Code + tests + `docs/LIVE-VERIFICATION.md` | READY (local + live openFDA verified). Live Rekognition NOT claimed — see below. |
| Judging: communication quality 25% | `docs/ARTICLE-FINAL-PROPOSAL.md`, `docs/DEMO-SCRIPT-FINAL.md` | NEEDS MIR APPROVAL (wording) + video recording. |
| Judging: originality 25% | `docs/ORIGINALITY.md`, README originality section | READY as built; "extends beyond the workshop" cannot be assessed until the workshop is taken — tied to the workshop gate. |

## Live-verification evidence (new this run)

- `docs/LIVE-VERIFICATION.md` — live openFDA explain/flag/questions
  (2026-10-30): explain found IBUPROFEN; flag ibuprofen vs warfarin
  returned 1 flag from the WARFARIN SODIUM label only; questions
  returned 5; unknown name returned an honest not-found; every
  result carried the full disclaimer and no dosing section.
- Rekognition: verified NOT configured (`REKOGNITION_ENABLED`
  unset; direct provider call raises `OCRNotConfigured`). No live
  Rekognition result is claimed. FIX PASS 2026-10-30 (S9):
  live-mode CLI photo NO LONGER falls back to the env-default
  mock — it now REFUSES with exit 2 and a clear stderr error
  when Rekognition is not configured; `--demo photo` still uses
  the explicitly-marked synthetic mock. Closing live photo needs
  a fully activated AWS account + credentials with
  `rekognition:DetectText` only + an observed successful call.
  It is NOT required for the article/video as staged (both state
  the non-claim explicitly), but it must never be upgraded to a
  claim without that observed call.

## Safety invariants (held in all staged text)

- Never declares a combination safe; never gives dosing advice;
  no dosing section anywhere; label text verbatim under
  plain-language headings; full disclaimer on every answer;
  demo data explicitly marked synthetic; no religious items,
  symbols, texts, or figures anywhere (scanned 2026-10-30: none
  found); no invented testimonials, traction, handles, reach, or
  credibility claims.

## Fix-pass disclosures — 2026-10-30 (honest, not hidden)

Fixed in this pass: B1 (safety filter broadened, 8 bypass probes
blocked, safe sentences still pass), B2 (incomplete-check lead in
both summary branches, no-mention scoped to labels retrieved),
B3 minimum fix (every "model can never invent a flag" instance
narrowed to "flags in tool results come only from find_mentions
over label text; model narration is not independently grounded"),
B4 (disclaimer stripped then appended exactly once at the end),
S9 (live-mode CLI photo refuses without Rekognition, exit 2),
S2 (punctuated/parenthetical names normalise; "Advil PM" still
NOT mapped to ibuprofen), S6 (class-mention caveat in both
summary branches), CLI photo missing-file (clean stderr error,
exit 2, no traceback). Full suite after the pass: 76 passed,
0 failed; compile clean; live openFDA re-run shows no regression
(see `docs/LIVE-VERIFICATION.md` addendum).

DEFERRED — B3 stronger fix: verbatim tool-output quotes for flags
in model narration, or post-checking narration against
flag_groups, was NOT attempted. Reason: the minimum narrowing
fix is the requirement, and the stronger change risks SafetyHook
regression near the deadline. The narrowed wording above is the
staged claim; do not upgrade it without the stronger fix plus
tests proving zero SafetyHook regression.

UNDEFINED — S1, S3, S4, S5, S7, S8, S10: these should-fix items
have NO definition in any workspace file. A parallel research
agent searched `~/workspace/strands-cleardose/` (all docs, src,
tests, demo), `~/workspace/hackathons/`,
`~/workspace/hackathon-pipeline/`, and
`~/workspace/goals/three-hackathon-sprint/` with word-boundary
greps for S1–S10 and "should-fix" and found zero matches — even
the already-defined S2/S6/S9 are not defined in those files.
Per the fix-pass brief, NO definitions were invented for
S1/S3/S4/S5/S7/S8/S10, and none of them is fixed or claimed
fixed here. Each is recorded UNDEFINED in this section. If a
definition is later verified with a source file, it can be
triaged then; until then, treat all seven as open unknowns, not
as passed checks.

Rules alignment (2026-10-30, official Strands pages read in a
browser — supersedes earlier assumptions): exact deadline
Nov 4, 2026, 11:59pm PT = Nov 5, 2:59am ET, target submission
Nov 4 DAYTIME ET, safety-net check Nov 4, 8:00pm ET; workshop
completion is pass/fail with no exceptions; eligibility as
recorded in the table above (to be attested at submission, not
agent-verified); submission requirements verified against the
repo in `docs/RULES-CHECKLIST.md` (MIT LICENSE at top level is
OSI-approved; demo-video target ~2:20 is under 3 minutes;
rubric 25% each; Gate 1 AI + human review, top 50 advance;
Gate 2 AWS expert panel picks 3 winners; prizes 3 × $5,000 AWS
credits + ~$600 swag + certificate). Full detail in
`docs/RULES-CHECKLIST.md`.

## Order of operations for Mir / parent

1. Mir approves (or amends) the exact article text in
   `docs/ARTICLE-FINAL-PROPOSAL.md` and the exact video script in
   `docs/DEMO-SCRIPT-FINAL.md`.
2. Mir completes the workshop (Oct 28–Nov 4 window) and records
   evidence in `docs/WORKSHOP-GATE.md`.
3. Parent-browser re-checks the Rules tab (eligibility, exact due
   time, any extra rules) and updates `docs/RULES-CHECKLIST.md`.
4. Parent creates the public repo (Mir's approval) and pastes the
   link into the article; records + publishes the video per
   `docs/DEMO-SCRIPT-FINAL.md` and pastes the link.
5. Only then submit the Builder Center project with the approved
   wording. Nothing in steps 1–5 is done by this implementer task.
