from candidate.test_support.assertions import assert_status_code
from candidate.test_support.extract import extract_items


def test_search_findings_by_known_cve(api_client):
    query = "CVE-2021-44228"
    resp = api_client.search_findings(query)
    assert_status_code(resp, (200,))
    data = resp.json()
    assert isinstance(data, (list, dict))

    items = extract_items(data)
    assert items, "Expected at least one search result"
    for item in items[:5]:
        assert "finding_id" in item or "id" in item
        assert item.get("cve_id") == query


def test_search_findings_by_hostname_fragment(api_client):
    query = "prod-web"
    resp = api_client.search_findings(query)
    assert_status_code(resp, (200,))
    data = resp.json()
    assert isinstance(data, (list, dict))

    items = extract_items(data)
    assert items, "Expected at least one search result"
    for item in items[:5]:
        assert "finding_id" in item or "id" in item
        assert "hostname" in item
        assert query.lower() in str(item["hostname"]).lower()
