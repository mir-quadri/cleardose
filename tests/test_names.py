from cleardose.names import normalize, parse, same_drug


def test_brand_resolves_to_canonical():
    assert parse("Advil").canonical == "ibuprofen"
    assert parse("Coumadin").canonical == "warfarin"


def test_normalize_strips_dose_and_form():
    assert normalize("Ibuprofen 200 mg Tablets") == "ibuprofen"
    assert normalize("  WARFARIN   Sodium ") == "warfarin"


def test_same_drug_brand_and_generic():
    assert same_drug("Advil", "ibuprofen")
    assert not same_drug("ibuprofen", "warfarin")


def test_unknown_name_keeps_spelling():
    assert parse("meloxicam").canonical == "meloxicam"


def test_normalize_strips_trailing_punctuation():
    # S2 fix pass: punctuated input resolves.
    assert normalize("Ibuprofen,") == "ibuprofen"
    assert parse("Advil.").canonical == "ibuprofen"
    assert normalize("Warfarin;") == "warfarin"


def test_normalize_strips_parenthetical_dose():
    # S2 fix pass: parenthetical dose/form content is dropped.
    assert parse("ibuprofen (200 mg)").canonical == "ibuprofen"
    assert normalize("Ibuprofen (200 mg)") == "ibuprofen"


def test_advil_pm_not_mapped_to_ibuprofen():
    # S2 HARD RULE: exact-match-only alias resolution. "Advil PM"
    # has an extra ingredient, so it must NOT resolve to ibuprofen.
    assert parse("Advil PM").canonical != "ibuprofen"
    assert parse("Advil PM").canonical == "advil pm"


def test_parenthetical_modifier_not_stripped_to_bare_drug():
    # S2 round-2 fix: parenthetical removal is dose/form-only.
    # "PM", "with codeine", "with diphenhydramine" are meaningful
    # modifiers, not dose/form — they must be LEFT INTACT so the
    # name does NOT silently resolve to a single-ingredient drug.
    # Fails on the old code (which stripped all parentheticals).
    assert parse("Advil (PM)").canonical != "ibuprofen"
    assert parse("acetaminophen (with codeine)").canonical != "acetaminophen"
    assert parse("ibuprofen (with diphenhydramine)").canonical != "ibuprofen"


def test_nested_parens_left_whole_no_stray_paren():
    # S2 round-2 fix: nested parens are never partially stripped.
    # Old code turned "ibuprofen (200 mg (extra))" into
    # "ibuprofen )" (stray paren) resolving to bare ibuprofen.
    normalized = normalize("ibuprofen (200 mg (extra))")
    assert parse("ibuprofen (200 mg (extra))").canonical != "ibuprofen"
    assert normalized != "ibuprofen )"
    # No STRAY paren: parens remain balanced (the whole group was
    # left intact), unlike the old partial strip "ibuprofen )".
    assert normalized.count("(") == normalized.count(")")
    assert normalized == "ibuprofen (200 mg (extra))"
    # Dose/form-only parens still resolve (no regression).
    assert parse("ibuprofen (200 mg)").canonical == "ibuprofen"
