"""ClearDose tools: plain functions the Strands agent calls.

Each tool returns a plain dict (JSON-friendly) that always carries
the safety disclaimer, the data source, and — for interaction
flags — verbatim label excerpts kept separate from the section
headings, so a quote is never silently paraphrased. The label text
itself is not simplified or rewritten; only the headings are
plain-language help.
"""
from __future__ import annotations

import re

from .labels import LabelLookup, LabelRecord, find_mentions
from .names import parse, same_drug
from .ocr import OCRNotConfigured, OCRResult, OCRUnavailable, OCRProvider
from .safety import DISCLAIMER, NO_MENTION_CAVEAT, with_disclaimer

_PLAIN_HEADINGS = {
    "indications_and_usage": "What it is used for",
    "warnings": "Important warnings",
    "drug_interactions": "Interactions with other medicines",
    "boxed_warning": "Boxed warning",
    # Deliberately no dosage_and_administration: ClearDose never shows
    # a dosing section, so no excerpt can be read as dosing advice.
    # Users follow their own prescription, not this tool.
}

_DOSE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*mg", re.IGNORECASE)


def _plain_summary(record: LabelRecord) -> list[dict[str, str]]:
    """Section list under plain-language headings. Quotes stay in
    `excerpt`, verbatim — the label text itself is NOT rewritten or
    simplified; only the headings are plain-language help."""
    out = []
    for key, heading in _PLAIN_HEADINGS.items():
        text = record.section_text(key)
        if text:
            out.append({"heading": heading, "section": key, "excerpt": text[:600]})
    return out


def explain_prescription(medicine: str, fetch) -> dict:
    """Explain one prescription from its FDA label, under
    plain-language headings. The excerpts are the label's own words;
    no simplification or rewriting of the label text is performed.

    `fetch` is a callable(medicine) -> LabelLookup, so tests and the
    demo can inject a stub without touching the network.
    """
    lookup: LabelLookup = fetch(medicine)
    if not lookup.found or lookup.record is None:
        return with_disclaimer(
            {
                "medicine": medicine,
                "label_found": False,
                "summary": (
                    f"No FDA label could be found for {medicine!r}. "
                    "Check the spelling, or ask your pharmacist for the "
                    "official information leaflet."
                ),
                "reason": lookup.reason,
                "data_source": "none — label not retrieved",
            }
        )
    record = lookup.record
    return with_disclaimer(
        {
            "medicine": medicine,
            "label_found": True,
            "matched_label": record.name,
            "brand_names": record.brand_names,
            "generic_names": record.generic_names,
            "data_source": record.data_source,
            "plain_language_sections": _plain_summary(record),
            "note": (
                "The excerpts above are the label's own words, shown with "
                "their section names. The headings are plain-language help; "
                "they are not part of the label. No dosing section is "
                "shown — follow your prescription, not this tool."
            ),
        }
    )


