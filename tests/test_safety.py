from cleardose.safety import DISCLAIMER, check_output_safety


def test_disclaimer_appended():
    out = check_output_safety("Take this list to your pharmacist.")
    assert out is not None and DISCLAIMER in out


def test_safe_claim_discarded():
    assert check_output_safety("This combination is safe to take.") is None
    assert check_output_safety("It is perfectly safe.") is None
    assert check_output_safety("You can safely take it.") is None


def test_dosing_advice_discarded():
    assert check_output_safety("You should take 2 tablets.") is None
    assert check_output_safety("Increase the dose tomorrow.") is None


def test_empty_discarded():
    assert check_output_safety("   ") is None


# B1 fix pass: one probe test per bypass that previously passed.
def test_bypass_fine_to_take_together_blocked():
    assert check_output_safety("This combination is fine to take together") is None


def test_bypass_safe_combination_blocked():
    assert check_output_safety("This is a safe combination") is None


def test_bypass_safe_to_combine_blocked():
    assert check_output_safety("Safe to combine") is None


def test_bypass_safely_combine_blocked():
    assert check_output_safety("You can safely combine them") is None


def test_bypass_word_number_dosing_blocked():
    assert check_output_safety("Take one tablet in the morning") is None
    assert check_output_safety("Take two capsules at night") is None


def test_bypass_dose_statement_blocked():
    assert check_output_safety("The dose is 200 mg daily") is None


def test_bypass_bare_mg_daily_blocked():
    assert check_output_safety("200 mg daily should be fine") is None
    # The bare assertion on its own must be blocked even without
    # any other unsafe wording.
    assert check_output_safety("The patient takes 200 mg daily.") is None


def test_bypass_absence_implies_safe_blocked():
    assert check_output_safety("No interaction was found, so it is ok") is None


def test_bypass_harm_denial_blocked():
    assert check_output_safety("It won't hurt you") is None
    assert check_output_safety("It will not hurt you") is None


def test_safe_sentences_still_pass():
    # Regression: ordinary safe sentences must not be blocked.
    assert check_output_safety("Take this list to your pharmacist.") is not None
    assert check_output_safety("Ask your pharmacist about this medicine.") is not None
    assert (
        check_output_safety("The label mentions warfarin in its warnings section.")
        is not None
    )
    assert (
        check_output_safety(
            "Discuss every question with your pharmacist or doctor first."
        )
        is not None
    )


def test_standard_question_phrasings_still_pass():
    # The standard pharmacist questions (tests/test_tools.py) must
    # survive the filter if ever run through it.
    assert (
        check_output_safety("Is ibuprofen right to take alongside them?")
        is not None
    )
    assert (
        check_output_safety(
            "What should I do if I miss a dose, and what should I never "
            "do to catch up?"
        )
        is not None
    )
    assert (
        check_output_safety(
            "Is there a time of day, or food, I should take it with — "
            "or avoid?"
        )
        is not None
    )


def test_disclaimer_text_itself_not_blocked():
    out = check_output_safety(DISCLAIMER)
    assert out is not None
    assert out.count(DISCLAIMER) == 1
    assert out.endswith(DISCLAIMER)


def test_mid_text_disclaimer_moved_to_end_once():
    # B4 fix pass: a disclaimer in the middle must come back exactly
    # once, at the end.
    text = f"Ask your pharmacist. {DISCLAIMER} Then check again."
    out = check_output_safety(text)
    assert out is not None
    assert out.count(DISCLAIMER) == 1
    assert out.endswith(DISCLAIMER)
    assert "Then check again." in out
    # Multiple occurrences collapse to one, at the end.
    text2 = f"{DISCLAIMER} Ask your pharmacist. {DISCLAIMER}"
    out2 = check_output_safety(text2)
    assert out2 is not None
    assert out2.count(DISCLAIMER) == 1
    assert out2.endswith(DISCLAIMER)


# B1 round-2 fix pass: one regression test per peer-review slip.
# Each asserts the structural pattern class, not one exact string.
def test_round2_take_together_safely_blocked():
    assert check_output_safety("You can take these together safely") is None


def test_round2_fine_to_take_them_together_blocked():
    assert check_output_safety("It's fine to take them together") is None


def test_round2_combining_is_fine_blocked():
    assert check_output_safety("Combining them is fine") is None


def test_round2_fine_to_combine_blocked():
    assert check_output_safety("It is fine to combine them") is None


def test_round2_wont_harm_blocked():
    assert check_output_safety("It won't harm you") is None


def test_round2_no_harm_in_taking_together_blocked():
    assert check_output_safety("No harm in taking them together") is None


def test_round2_go_ahead_take_together_blocked():
    assert check_output_safety("Go ahead and take them together") is None


def test_round2_no_interaction_so_go_ahead_blocked():
    assert check_output_safety("No interaction was found, so go ahead") is None


def test_round2_daily_dose_is_blocked():
    assert check_output_safety("The daily dose is 200 mg") is None


def test_round2_bare_no_interaction_found_blocked():
    assert check_output_safety("No interaction was found") is None


def test_scoped_no_mention_still_passes():
    # The honest scoped tool-result phrasing must survive: it says
    # "mention", not "interaction", and asserts no dose, harm, or
    # permission claim.
    out = check_output_safety("No mention was found in the label sections checked")
    assert out is not None and DISCLAIMER in out


def test_round2_fresh_paraphrases_all_blocked():
    # Fresh adversarial paraphrases beyond the 10 listed slips:
    # new word orders, synonyms, and pronoun insertions across
    # the safe/fine/combine/dose/harm/go-ahead themes. Every one
    # must be blocked by a pattern class, not an exact string.
    fresh = [
        "You can safely use them together",
        "Taking them together is perfectly fine",
        "It is safe to mix them",
        "Mixing the two is okay",
        "There is no known interaction between them",
        "You won't be harmed by taking both",
        "The recommended dose is 200 mg",
        "Go right ahead and use them",
        "These two are compatible, so you can take them",
        "Nothing to worry about when you take both",
        "It should be fine to take both together",
        "Combining the medicines looks safe",
        "You're in the clear with this pair",
        "No interaction detected between these medicines",
        "Together, they are safe to use",
        "It does not hurt to combine them",
    ]
    for phrase in fresh:
        assert check_output_safety(phrase) is None, phrase


# B1 round-2 narrowing: dose/hurt patterns must require a value /
# medical object, so ordinary meta-sentences pass.
def test_round2_narrowing_dose_meta_sentences_pass():
    assert (
        check_output_safety("The dose is on your prescription bottle.")
        is not None
    )
    assert check_output_safety("The dose is not shown here.") is not None
    # ... while a valued dose statement still blocks.
    assert check_output_safety("The daily dose is 200 mg") is None
    assert check_output_safety("The dose is 200 mg daily") is None
    assert check_output_safety("The daily dose of 200 mg is listed.") is None


def test_round2_narrowing_hurt_ask_pharmacist_passes():
    assert (
        check_output_safety("It won't hurt to ask your pharmacist.")
        is not None
    )
    # ... while hurt with a medical object still blocks.
    assert check_output_safety("It won't hurt you") is None
    assert check_output_safety("It will not hurt you") is None
    assert check_output_safety("It does not hurt to combine them") is None
