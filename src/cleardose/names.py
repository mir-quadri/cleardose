"""Medicine-name handling for ClearDose.

Normalisation plus a deliberately small, auditable brand/generic map.
This is a matching aid for label text, not a drug database: names not
in the map are still looked up by their normalised spelling in
openFDA, they simply get no alias expansion.

Overlap disclosure: the map covers the same public brand/generic
facts as an earlier, separately submitted project's map (e.g.
Advil/ibuprofen, Coumadin/warfarin) — those pairings are public
facts, not code — and it was recreated in Python for this project
with the same 10 canonical names, except the multi-word alias
"bayer aspirin" was dropped (only "ecotrin" is kept for aspirin).
See docs/ORIGINALITY.md for the full statement.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FORM_WORDS = (
    "sodium", "hydrochloride", "hcl", "tablets", "tablet",
    "capsules", "capsule", "extended release", "mg", "ml",
)

_ALIASES: dict[str, tuple[str, ...]] = {
    "warfarin": ("coumadin", "jantoven"),
    "ibuprofen": ("advil", "motrin"),
    "acetaminophen": ("tylenol", "paracetamol"),
    "atorvastatin": ("lipitor",),
    "metformin": ("glucophage",),
    "lisinopril": ("zestril", "prinivil"),
    "aspirin": ("ecotrin",),
    "omeprazole": ("prilosec",),
    "sertraline": ("zoloft",),
    "amoxicillin": ("amoxil",),
}


@dataclass(frozen=True)
class DrugName:
    """A medicine name as given, plus its canonical form and aliases."""

    given: str
    canonical: str
    aliases: tuple[str, ...]

    @property
    def search_terms(self) -> list[str]:
        terms = {self.given, self.canonical, *self.aliases}
        return sorted(t for t in terms if len(t) >= 3)


_DOSE_FORM_TOKEN = re.compile(
    r"(?:\d+(?:\.\d+)?|extended\s+release|tablets?|capsules?|"
    r"sodium|hydrochloride|hcl|mcg|mg|ml|g)"
)


def _is_dose_form_only(inner: str) -> bool:
    """True only when a parenthetical's content is dose/form words.

    Allowed: numbers, units (mg/ml/mcg/g), tablet(s)/capsule(s),
    "extended release", and salt/form words from _FORM_WORDS, in
    any combination, separated by spaces/commas. Anything else
    (PM, "with codeine", "extra", ...) is NOT dose/form-only.
    Nested parens are never dose/form-only: the whole group is
    then left intact by the caller, so no stray ")" can result.
    """
    s = inner.strip().lower()
    if not s:
        return True
    if "(" in s or ")" in s:
        return False
    pos = 0
    while pos < len(s):
        # Skip separators between tokens.
        sep = re.match(r"[\s,;]+", s[pos:])
        if sep:
            pos += sep.end()
            if pos >= len(s):
                break
            continue
        token = _DOSE_FORM_TOKEN.match(s, pos)
        if token is None:
            return False
        pos = token.end()
    return pos >= len(s) and s.strip() != ""


def _strip_dose_form_parens(name: str) -> str:
    """Remove only dose/form-only parenthetical groups, balanced.

    Groups are matched with depth counting, so nested parens are
    handled as one whole group: a non-dose/form group (including
    any nested content) is copied verbatim, never partially
    stripped — a stray ")" is impossible. An unbalanced "(" is
    likewise copied verbatim to the end.
    """
    out: list[str] = []
    i = 0
    while i < len(name):
        if name[i] != "(":
            out.append(name[i])
            i += 1
            continue
        depth = 1
        j = i + 1
        while j < len(name) and depth > 0:
            if name[j] == "(":
                depth += 1
            elif name[j] == ")":
                depth -= 1
            j += 1
        if depth != 0:
            out.append(name[i:])
            break
        inner = name[i + 1 : j - 1]
        if _is_dose_form_only(inner):
            out.append(" ")
        else:
            out.append(name[i:j])
        i = j
    return "".join(out)


def normalize(raw: str) -> str:
    """Lowercase, collapse whitespace, strip trailing form/dose words.

    S2 fix pass: also strip parenthetical dose/form content
    ("ibuprofen (200 mg)" -> "ibuprofen") and trailing punctuation
    ("Ibuprofen," -> "ibuprofen", "Advil." -> "advil"). Alias
    resolution stays exact-match-only: "Advil PM" normalises to
    "advil pm", which matches no alias, so it is NOT mapped to
    ibuprofen (extra ingredient).
    S2 round-2 fix: parenthetical removal is restricted to
    DOSE/FORM-ONLY contents. Any other parenthetical content
    ("Advil (PM)", "acetaminophen (with codeine)") is LEFT
    INTACT, so the name does NOT resolve to a bare canonical —
    failing toward honest unknown, never toward a wrong drug.
    Nested parens are left whole, never partially stripped.
    """
    name = re.sub(r"\s+", " ", raw.strip().lower())
    name = _strip_dose_form_parens(name)
    name = re.sub(r"[.,;:!?]+$", "", name.strip())
    name = re.sub(r"\s+\d+(\.\d+)?\s*(mg|ml|mcg|g)\b", "", name)
    changed = True
    while changed:
        changed = False
        for word in _FORM_WORDS:
            suffix = f" {word}"
            if name.endswith(suffix):
                name = name[: -len(suffix)].strip()
                changed = True
    name = re.sub(r"[.,;:!?]+$", "", name.strip())
    return name.strip()


def parse(raw: str) -> DrugName:
    """Resolve a raw name to its canonical form via the alias map."""
    given = normalize(raw)
    for canonical, aliases in _ALIASES.items():
        if given == canonical or given in aliases:
            return DrugName(given=given, canonical=canonical, aliases=aliases)
    return DrugName(given=given, canonical=given, aliases=())


def same_drug(a: str, b: str) -> bool:
    """True when two names refer to the same drug (brand counts)."""
    return parse(a).canonical == parse(b).canonical


def all_known_names() -> list[str]:
    """Every canonical name plus alias in the map, for label scanning."""
    names: list[str] = []
    for canonical, aliases in _ALIASES.items():
        names.append(canonical)
        names.extend(aliases)
    return names