def flag_interactions(candidate: str, current_medicines: list[str], fetch) -> dict:
    """Check a candidate medicine against medicines already taken, both ways.

    Direction 1: the candidate's label, scanned for each current medicine.
    Direction 2: each current medicine's label, scanned for the candidate.
    A medicine is never checked against its own label.
    """
    candidate_name = parse(candidate)
    others = [m for m in current_medicines if not same_drug(m, candidate)]
    excluded = [m for m in current_medicines if same_drug(m, candidate)]

    flag_groups: list[dict] = []
    labels_not_found: list[str] = []
    candidate_lookup: LabelLookup = fetch(candidate)
    # B2 round-2 fix: track explicitly whether the candidate label was
    # retrieved, so the no-mention branch never claims a search of a
    # label that was never retrieved.
    candidate_retrieved = bool(
        candidate_lookup.found and candidate_lookup.record is not None
    )
    if candidate_retrieved:
        record = candidate_lookup.record
        terms = []
        for med in others:
            terms.extend(parse(med).search_terms)
        mentions = find_mentions(record, sorted(set(terms)))
        if mentions:
            flag_groups.append(
                {
                    "source_label": record.name,
                    "data_source": record.data_source,
                    "flags": [
                        {
                            "mentioned_medicine": m.medicine,
                            "section": m.section,
                            "excerpt": m.excerpt,
                        }
                        for m in mentions
                    ],
                }
            )
    else:
        labels_not_found.append(candidate)

    for med in others:
        lookup: LabelLookup = fetch(med)
        if not lookup.found or lookup.record is None:
            labels_not_found.append(med)
            continue
        record = lookup.record
        mentions = find_mentions(record, candidate_name.search_terms)
        if mentions:
            flag_groups.append(
                {
                    "source_label": record.name,
                    "data_source": record.data_source,
                    "flags": [
                        {
                            "mentioned_medicine": m.medicine,
                            "section": m.section,
                            "excerpt": m.excerpt,
                        }
                        for m in mentions
                    ],
                }
            )

    total_flags = sum(len(g["flags"]) for g in flag_groups)
    # B2 fix pass: a missing label must never be silently "cleared".
    # When any label could not be retrieved, the summary LEADS with
    # the incomplete-check warning, in both the flags-found and the
    # no-mention branch — a found flag does not cure a missing label.
    missing = sorted(set(labels_not_found))
    missing_lead = (
        "Check incomplete — label(s) for "
        + ", ".join(missing)
        + " could not be retrieved, so no conclusion is possible for "
        "those pairs"
        if missing
        else ""
    )
    # S6 fix pass: class-name mentions are not searched, only medicine
    # names are — say so in both branches, so a class mention (as in
    # the live run's "blood thinning (anticoagulant)") is never read
    # as a checked-and-clear result.
    class_caveat = (
        "Class mentions are not searched — only medicine names are — "
        "so a class mention (such as anticoagulant, NSAID, or blood "
        "thinner) is not detected as a flag."
    )
    if not others:
        summary = (
            "No check was performed — no other medicines were listed, so "
            f"there was nothing to check {candidate} against. List the "
            "medicines already taken first, then run the check again. "
            f"Nothing here is a safety result — {NO_MENTION_CAVEAT}"
        )
    elif total_flags:
        # B2 round-2 fix: "Checked in both directions" is unqualified
        # only when no label is missing; with a missing label it is
        # qualified to the labels retrieved.
        checked_phrase = (
            "Checked in both directions for the labels retrieved."
            if missing
            else "Checked in both directions."
        )
        summary = (
            (missing_lead + ". " if missing_lead else "")
            + f"{checked_phrase} {total_flags} label mention(s) "
            f"were found for {candidate} against {', '.join(others)}. Treat "
            "each mention as a label flag to discuss with your pharmacist "
            "or doctor before taking it — a mention is the label raising "
            "the combination, not proof of harm, and ClearDose never calls "
            f"a combination safe. {class_caveat}"
        )
    else:
        # B2 round-2 fix: the direction-1 no-mention clause is
        # conditional on the candidate label having been retrieved.
        # When it was not retrieved, that direction is omitted
        # entirely and the summary states plainly that it did not
        # run — it never asserts a search of a label never fetched.
        # The direction-2 clause stays scoped to labels retrieved.
        if candidate_retrieved:
            direction_1 = (
                "Among the labels actually retrieved, no explicit mention of "
                f"{', '.join(others)} was found in the {candidate} label's "
                "interaction or warnings sections"
            )
        else:
            direction_1 = (
                "The candidate-label direction of the check did not run "
                f"because the {candidate} label could not be retrieved"
            )
        summary = (
            (missing_lead + ". " if missing_lead else "")
            + direction_1
            + f", and no mention of {candidate} was found in the labels "
            f"actually retrieved for {', '.join(others)} — "
            f"{NO_MENTION_CAVEAT} {class_caveat}"
        )
    return with_disclaimer(
        {
            "candidate": candidate,
            "current_medicines_checked": others,
            "excluded_from_check": excluded,
            "labels_not_found": sorted(set(labels_not_found)),
            "flag_groups": flag_groups,
            "flag_count": total_flags,
            "summary": summary,
        }
    )


def _candidates_from_lines(lines: list[str]) -> list[dict]:
    """Match known medicine names in OCR lines, in order of appearance."""
    from .names import all_known_names

    joined = " ".join(lines)
    lowered = joined.lower()
    found: list[dict] = []
    seen: set[str] = set()
    for name in all_known_names():
        match = re.search(rf"\b{re.escape(name)}\b", lowered)
        if match and parse(name).canonical not in seen:
            seen.add(parse(name).canonical)
            # Dose attribution, own line only: the dose must appear on
            # the same OCR line as the medicine name. Never fall back
            # to a dose found anywhere else in the label text — that
            # would attribute another medicine's dose to this one.
            line_with_name = next(
                (ln for ln in lines if name in ln.lower()), ""
            )
            dose_match = _DOSE_RE.search(line_with_name)
            found.append(
                {
                    "medicine": parse(name).canonical,
                    "matched_term": name,
                    "dose_on_label": (
                        f"{dose_match.group(1)} mg" if dose_match else None
                    ),
                    "line": line_with_name,
                }
            )
    found.sort(key=lambda c: lowered.find(c["matched_term"]))
    return found


