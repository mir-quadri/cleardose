from cleardose.cli import _demo_fetch
from cleardose.ocr import MockOCRProvider
from cleardose.safety import DISCLAIMER
from cleardose.tools import (
    check_label_photo,
    explain_prescription,
    flag_interactions,
    generate_pharmacist_questions,
)


def test_explain_demo_carries_disclaimer_and_source():
    result = explain_prescription("ibuprofen", _demo_fetch)
    assert result["label_found"] is True
    assert result["data_source"].startswith("DEMO DATA")
    assert result["disclaimer"] == DISCLAIMER
    assert result["plain_language_sections"][0]["heading"] == "What it is used for"


def test_explain_unknown_label_not_found_not_fabricated():
    result = explain_prescription("nosuchdrug", _demo_fetch)
    assert result["label_found"] is False
    assert "No FDA label" in result["summary"]


def test_flag_bidirectional_demo():
    result = flag_interactions("ibuprofen", ["warfarin"], _demo_fetch)
    assert result["flag_count"] >= 2
    sources = {g["source_label"] for g in result["flag_groups"]}
    assert sources == {"ibuprofen", "warfarin"}
    assert "never calls" in result["summary"] or "never" in result["summary"]
    assert result["disclaimer"] == DISCLAIMER


def test_flag_no_mention_language():
    result = flag_interactions("ibuprofen", ["metformin"], _demo_fetch)
    # metformin has no demo record, so its label is not found. B2 fix
    # pass: the summary must LEAD with the incomplete-check warning
    # and scope the no-mention claim to labels actually retrieved —
    # never a blanket "clear" for the missing pair.
    assert result["labels_not_found"] == ["metformin"]
    assert result["summary"].startswith(
        "Check incomplete — label(s) for metformin could not be "
        "retrieved, so no conclusion is possible for those pairs"
    )
    assert "labels actually retrieved" in result["summary"]
    assert "not a guarantee of safety" in result["summary"]


def test_flag_missing_label_lead_in_flags_found_branch():
    # B2 fix pass: a found flag does not cure a missing label. Use a
    # stub fetch where warfarin is found (flag) and metformin is not.
    from cleardose.labels import LabelLookup

    def fetch(name):
        if name == "metformin":
            return LabelLookup(found=False, reason="No demo record.")
        return _demo_fetch(name)

    result = flag_interactions("ibuprofen", ["warfarin", "metformin"], fetch)
    assert result["flag_count"] >= 1
    assert "metformin" in result["labels_not_found"]
    assert result["summary"].startswith(
        "Check incomplete — label(s) for metformin could not be "
        "retrieved, so no conclusion is possible for those pairs"
    )


def test_flag_class_mention_caveat_both_branches():
    # S6 fix pass: both branches state that class mentions are not
    # searched — only medicine names are.
    found = flag_interactions("ibuprofen", ["warfarin"], _demo_fetch)
    assert "Class mentions are not searched" in found["summary"]
    assert "only medicine names are" in found["summary"]
    assert "anticoagulant" in found["summary"]
    missing = flag_interactions("ibuprofen", ["metformin"], _demo_fetch)
    assert "Class mentions are not searched" in missing["summary"]
    assert "only medicine names are" in missing["summary"]


def test_photo_summary_with_missing_label_still_reads_sensibly():
    # check_label_photo inherits the flag summary by concatenation.
    result = check_label_photo(
        b"bytes", ["metformin"], _demo_fetch, MockOCRProvider("ibuprofen-200mg")
    )
    assert result["summary"].startswith("The label reads as ibuprofen")
    assert "Check incomplete" in result["summary"]
    assert "metformin" in result["summary"]


def test_flag_empty_list_no_check():
    result = flag_interactions("ibuprofen", [], _demo_fetch)
    assert result["flag_count"] == 0
    assert "No check was performed" in result["summary"]


def test_flag_same_drug_excluded():
    result = flag_interactions("Advil", ["ibuprofen"], _demo_fetch)
    assert result["excluded_from_check"] == ["ibuprofen"]
    assert result["current_medicines_checked"] == []


def test_photo_single_candidate_runs_check():
    result = check_label_photo(
        b"bytes", ["warfarin"], _demo_fetch, MockOCRProvider("ibuprofen-200mg")
    )
    assert result["photo_read"] is True
    assert result["synthetic_sample"] is True
    assert result["matched_medicine"] == "ibuprofen"
    assert result["dose_on_label"] == "200 mg"
    assert result["interaction_check"]["flag_count"] >= 1


def test_photo_no_candidate_no_check_no_guess():
    result = check_label_photo(
        b"bytes", ["warfarin"], _demo_fetch, MockOCRProvider("nope")
    )
    assert result["photo_read"] is True
    assert result["candidates"] == []
    assert "interaction_check" not in result


