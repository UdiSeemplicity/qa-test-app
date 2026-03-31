from tests.integration_tests.base_integration_test import BaseIntegrationTest


class TestScanImportFlow(BaseIntegrationTest):
    def test_run_scan_via_scanner_service_creates_findings_in_dashboard_api(
        self,
        created_asset,
        seed_vulnerability,
    ):
        vulnerability_ids = [seed_vulnerability["id"]]
        initial_count = self.db_client.count_findings_for_asset_and_vulnerabilities(
            created_asset["id"],
            vulnerability_ids,
        )

        scan_response = self.api_clients["scans_api"].create_scan(
            {
                "asset_id": created_asset["id"],
                "scanner_name": "Nessus",
                "vulnerability_ids": vulnerability_ids,
            }
        )

        db_count = self.db_client.count_findings_for_asset_and_vulnerabilities(
            created_asset["id"],
            vulnerability_ids,
        )
        findings_response = self.api_clients["findings_api"].list_findings(
            asset_id=created_asset["id"],
            per_page=100,
        )

        assert scan_response["status"] == "completed"
        assert scan_response["findings_count"] == 1
        assert db_count == initial_count + 1
        assert any(
            item["asset_id"] == created_asset["id"] and item["vulnerability_id"] == seed_vulnerability["id"]
            for item in findings_response["items"]
        )
