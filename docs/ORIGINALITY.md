# Originality statement — ClearDose vs. DoseWise

ClearDose is an original agent that has not been published before.
No DoseWise code, repository, article, or video was reused or
submitted for this hackathon.

How ClearDose differs:

| Aspect | DoseWise (earlier, separate submission, Oct 22) | ClearDose (this project) |
|---|---|---|
| Framework | TypeScript MCP server (MCP SDK, Streamable HTTP) | Python Strands Agents SDK (`strands-agents==1.62.0`), Strands `Agent` + `@tool` tools |
| Audience framing | Medication preflight + visit brief for Alexa+ | Plain-language prescription explainer for older adults / low health literacy, Health track social-good framing |
| Label data | Live openFDA with bundled real-label excerpts as offline fallback | Live openFDA only; **no bundled fallback** — a failed lookup says so and flags nothing |
| Photo reading | MCP tool calling Rekognition, added later as an extension | Pluggable OCR interface from the start (mock + env-gated Rekognition), photo tool bound at agent construction |
| Safety layer | Post-filter on one optional Bedrock explanation | Deterministic tools + safety filter on all model text + disclaimer on every tool result (tool-result flags come only from `find_mentions` over label text; model narration is filtered but not independently grounded) |
| Demo data | Bundled FDA excerpts | Explicitly-marked demo records in `demo_data.py`, never presented as FDA labels |

Honest overlap (concept only, not code): both projects use the same
public idea — an FDA label mentions another medicine, so checking both
labels and quoting the label is useful — and both use the same public
sources (openFDA, FDA label sections) and the same unavoidable facts
(brand/generic names such as Advil/ibuprofen, Coumadin/warfarin).
The name-normalisation code, tool functions, agent, tests, article,
and demo script in this repository were written for ClearDose.
No file was copied from `~/workspace/dosewise` or
`~/workspace/dosewise-photo-label`, and neither directory was written
to during this build.

Alias-map overlap, disclosed (fix pass, 2026-10-26): the alias map in
`src/cleardose/names.py` was recreated in Python for ClearDose, but
it covers the same public brand/generic facts as DoseWise's map —
the same 10 canonical names (warfarin, ibuprofen, acetaminophen,
atorvastatin, metformin, lisinopril, aspirin, omeprazole, sertraline,
amoxicillin) with the same aliases, except the multi-word alias
"bayer aspirin" was dropped (only "ecotrin" is kept for aspirin).
Those pairings are public facts (a brand name belongs to a generic),
not code, and the map's code, normalisation rules, and surrounding
logic are ClearDose's own. The earlier wording "written fresh" is
therefore qualified by this paragraph, not left unqualified: the
facts overlap, the code does not.