def test_explain_never_shows_dosage_section():
    from cleardose.labels import LabelLookup, LabelRecord

    record = LabelRecord(
        name="ibuprofen",
        sections={
            "indications_and_usage": "Relieves pain.",
            "dosage_and_administration": "Take 2 tablets every 6 hours.",
        },
        data_source="test",
    )
    result = explain_prescription(
        "ibuprofen", lambda m: LabelLookup(found=True, record=record)
    )
    sections = [s["section"] for s in result["plain_language_sections"]]
    assert "dosage_and_administration" not in sections
    assert "Take 2 tablets" not in str(result)
    assert "follow your prescription" in result["note"]


def test_photo_multiple_candidates_no_check_and_own_line_dose_only():
    from cleardose.ocr import OCRResult, TextLine

    class TwoLabelOCR:
        def read_text(self, image_bytes):
            return OCRResult(
                lines=[
                    TextLine(text="IBUPROFEN", confidence=99.0),
                    TextLine(text="ACETAMINOPHEN 500 mg Tablets", confidence=99.0),
                ],
                provider="test-ocr",
                synthetic=False,
            )

    result = check_label_photo(
        b"bytes", ["warfarin"], _demo_fetch, TwoLabelOCR()
    )
    assert result["photo_read"] is True
    assert len(result["candidates"]) == 2
    assert "interaction_check" not in result
    by_medicine = {c["medicine"]: c for c in result["candidates"]}
    # Own-line only: ibuprofen's line has no dose, so it must NOT
    # inherit acetaminophen's 500 mg from elsewhere in the text.
    assert by_medicine["ibuprofen"]["dose_on_label"] is None
    assert by_medicine["acetaminophen"]["dose_on_label"] == "500 mg"
    result = check_label_photo(
        b"bytes", ["warfarin"], _demo_fetch, MockOCRProvider("nope")
    )
    assert result["photo_read"] is True
    assert result["candidates"] == []
    assert "interaction_check" not in result


def test_photo_oversize_rejected():
    result = check_label_photo(
        b"x" * 5_000_001, ["warfarin"], _demo_fetch, MockOCRProvider()
    )
    assert result["photo_read"] is False


def test_photo_not_configured_rekognition(monkeypatch):
    from cleardose.ocr import RekognitionOCRProvider

    monkeypatch.delenv("REKOGNITION_ENABLED", raising=False)
    result = check_label_photo(
        b"bytes", ["warfarin"], _demo_fetch, RekognitionOCRProvider()
    )
    assert result["photo_read"] is False
    assert result["ocr_configured"] is False


def test_questions_include_flag_question():
    result = generate_pharmacist_questions("ibuprofen", ["warfarin"], _demo_fetch)
    assert len(result["questions"]) >= 4
    assert any("label mentions" in q for q in result["questions"])
    assert result["disclaimer"] == DISCLAIMER
    joined = " ".join(result["questions"]).lower()
    assert "safe to take" not in joined
    assert "take 2" not in joined
    assert "increase the dose" not in joined


def test_flag_candidate_missing_no_search_of_unretrieved_label():
    # B2 round-2 fix: candidate label never retrieved, so the summary
    # must NOT claim any search of that label. Old code said "no
    # explicit mention ... was found in the unknownmed label's
    # interaction or warnings sections" — asserting a search of a
    # label never fetched. Fails on the old code.
    result = flag_interactions("unknownmed", ["warfarin"], _demo_fetch)
    assert result["labels_not_found"] == ["unknownmed"]
    assert result["summary"].startswith(
        "Check incomplete — label(s) for unknownmed could not be "
        "retrieved, so no conclusion is possible for those pairs"
    )
    assert "in the unknownmed label" not in result["summary"]
    assert "did not run" in result["summary"]
    assert "unknownmed label could not be retrieved" in result["summary"]
    # Direction 2 (warfarin's label, actually retrieved) still stands.
    assert "labels actually retrieved for warfarin" in result["summary"]


def test_flag_flags_branch_qualified_when_label_missing():
    # B2 round-2 fix: with a label missing, the flags branch must
    # qualify "Checked in both directions" to the labels retrieved,
    # and the unqualified standalone claim must be absent.
    result = flag_interactions("ibuprofen", ["warfarin", "metformin"], _demo_fetch)
    assert result["flag_count"] >= 1
    assert "metformin" in result["labels_not_found"]
    assert "Checked in both directions for the labels retrieved." in result["summary"]
    assert "Checked in both directions." not in result["summary"]
    # Control: with no label missing, the unqualified wording stands.
    clean = flag_interactions("ibuprofen", ["warfarin"], _demo_fetch)
    assert clean["labels_not_found"] == []
    assert "Checked in both directions." in clean["summary"]
