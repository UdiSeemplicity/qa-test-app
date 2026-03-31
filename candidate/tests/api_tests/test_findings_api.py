from tests.api_tests.base_api_test import BaseApiTest


class TestFindingsApi(BaseApiTest):
    def test_list_findings_returns_paginated_payload(self):
        response = self.findings_api.list_findings(per_page=10)

        assert "items" in response
        assert "total" in response
        assert "page" in response
        assert "per_page" in response
        assert isinstance(response["items"], list)

    def test_get_finding_returns_detail_for_existing_record(self, created_finding):
        response = self.findings_api.get_finding(created_finding["id"])

        assert response["id"] == created_finding["id"]
        assert response["asset_id"] == created_finding["asset_id"]
        assert response["vulnerability_id"] == created_finding["vulnerability_id"]
        assert "vulnerability" in response
        assert "asset_hostname" in response

    def test_get_finding_returns_data_consistent_with_db(self, db_client, created_finding):
        response = self.findings_api.get_finding(created_finding["id"])
        db_row = db_client.get_finding_detail_by_id(created_finding["id"])

        assert response["id"] == db_row["id"]
        assert response["asset_id"] == db_row["asset_id"]
        assert response["vulnerability_id"] == db_row["vulnerability_id"]
        assert response["status"] == db_row["status"]
        assert response["scanner"] == db_row["scanner"]
        assert response["notes"] == db_row["notes"]
        assert response["is_dismissed"] == db_row["is_dismissed"]
        assert response["asset_hostname"] == db_row["asset_hostname"]
        assert response["vulnerability"]["id"] == db_row["vuln_id"]
        assert response["vulnerability"]["cve_id"] == db_row["cve_id"]
        assert response["vulnerability"]["title"] == db_row["title"]
        assert response["vulnerability"]["severity"] == db_row["severity"]

    def test_create_finding_creates_open_finding(self, created_asset, seed_vulnerability, unique_suffix):
        payload = {
            "asset_id": created_asset["id"],
            "vulnerability_id": seed_vulnerability["id"],
            "scanner": "Nessus",
            "notes": f"happy path create {unique_suffix}",
        }

        response = self.findings_api.create_finding(payload)

        assert response["asset_id"] == payload["asset_id"]
        assert response["vulnerability_id"] == payload["vulnerability_id"]
        assert response["status"] == "open"
        assert response["is_dismissed"] is False
        assert response["resolved_at"] is None

    def test_create_finding_persists_correct_data_in_db(self, db_client, created_asset, seed_vulnerability, unique_suffix):
        payload = {
            "asset_id": created_asset["id"],
            "vulnerability_id": seed_vulnerability["id"],
            "scanner": "Nessus",
            "notes": f"db-check-create-{unique_suffix}",
        }

        response = self.findings_api.create_finding(payload)
        db_row = db_client.get_finding_by_id(response["id"])

        assert db_row is not None
        assert db_row["asset_id"] == payload["asset_id"]
        assert db_row["vulnerability_id"] == payload["vulnerability_id"]
        assert db_row["status"] == "open"
        assert db_row["scanner"] == payload["scanner"]
        assert db_row["notes"] == payload["notes"]
        assert db_row["is_dismissed"] is False

    def test_list_findings_returns_data_consistent_with_db(self, db_client):
        response = self.findings_api.list_findings(page=1, per_page=10)
        db_response = db_client.get_findings_page(page=1, per_page=10)

        assert response["total"] == db_response["total"]
        assert response["page"] == db_response["page"]
        assert response["per_page"] == db_response["per_page"]
        assert [item["id"] for item in response["items"]] == [item["id"] for item in db_response["items"]]

    def test_list_findings_with_filters_returns_data_consistent_with_db(self, db_client, created_finding):
        self.findings_api.update_status(created_finding["id"], {"status": "confirmed"})

        response = self.findings_api.list_findings(
            page=1,
            per_page=20,
            status="confirmed",
            asset_id=created_finding["asset_id"],
        )
        db_response = db_client.get_findings_page(
            page=1,
            per_page=20,
            status="confirmed",
            asset_id=created_finding["asset_id"],
        )

        assert response["total"] == db_response["total"]
        assert [item["id"] for item in response["items"]] == [item["id"] for item in db_response["items"]]

    def test_update_finding_status_updates_status_and_notes(self, created_finding):
        response = self.findings_api.update_status(
            created_finding["id"],
            {"status": "confirmed", "notes": "validated by automation"},
        )

        assert response["id"] == created_finding["id"]
        assert response["status"] == "confirmed"
        assert response["notes"] == "validated by automation"

    def test_update_finding_status_is_persisted_in_db(self, db_client, created_finding):
        self.findings_api.update_status(
            created_finding["id"],
            {"status": "confirmed", "notes": "db persistence check"},
        )

        db_row = db_client.get_finding_by_id(created_finding["id"])

        assert db_row["status"] == "confirmed"
        assert db_row["notes"] == "db persistence check"

    def test_update_finding_status_to_resolved_sets_resolved_at(self, created_finding):
        self.findings_api.update_status(created_finding["id"], {"status": "confirmed"})
        self.findings_api.update_status(created_finding["id"], {"status": "in_progress"})

        response = self.findings_api.update_status(created_finding["id"], {"status": "resolved"})

        assert response["status"] == "resolved"
        assert response["resolved_at"] is not None

    def test_resolved_status_sets_resolved_at_in_db(self, db_client, created_finding):
        self.findings_api.update_status(created_finding["id"], {"status": "confirmed"})
        self.findings_api.update_status(created_finding["id"], {"status": "in_progress"})
        self.findings_api.update_status(created_finding["id"], {"status": "resolved"})

        db_row = db_client.get_finding_by_id(created_finding["id"])

        assert db_row["status"] == "resolved"
        assert db_row["resolved_at"] is not None

    def test_dismiss_finding_hides_finding_from_list(self, created_finding):
        result = self.findings_api.dismiss_finding(created_finding["id"])
        listed = self.findings_api.list_findings(asset_id=created_finding["asset_id"], per_page=100)

        assert result is None
        assert all(item["id"] != created_finding["id"] for item in listed["items"])

    def test_dismiss_finding_sets_db_flag(self, db_client, created_finding):
        self.findings_api.dismiss_finding(created_finding["id"])

        db_row = db_client.get_finding_by_id(created_finding["id"])

        assert db_row["is_dismissed"] is True

    def test_search_findings_by_notes_returns_matching_records(self, created_finding):
        response = self.findings_api.search(created_finding["notes"])

        assert isinstance(response, list)
        assert any(item["finding_id"] == created_finding["id"] for item in response)

    def test_search_findings_returns_data_consistent_with_db(self, db_client, created_finding):
        response = self.findings_api.search(created_finding["notes"])
        db_response = db_client.search_findings_from_db(created_finding["notes"])

        assert response == db_response

    def test_search_findings_by_hostname_returns_matching_records(
        self,
        created_finding,
        created_asset,
    ):
        response = self.findings_api.search(created_asset["hostname"])

        assert isinstance(response, list)
        assert any(item["finding_id"] == created_finding["id"] for item in response)

    def test_search_findings_by_cve_returns_matching_records(
        self,
        created_finding,
        seed_vulnerability,
    ):
        response = self.findings_api.search(seed_vulnerability["cve_id"])

        assert isinstance(response, list)
        assert any(item["finding_id"] == created_finding["id"] for item in response)

    def test_create_finding_with_invalid_asset_returns_error_message(self, seed_vulnerability, unique_suffix):
        payload = {
            "asset_id": 999999,
            "vulnerability_id": seed_vulnerability["id"],
            "scanner": "pytest",
            "notes": f"negative invalid asset {unique_suffix}",
        }

        response = self.findings_api.create_finding(payload, is_negative=True)

        assert "Asset not found" in response

    def test_create_finding_with_invalid_vulnerability_returns_error_message(self, created_asset, unique_suffix):
        payload = {
            "asset_id": created_asset["id"],
            "vulnerability_id": 999999,
            "scanner": "pytest",
            "notes": f"negative invalid vulnerability {unique_suffix}",
        }

        response = self.findings_api.create_finding(payload, is_negative=True)

        assert "Vulnerability not found" in response

    def test_update_status_with_invalid_value_returns_error_message(self, created_finding):
        response = self.findings_api.update_status(
            created_finding["id"],
            {"status": "closed"},
            is_negative=True,
        )

        assert "Invalid status" in response

    def test_get_nonexistent_finding_returns_error_message(self):
        response = self.findings_api.get_finding(999999, is_negative=True)

        assert "Finding not found" in response

    def test_search_with_empty_query_returns_empty_list(self):
        response = self.findings_api.search("")

        assert response == []

    def test_search_findings_is_not_vulnerable_to_sql_injection(self, db_client):
        malicious_query = "' OR '1'='1"

        api_response = self.findings_api.search(malicious_query)
        db_response = db_client.search_findings_from_db(malicious_query)

        assert api_response == db_response
