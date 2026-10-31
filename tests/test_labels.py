from cleardose.labels import LabelRecord, OpenFDALabelClient, find_mentions


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status
        self.ok = status == 200

    def json(self):
        return self._payload


def _record():
    return LabelRecord(
        name="ibuprofen",
        sections={
            "drug_interactions": "Bleeding has been reported with warfarin.",
            "indications_and_usage": "Warfarin is mentioned here but it is not a flag.",
            "warnings": "Ask a doctor if you take warfarin.",
        },
    )


def test_find_mentions_only_interaction_and_warning_sections():
    mentions = find_mentions(_record(), ["warfarin"])
    assert {m.section for m in mentions} == {"drug_interactions", "warnings"}
    assert all("warfarin" in m.excerpt.lower() for m in mentions)


def test_openfda_client_parses_live_response(monkeypatch):
    import cleardose.labels as labels_module

    payload = {
        "results": [{
            "openfda": {"generic_name": ["ibuprofen"], "brand_name": ["Advil"]},
            "indications_and_usage": ["Relieves pain."],
            "drug_interactions": ["Warfarin interaction."],
        }]
    }
    monkeypatch.setattr(
        labels_module.requests, "get", lambda *a, **k: FakeResponse(payload)
    )
    lookup = OpenFDALabelClient().fetch("ibuprofen")
    assert lookup.found and lookup.record is not None
    assert lookup.record.data_source == "live openFDA"
    assert lookup.record.brand_names == ["Advil"]


def test_openfda_client_404_is_not_found_not_fabricated(monkeypatch):
    import cleardose.labels as labels_module

    monkeypatch.setattr(
        labels_module.requests, "get", lambda *a, **k: FakeResponse({}, status=404)
    )
    lookup = OpenFDALabelClient().fetch("nosuchdrug")
    assert not lookup.found and lookup.record is None


def test_openfda_fetch_normalises_before_query(monkeypatch):
    import cleardose.labels as labels_module

    seen = []

    def fake_get(url, params=None, timeout=None):
        seen.append(params["search"])
        return FakeResponse(
            {"results": [{"openfda": {"generic_name": ["ibuprofen"]}}]}
        )

    monkeypatch.setattr(labels_module.requests, "get", fake_get)
    client = OpenFDALabelClient()
    assert client.fetch("Ibuprofen 200 mg Tablets").found
    assert '"ibuprofen"' in seen[-1] and "Tablets" not in seen[-1]
    assert client.fetch("warfarin sodium").found
    assert '"warfarin"' in seen[-1] and "sodium" not in seen[-1]


def test_openfda_failed_lookups_are_not_cached(monkeypatch):
    import cleardose.labels as labels_module

    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(1)
        return FakeResponse({}, status=404)

    monkeypatch.setattr(labels_module.requests, "get", fake_get)
    client = OpenFDALabelClient()
    assert not client.fetch("nosuchdrug").found
    assert not client.fetch("nosuchdrug").found
    assert len(calls) == 2  # a failed lookup must not poison the cache
