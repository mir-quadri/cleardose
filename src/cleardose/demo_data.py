"""Demo-only label records. NOT FDA labels. NOT live data.

These short records exist so the CLI demo and the demo video script
run offline and reproducibly. Every record is marked demo, and every
tool result built from one carries data_source "DEMO DATA". A live
run uses OpenFDALabelClient instead and says "live openFDA".
"""
from __future__ import annotations

from .labels import LabelRecord


def demo_label(medicine: str) -> LabelRecord | None:
    records = {
        "ibuprofen": LabelRecord(
            name="ibuprofen",
            brand_names=["Advil", "Motrin"],
            generic_names=["ibuprofen"],
            sections={
                "indications_and_usage": (
                    "DEMO DATA: used for temporary relief of minor aches and pains."
                ),
                "warnings": (
                    "DEMO DATA: ask a doctor before use if you take a blood thinner "
                    "such as warfarin."
                ),
                "drug_interactions": (
                    "DEMO DATA: bleeding has been reported when ibuprofen is used "
                    "with warfarin-type anticoagulants."
                ),
            },
            data_source="DEMO DATA — not an FDA label",
        ),
        "warfarin": LabelRecord(
            name="warfarin",
            brand_names=["Coumadin"],
            generic_names=["warfarin"],
            sections={
                "indications_and_usage": (
                    "DEMO DATA: used to reduce the risk of blood clots."
                ),
                "boxed_warning": (
                    "DEMO DATA: bleeding risk — the risk of bleeding is higher "
                    "when warfarin is combined with ibuprofen and other NSAIDs."
                ),
                "drug_interactions": (
                    "DEMO DATA: ibuprofen increases the risk of bleeding in "
                    "people taking warfarin."
                ),
            },
            data_source="DEMO DATA — not an FDA label",
        ),
    }
    return records.get(medicine.strip().lower())
