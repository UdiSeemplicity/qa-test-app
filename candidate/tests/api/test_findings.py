import pytest

from candidate.test_support.assertions import (
    assert_finding_base,
    assert_finding_matches,
    assert_finding_status,
    assert_is_dict,
    assert_status_code,
)
from candidate.test_support.data import DEFAULT_SCANNER, build_finding_payload


def test_create_finding(api_client, valid_asset_id, valid_vulnerability_id):
    payload = build_finding_payload(
        asset_id=valid_asset_id,
        vulnerability_id=valid_vulnerability_id,
        notes="Created via API test",
    )

    finding_id = None
    try:
        resp = api_client.create_finding(payload)
        assert_status_code(resp, (200, 201))
        data = resp.json()

        assert_finding_base(data)
        assert_finding_matches(data, asset_id=valid_asset_id, vulnerability_id=valid_vulnerability_id)
        assert data.get("scanner") in (DEFAULT_SCANNER, None)

        finding_id = data["id"]
    finally:
        if finding_id is not None:
            api_client.dismiss_finding(finding_id)


def test_get_finding(api_client, test_finding):
    finding_id = test_finding["id"]

    resp = api_client.get_finding(finding_id)
    assert_status_code(resp, (200,))
    data = resp.json()

    assert_is_dict(data)
    assert data.get("id") == finding_id
    assert data.get("asset_id") == test_finding.get("asset_id")
    assert "vulnerability" in data or "vulnerability_id" in data


def test_update_finding_status(api_client, test_finding):
    finding_id = test_finding["id"]

    update_resp = api_client.update_finding_status(finding_id, status="confirmed", notes="Verified")
    assert_status_code(update_resp, (200, 204))

    get_resp = api_client.get_finding(finding_id)
    assert_status_code(get_resp, (200,))
    data = get_resp.json()
    assert_finding_status(data, "confirmed")


def test_dismiss_finding(api_client, test_finding):
    finding_id = test_finding["id"]

    dismiss_resp = api_client.dismiss_finding(finding_id)
    assert_status_code(dismiss_resp, (200, 204))

    get_resp = api_client.get_finding(finding_id)
    if get_resp.status_code == 200:
        data = get_resp.json()
        assert data.get("is_dismissed") is True
    else:
        # Some implementations remove/soft-hide dismissed findings from the details endpoint.
        assert get_resp.status_code in (404, 410)


def test_error_invalid_status(api_client, test_finding):
    finding_id = test_finding["id"]
    resp = api_client.update_finding_status(finding_id, status="not_a_real_status")
    assert_status_code(resp, (400, 422))


def test_error_non_existing_finding_id(api_client):
    resp = api_client.get_finding(9999999)
    assert_status_code(resp, (404,))


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"asset_id": "abc"},
        {"asset_id": 1},
        {"asset_id": 1, "vulnerability_id": None},
    ],
)
def test_error_invalid_payload(api_client, payload):
    resp = api_client.create_finding(payload)
    assert_status_code(resp, (400, 422))
