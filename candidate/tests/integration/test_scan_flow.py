import time

from candidate.test_support.data import build_scan_payload
from candidate.test_support.extract import extract_items


def test_scan_flow_creates_findings(scanner_client, api_client, test_asset, valid_vulnerability_id):
    asset_id = test_asset["id"]

    scan_payload = build_scan_payload(asset_id=asset_id, vulnerability_ids=[valid_vulnerability_id])
    scan_resp = scanner_client.run_scan(scan_payload)
    assert scan_resp.status_code in (200, 201), scan_resp.text

    deadline = time.time() + 10.0
    last_body = None
    items = []
    while time.time() < deadline:
        list_resp = api_client.list_findings(params={"asset_id": asset_id, "page": 1, "per_page": 50})
        assert list_resp.status_code == 200, list_resp.text
        last_body = list_resp.json()
        items = [i for i in extract_items(last_body) if i.get("asset_id") == asset_id]
        if items:
            break
        time.sleep(0.25)

    assert items, f"No findings became visible for asset_id={asset_id} within timeout. Last response: {last_body}"

    assert any(
        item.get("vulnerability_id") == valid_vulnerability_id for item in items
    ), "Expected vulnerability not found in findings"

    finding_id = items[0].get("id") or items[0].get("finding_id")
    assert finding_id is not None, f"Finding id missing from response item: {items[0]}"

    update_resp = api_client.update_finding_status(int(finding_id), status="confirmed", notes="Integration test")
    assert update_resp.status_code in (200, 204), update_resp.text

    get_resp = api_client.get_finding(int(finding_id))
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json().get("status") == "confirmed"
