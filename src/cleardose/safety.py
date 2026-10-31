"""Safety language for ClearDose. Non-negotiable, applied everywhere.

Every user-facing output carries the disclaimer. No output — tool
result, model text, demo script, or article — may call a combination
safe, or tell a person how much of a medicine to take.
"""
from __future__ import annotations

import re

DISCLAIMER = (
    "Advisory only — not medical advice. ClearDose reads FDA label text and "
    "presents it under plain-language headings. It does not replace your pharmacist or "
    "doctor. Never start, stop, or change a medication based on this tool — "
    "discuss every question with your pharmacist or doctor first."
)

NO_MENTION_CAVEAT = (
    "No mention was found in the label sections checked. That is not a "
    "guarantee of safety: FDA labels are incomplete, vary by manufacturer, "
    "and cannot cover every combination. Always confirm a new medication "
    "with your pharmacist or doctor."
)

# Patterns that must never appear in a ClearDose answer about a combination
# or a dose. Used to filter model-generated text before it reaches a user.
# Deliberately broad for model prose in the Strands path: a false
# positive there yields a withheld answer, not a wrong medical claim.
# Kept narrow enough not to block the disclaimer itself, the standard
# pharmacist questions, or ordinary safe sentences such as "Take this
# list to your pharmacist."
_UNSAFE_PATTERNS = [
    re.compile(r"\bsafe to (take|use)\b", re.IGNORECASE),
    re.compile(r"\bis safe\b", re.IGNORECASE),
    re.compile(r"\bperfectly safe\b", re.IGNORECASE),
    re.compile(r"\bsafe for (you|anyone)\b", re.IGNORECASE),
    re.compile(r"\bsafely (take|use)\b", re.IGNORECASE),
    re.compile(r"\bno risk\b", re.IGNORECASE),
    re.compile(r"\byou should take\b", re.IGNORECASE),
    re.compile(r"\btake \d+\b", re.IGNORECASE),
    re.compile(r"\bincrease|decrease (the )?dose\b", re.IGNORECASE),
    re.compile(r"\bdouble (the )?dose\b", re.IGNORECASE),
    # B1 fix pass: safe-to-combine phrasings.
    re.compile(r"\bsafe to combine\b", re.IGNORECASE),
    re.compile(r"\bsafely combine\b", re.IGNORECASE),
    re.compile(r"\bsafe combination\b", re.IGNORECASE),
    re.compile(
        r"\bis a safe (combination|medicine|medication|drug|pair|mix)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bcombination is (fine|ok|okay|safe)\b", re.IGNORECASE),
    re.compile(r"\bfine to take together\b", re.IGNORECASE),
    # B1 fix pass: word-number dosing ("take one tablet ...").
    re.compile(
        r"\btake (one|two|three|four|five|six|seven|eight|nine|ten) "
        r"(tablet|tablets|capsule|capsules|pill|pills)\b",
        re.IGNORECASE,
    ),
    # B1 fix pass: dose statements ("the dose is 200 mg daily") and
    # bare "N mg daily"-style dose assertions. Round-2 narrowing:
    # a bare "dose is" is NOT blocked — the pattern requires a
    # dose value (number + unit, or word-number + tablet/capsule/
    # pill) after "dose is", so ordinary meta-sentences such as
    # "The dose is on your prescription bottle." and "The dose is
    # not shown here." pass, while "The daily dose is 200 mg"
    # still blocks.
    re.compile(
        r"\bdose\s+is\b[^.\n]{0,30}?\b(?:\d+(?:\.\d+)?\s*"
        r"(?:mg|g|mcg|µg|ml|units?|tablets?|capsules?|pills?|drops?)|"
        r"(?:one|two|three|four|five|six|seven|eight|nine|ten)\s+"
        r"(?:tablets?|capsules?|pills?))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b\d+(?:\.\d+)?\s*mg (daily|a day|per day|every day)\b",
        re.IGNORECASE,
    ),
    # B1 fix pass: absence-implies-safe conclusions ("no interaction
    # was found, so it is ok/fine/safe").
    re.compile(
        r"\bno interaction(s)? (was |were )?found\b[^.]*\b(ok|okay|fine|safe)\b",
        re.IGNORECASE,
    ),
    # B1 fix pass: harm-denial ("it won't hurt you"). Round-2
    # narrowing: "hurt" requires the medical object "you", so the
    # idiom "It won't hurt to ask your pharmacist." passes.
    re.compile(r"\b(won't|will not|would not) hurt you\b", re.IGNORECASE),
    # B1 round-2 structural fix: paraphrase classes, not exact
    # strings. Each pattern below covers a whole family — flexible
    # intervening words, either word order, and synonyms — so a
    # rewording of a blocked claim is still blocked. The scoped
    # tool-result phrasing "No mention was found in the label
    # sections checked" contains none of these triggers (it says
    # "mention", not "interaction", and names no dose, harm, or
    # permission verb), so it still passes; see the regression
    # test test_scoped_no_mention_still_passes.
    # Take/use + (pronoun/quantifier) + together, in either
    # direction of the safety word: "take them together",
    # "take these together safely", "use them together".
    re.compile(r"\b(take|use)(?:\s+\w+){0,4}\s+together\b", re.IGNORECASE),
    re.compile(r"\btogether\s+(safely|safe)\b", re.IGNORECASE),
    re.compile(
        r"\btogether\b[^.\n]{0,40}?\b(safely|safe|fine|ok|okay)\b",
        re.IGNORECASE,
    ),
    # Take/use + ... + safely, trailing or not: "take these
    # together safely", "take it safely", "use both safely".
    re.compile(r"\b(take|use)(?:\s+\w+){0,5}\s+safely\b", re.IGNORECASE),
    # Combine/mix + ... + safety conclusion, and safety word + to
    # + combine/mix/take/use: "combining them is fine", "it is
    # fine to combine them", "okay to mix them", "mix them
    # together", "these should be fine".
    re.compile(
        r"\b(combin(?:e|ing|ed)|mix(?:ing|ed)?)\b[^.\n]{0,40}?"
        r"\b(is|are|seems|looks|feels)\s+(fine|ok|okay|safe|alright|harmless)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(fine|ok|okay|safe|alright)\s+to\s+(combine|mix|take|use)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(combine|mix)(?:\s+\w+){0,4}\s+together\b", re.IGNORECASE
    ),
    re.compile(
        r"\b(safe|fine|ok|okay)\s+together\b", re.IGNORECASE
    ),
    re.compile(
        r"\bshould\s+be\s+(fine|ok|okay|safe|alright)\b", re.IGNORECASE
    ),
    re.compile(
        r"\bperfectly\s+(fine|ok|okay)\b", re.IGNORECASE
    ),
    re.compile(
        r"\b(safe|fine)\s+(pair|pairing|mix|combo)\b", re.IGNORECASE
    ),
    # Harm-denial family: any negation + harm/problems, and
    # "no harm"/"harm-free": "it won't harm you",
    # "no harm in taking them together", "doesn't cause problems",
    # "it is harmless". Round-2 narrowing for "hurt": it is only
    # blocked with a medical object — "hurt you/them/me/..." or
    # "hurt to combine/mix/take/use" — so "It won't hurt to ask
    # your pharmacist." passes while "It does not hurt to
    # combine them" still blocks.
    re.compile(
        r"\b(won't|will not|would not|doesn't|does not|don't|do not|"
        r"can't|cannot|never)\b[^.\n]{0,25}?\b(harm\w*|problems?|issues?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(won't|will not|would not|doesn't|does not|don't|do not|"
        r"can't|cannot|never)\b[^.\n]{0,25}?\bhurt\b\s+"
        r"(you|them|me|us|him|her)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(won't|will not|would not|doesn't|does not|don't|do not|"
        r"can't|cannot|never)\b[^.\n]{0,25}?\bhurt\b\s+to\s+"
        r"(combine|mix|take|use)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bno\s+harm\b", re.IGNORECASE),
    re.compile(
        r"\bno\s+hurt\b[^.\n]{0,25}?\b(taking|using|combining|mixing|you|them)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(harm|hurt)-?free\b", re.IGNORECASE),
    re.compile(r"\bharmless\b", re.IGNORECASE),
    # Go-ahead permission, with or without a following verb:
    # "go ahead and take them together", "no interaction was
    # found, so go ahead", "go right ahead".
    re.compile(r"\bgo\s+(right\s+)?ahead\b", re.IGNORECASE),
    # Absence asserted in model prose, in any finding-word form:
    # bare "no interaction was found" as well as "no known
    # interaction detected/reported". Only the scoped
    # "No mention ..." tool phrasing survives, because it does
    # not contain the word "interaction".
    re.compile(
        r"\bno\s+(known\s+)?interactions?\b", re.IGNORECASE
    ),
    re.compile(r"\bnothing to worry about\b", re.IGNORECASE),
    re.compile(r"\b(in the clear|all clear)\b", re.IGNORECASE),
    re.compile(r"\bcompatible\b", re.IGNORECASE),
    # Dose statements with an intervening adjective, value-gated
    # like the "dose is" pattern above: "daily dose of 200 mg"
    # blocks, but "daily dose" with no value does not. ("The
    # daily dose is 200 mg" is already covered by "dose is" +
    # value above.)
    re.compile(
        r"\b(daily|recommended|usual)\s+dose\s+of\b[^.\n]{0,30}?"
        r"\b(?:\d+(?:\.\d+)?\s*"
        r"(?:mg|g|mcg|µg|ml|units?|tablets?|capsules?|pills?|drops?)|"
        r"(?:one|two|three|four|five|six|seven|eight|nine|ten)\s+"
        r"(?:tablets?|capsules?|pills?))\b",
        re.IGNORECASE,
    ),
]


def check_output_safety(text: str) -> str | None:
    """Return the text with the disclaimer appended, or None if unsafe.

    A None return means the text must be discarded wholesale — never
    edited into shape, because a partial edit could leave a dosing
    instruction intact.
    """
    for pattern in _UNSAFE_PATTERNS:
        if pattern.search(text):
            return None
    # B4 fix pass: "appended" must mean "ends with". Strip ALL existing
    # exact occurrences of the disclaimer first, then append it exactly
    # once at the end — a mid-text disclaimer no longer survives.
    if not text.strip():
        return None
    without = text.replace(DISCLAIMER, "")
    cleaned = re.sub(r"\n{3,}", "\n\n", without).strip()
    if not cleaned:
        # Input was disclaimer text only: return it exactly once.
        return DISCLAIMER
    return f"{cleaned}\n\n{DISCLAIMER}"


def with_disclaimer(payload: dict) -> dict:
    """Attach the disclaimer to a tool-result dict (in place, returned)."""
    payload["disclaimer"] = DISCLAIMER
    return payload
