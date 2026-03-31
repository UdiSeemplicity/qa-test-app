from tests.api_tests.base_api_test import BaseApiTest


class TestScansApi(BaseApiTest):
    def test_list_scans_returns_paginated_payload(self):
        response = self.scans_api.list_scans(per_page=10)

        assert "items" in response
        assert "total" in response
        assert "page" in response
        assert "per_page" in response
        assert isinstance(response["items"], list)

    def test_create_scan_creates_completed_scan(self, created_asset, seed_vulnerability):
        payload = {
            "asset_id": created_asset["id"],
            "scanner_name": "Nessus",
            "vulnerability_ids": [seed_vulnerability["id"]],
        }

        response = self.scans_api.create_scan(payload)

        assert response["asset_id"] == created_asset["id"]
        assert response["scanner_name"] == "Nessus"
        assert response["status"] == "completed"
        assert response["findings_count"] >= 1
        assert response["completed_at"] is not None

    def test_create_scan_persists_scan_record_and_findings_count_in_db(
        self,
        db_client,
        created_asset,
        seed_vulnerability,
    ):
        vulnerability_ids = [seed_vulnerability["id"]]
        payload = {
            "asset_id": created_asset["id"],
            "scanner_name": "Nessus",
            "vulnerability_ids": vulnerability_ids,
        }

        response = self.scans_api.create_scan(payload)
        scan_row = db_client.get_scan_by_id(response["id"])
        findings_count = db_client.count_findings_for_asset_and_vulnerabilities(
            created_asset["id"],
            vulnerability_ids,
        )

        assert scan_row is not None
        assert scan_row["asset_id"] == payload["asset_id"]
        assert scan_row["scanner_name"] == payload["scanner_name"]
        assert scan_row["status"] == "completed"
        assert scan_row["completed_at"] is not None
        assert scan_row["findings_count"] == response["findings_count"]
        assert findings_count >= response["findings_count"]

    def test_list_scans_returns_data_consistent_with_db(self, db_client):
        response = self.scans_api.list_scans(page=1, per_page=10)
        db_response = db_client.list_scans_from_db(page=1, per_page=10)

        assert response["total"] == db_response["total"]
        assert response["page"] == db_response["page"]
        assert response["per_page"] == db_response["per_page"]
        assert [item["id"] for item in response["items"]] == [item["id"] for item in db_response["items"]]

    def test_list_scans_can_filter_by_asset_id(self, created_asset, seed_vulnerability):
        created_scan = self.scans_api.create_scan(
            {
                "asset_id": created_asset["id"],
                "scanner_name": "Qualys",
                "vulnerability_ids": [seed_vulnerability["id"]],
            }
        )

        response = self.scans_api.list_scans(asset_id=created_asset["id"], per_page=50)

        assert any(item["id"] == created_scan["id"] for item in response["items"])

    def test_list_scans_filter_returns_data_consistent_with_db(self, db_client, created_asset, seed_vulnerability):
        self.scans_api.create_scan(
            {
                "asset_id": created_asset["id"],
                "scanner_name": "Qualys",
                "vulnerability_ids": [seed_vulnerability["id"]],
            }
        )

        response = self.scans_api.list_scans(asset_id=created_asset["id"], per_page=50)
        db_response = db_client.list_scans_from_db(asset_id=created_asset["id"], per_page=50)

        assert response["total"] == db_response["total"]
        assert [item["id"] for item in response["items"]] == [item["id"] for item in db_response["items"]]

    def test_get_scan_returns_existing_scan(self, created_asset, seed_vulnerability):
        created_scan = self.scans_api.create_scan(
            {
                "asset_id": created_asset["id"],
                "scanner_name": "OpenVAS",
                "vulnerability_ids": [seed_vulnerability["id"]],
            }
        )

        response = self.scans_api.get_scan(created_scan["id"])

        assert response["id"] == created_scan["id"]
        assert response["asset_id"] == created_scan["asset_id"]
        assert response["scanner_name"] == created_scan["scanner_name"]

    def test_get_scan_returns_data_consistent_with_db(self, db_client, created_asset, seed_vulnerability):
        created_scan = self.scans_api.create_scan(
            {
                "asset_id": created_asset["id"],
                "scanner_name": "OpenVAS",
                "vulnerability_ids": [seed_vulnerability["id"]],
            }
        )

        response = self.scans_api.get_scan(created_scan["id"])
        db_row = db_client.get_scan_by_id(created_scan["id"])

        assert response["id"] == db_row["id"]
        assert response["asset_id"] == db_row["asset_id"]
        assert response["scanner_name"] == db_row["scanner_name"]
        assert response["status"] == db_row["status"]
        assert response["findings_count"] == db_row["findings_count"]

    def test_create_scan_with_invalid_asset_returns_error_message(self, seed_vulnerability):
        payload = {
            "asset_id": 999999,
            "scanner_name": "Nessus",
            "vulnerability_ids": [seed_vulnerability["id"]],
        }

        response = self.scans_api.create_scan(payload, is_negative=True)

        assert "Asset not found or inactive" in response

    def test_get_nonexistent_scan_returns_error_message(self):
        response = self.scans_api.get_scan(999999, is_negative=True)

        assert "Scan not found" in response