def check_label_photo(
    image_bytes: bytes,
    current_medicines: list[str],
    fetch,
    ocr: OCRProvider,
) -> dict:
    """Read a bottle-label photo, match the medicine, run the flag check.

    Exactly one candidate -> the interaction check runs. Zero or
    several candidates -> no check runs and no guess is made.
    """
    if not image_bytes:
        return with_disclaimer(
            {
                "photo_read": False,
                "summary": "No photo was provided.",
                "data_source": "none",
            }
        )
    if len(image_bytes) > 5_000_000:
        return with_disclaimer(
            {
                "photo_read": False,
                "summary": "The photo is larger than the 5 MB limit.",
                "data_source": "none",
            }
        )
    try:
        result: OCRResult = ocr.read_text(image_bytes)
    except OCRNotConfigured as exc:
        return with_disclaimer(
            {
                "photo_read": False,
                "ocr_configured": False,
                "summary": str(exc),
                "data_source": "none",
            }
        )
    except OCRUnavailable as exc:
        return with_disclaimer(
            {
                "photo_read": False,
                "ocr_configured": True,
                "summary": str(exc),
                "data_source": "none",
            }
        )
    lines = [ln.text for ln in result.lines if ln.confidence >= 50]
    candidates = _candidates_from_lines(lines)
    base = {
        "photo_read": True,
        "ocr_provider": result.provider,
        "synthetic_sample": result.synthetic,
        "lines_read": lines,
        "candidates": candidates,
    }
    if len(candidates) == 0:
        return with_disclaimer(
            {
                **base,
                "summary": (
                    "The label text was read, but no known medicine name "
                    "was found in it. Type the medicine name and use the "
                    "interaction check instead of guessing from the photo."
                ),
            }
        )
    if len(candidates) > 1:
        return with_disclaimer(
            {
                **base,
                "summary": (
                    "More than one medicine name was found on the label. "
                    "ClearDose will not guess which one to check — pick one "
                    "name and run the interaction check for it."
                ),
            }
        )
    candidate = candidates[0]["medicine"]
    checked = flag_interactions(candidate, current_medicines, fetch)
    checked.pop("disclaimer", None)
    return with_disclaimer(
        {
            **base,
            "matched_medicine": candidate,
            "dose_on_label": candidates[0]["dose_on_label"],
            "interaction_check": checked,
            "summary": (
                f"The label reads as {candidate}"
                + (
                    f" ({candidates[0]['dose_on_label']})"
                    if candidates[0]["dose_on_label"]
                    else ""
                )
                + ". " + checked["summary"]
            ),
        }
    )


def generate_pharmacist_questions(
    medicine: str, current_medicines: list[str], fetch
) -> dict:
    """Questions to take to a pharmacist, built from the flag check."""
    checked = flag_interactions(medicine, current_medicines, fetch)
    questions = [
        f"I take {', '.join(current_medicines) if current_medicines else 'no other medicines listed'}. "
        f"Is {medicine} right to take alongside them?",
        f"What warning signs should make me call you or my doctor after starting {medicine}?",
        "Is there a time of day, or food, I should take it with — or avoid?",
        "What should I do if I miss a dose, and what should I never do to catch up?",
    ]
    if checked["flag_count"]:
        for group in checked["flag_groups"]:
            for flag in group["flags"]:
                questions.insert(
                    1,
                    f"The {group['source_label']} label mentions "
                    f"{flag['mentioned_medicine']} in its {flag['section']} "
                    "section. What does that mean for me, and what should I "
                    "do before my first dose?",
                )
                break
    if checked["labels_not_found"]:
        questions.append(
            "The label for "
            + ", ".join(checked["labels_not_found"])
            + " could not be retrieved — can you check it from the "
            "official information leaflet?"
        )
    return with_disclaimer(
        {
            "medicine": medicine,
            "current_medicines": current_medicines,
            "flag_count": checked["flag_count"],
            "questions": questions,
            "note": (
                "Take this list to your pharmacist. It is a starting point "
                "for a conversation, not advice about what to take."
            ),
        }
    )


__all__ = [
    "DISCLAIMER",
    "explain_prescription",
    "flag_interactions",
    "check_label_photo",
    "generate_pharmacist_questions",
]
