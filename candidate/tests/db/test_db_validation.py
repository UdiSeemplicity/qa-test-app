from candidate.test_support.assertions import assert_status_code


def test_foreign_keys_valid_for_findings(db_client):
    rows = db_client.fetch_all(
        """
        SELECT f.id as finding_id, a.id as asset_id, v.id as vulnerability_id
        FROM findings f
        JOIN assets a ON a.id = f.asset_id
        JOIN vulnerabilities v ON v.id = f.vulnerability_id
        LIMIT 20
        """
    )
    assert len(rows) > 0


def test_db_state_after_status_update(api_client, db_client, test_finding):
    finding_id = test_finding["id"]

    resp = api_client.update_finding_status(finding_id, status="resolved", notes="resolved via db test")
    assert_status_code(resp, (200, 204))

    row = db_client.fetch_one("SELECT status, resolved_at FROM findings WHERE id=%s", (finding_id,))
    assert row is not None
    assert row["status"] == "resolved"


def test_db_state_after_dismiss(api_client, db_client, test_finding):
    finding_id = test_finding["id"]

    resp = api_client.dismiss_finding(finding_id)
    assert_status_code(resp, (200, 204))

    row = db_client.fetch_one("SELECT is_dismissed FROM findings WHERE id=%s", (finding_id,))
    assert row is not None
    assert row["is_dismissed"] is True
