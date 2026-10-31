"""FDA label lookup via openFDA, with honest provenance.

Design decision that distinguishes ClearDose: there is NO bundled
fallback label text. If the live openFDA lookup fails, the result
says the label could not be retrieved — ClearDose never flags or
clears a combination from stale, bundled prose. Demo scenarios use
explicitly-marked demo data (see demo_data.py), never disguised as
a live label.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

import requests

OPENFDA_URL = "https://api.fda.gov/drug/label.json"

# Label sections ClearDose reads, in plain-language order.
# No dosage_and_administration: ClearDose never shows a dosing
# section, so no excerpt can be read as dosing advice.
SECTIONS = (
    ("indications_and_usage", "What it is used for"),
    ("warnings", "Important warnings"),
    ("drug_interactions", "Interactions with other medicines"),
    ("boxed_warning", "Boxed warning (the strongest warning on the label)"),
)


@dataclass
class LabelRecord:
    """One medicine's label, as returned by openFDA (or demo data)."""

    name: str
    brand_names: list[str] = field(default_factory=list)
    generic_names: list[str] = field(default_factory=list)
    sections: dict[str, str] = field(default_factory=dict)
    data_source: str = "live openFDA"

    def section_text(self, key: str) -> str:
        return self.sections.get(key, "")


@dataclass
class LabelLookup:
    found: bool
    record: LabelRecord | None = None
    reason: str = ""


def _first_text(value: object) -> str:
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value) if value else ""


class OpenFDALabelClient:
    """Live openFDA client with a small, bounded in-memory cache.

    Names are normalised before fetching (canonical form, dose/form
    words stripped — see names.parse), so "Ibuprofen 200 mg Tablets"
    and "warfarin sodium" query openFDA as "ibuprofen" and "warfarin".
    Only successful lookups are cached; failed lookups are never
    cached, so a transient failure does not poison results for an
    hour. The cache holds at most 128 entries (oldest evicted first).
    """

    _MAX_CACHE = 128

    def __init__(self, timeout_seconds: float = 5.0, cache_ttl_seconds: int = 3600):
        self._timeout = timeout_seconds
        self._ttl = cache_ttl_seconds
        self._cache: dict[str, tuple[float, LabelLookup]] = {}

    def fetch(self, medicine: str) -> LabelLookup:
        # Imported here to keep module import order simple (names
        # does not import labels, but this avoids any cycle risk).
        from .names import parse

        canonical = parse(medicine).canonical
        cached = self._cache.get(canonical)
        if cached and time.monotonic() - cached[0] < self._ttl:
            return cached[1]
        result = self._fetch_live(canonical)
        if result.found:
            if len(self._cache) >= self._MAX_CACHE:
                self._cache.pop(next(iter(self._cache)))
            self._cache[canonical] = (time.monotonic(), result)
        return result

    def _fetch_live(self, medicine: str) -> LabelLookup:
        query = f'openfda.generic_name:"{medicine}" OR openfda.brand_name:"{medicine}"'
        try:
            response = requests.get(
                OPENFDA_URL,
                params={"search": query, "limit": 1},
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            return LabelLookup(found=False, reason=f"openFDA request failed: {exc}")
        if response.status_code == 404:
            return LabelLookup(found=False, reason=f"No FDA label found for {medicine!r}.")
        if not response.ok:
            return LabelLookup(
                found=False, reason=f"openFDA returned HTTP {response.status_code}."
            )
        try:
            results = response.json()["results"]
        except (ValueError, KeyError) as exc:
            return LabelLookup(found=False, reason=f"openFDA response unreadable: {exc}")
        if not results:
            return LabelLookup(found=False, reason=f"No FDA label found for {medicine!r}.")
        raw = results[0]
        openfda = raw.get("openfda", {})
        sections = {
            key: _first_text(raw.get(key, ""))
            for key, _ in SECTIONS
            if raw.get(key)
        }
        record = LabelRecord(
            name=_first_text(openfda.get("generic_name", [medicine])),
            brand_names=[str(v) for v in openfda.get("brand_name", [])],
            generic_names=[str(v) for v in openfda.get("generic_name", [])],
            sections=sections,
            data_source="live openFDA",
        )
        return LabelLookup(found=True, record=record)


@dataclass
class Mention:
    """A quoted mention of another medicine inside one label section."""

    medicine: str
    section: str
    excerpt: str


def find_mentions(record: LabelRecord, medicine_names: list[str]) -> list[Mention]:
    """Find whole-word mentions of each medicine in interaction/warning text.

    Only the interaction, warnings, and boxed-warning sections are
    scanned — an indications mention is not an interaction flag.
    Excerpts are verbatim slices of the label, never paraphrases.
    """
    mentions: list[Mention] = []
    for key in ("drug_interactions", "warnings", "boxed_warning"):
        text = record.section_text(key)
        if not text:
            continue
        for name in medicine_names:
            pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                start = max(0, match.start() - 120)
                end = min(len(text), match.end() + 160)
                excerpt = text[start:end].strip()
                mentions.append(
                    Mention(medicine=name, section=key, excerpt=excerpt)
                )
    return mentions
