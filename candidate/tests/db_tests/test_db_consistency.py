from tests.db_tests.base_db_test import BaseDbTest


class TestDbConsistency(BaseDbTest):
    def test_findings_have_valid_asset_and_vulnerability_references(self):
        orphan_counts = self.db_client.fetch_one(
            """
            SELECT
                COUNT(*) FILTER (WHERE a.id IS NULL) AS missing_assets,
                COUNT(*) FILTER (WHERE v.id IS NULL) AS missing_vulnerabilities
            FROM findings f
            LEFT JOIN assets a ON f.asset_id = a.id
            LEFT JOIN vulnerabilities v ON f.vulnerability_id = v.id
            """
        )

        assert orphan_counts["missing_assets"] == 0
        assert orphan_counts["missing_vulnerabilities"] == 0

    def test_scans_have_valid_asset_references(self):
        result = self.db_client.fetch_one(
            """
            SELECT COUNT(*) AS missing_assets
            FROM scans s
            LEFT JOIN assets a ON s.asset_id = a.id
            WHERE a.id IS NULL
            """
        )

        assert result["missing_assets"] == 0

    def test_findings_reference_consistent_asset_and_vulnerability_data(self):
        rows = self.db_client.fetch_all(
            """
            SELECT
                f.id,
                f.asset_id,
                f.vulnerability_id,
                a.hostname,
                v.cve_id,
                v.severity
            FROM findings f
            JOIN assets a ON f.asset_id = a.id
            JOIN vulnerabilities v ON f.vulnerability_id = v.id
            LIMIT 50
            """
        )

        assert rows, "Expected findings joined to assets and vulnerabilities"
        assert all(row["asset_id"] is not None for row in rows)
        assert all(row["vulnerability_id"] is not None for row in rows)
        assert all(row["hostname"] for row in rows)
        assert all(row["cve_id"] for row in rows)
        assert all(row["severity"] for row in rows)

    def test_no_findings_reference_inactive_or_missing_assets_after_deactivation(self, created_asset, seed_vulnerability):
        created_finding = self.api_clients["findings_api"].create_finding(
            {
                "asset_id": created_asset["id"],
                "vulnerability_id": seed_vulnerability["id"],
                "scanner": "pytest",
                "notes": "db consistency check",
            }
        )
        self.api_clients["assets_api"].deactivate_asset(created_asset["id"])

        row = self.db_client.fetch_one(
            """
            SELECT f.id, f.asset_id, a.is_active
            FROM findings f
            LEFT JOIN assets a ON f.asset_id = a.id
            WHERE f.id = %s
            """,
            (created_finding["id"],),
        )

        assert row is not None
        assert row["asset_id"] == created_asset["id"]
        assert row["is_active"] is False
