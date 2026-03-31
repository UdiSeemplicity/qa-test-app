from tests.api_tests.base_api_test import BaseApiTest


class TestVulnerabilitiesApi(BaseApiTest):
    def test_list_vulnerabilities_returns_non_empty_list(self):
        response = self.vulnerabilities_api.list_vulnerabilities()

        assert isinstance(response, list)
        assert response
        assert "id" in response[0]
        assert "cve_id" in response[0]
        assert "severity" in response[0]

    def test_list_vulnerabilities_can_filter_by_severity(self):
        response = self.vulnerabilities_api.list_vulnerabilities(severity="critical")

        assert isinstance(response, list)
        assert all(item["severity"] == "critical" for item in response)

    def test_list_vulnerabilities_returns_data_consistent_with_db(self, db_client):
        response = self.vulnerabilities_api.list_vulnerabilities()
        db_response = db_client.list_vulnerabilities_from_db()

        assert [item["id"] for item in response] == [item["id"] for item in db_response]

    def test_list_vulnerabilities_filter_returns_data_consistent_with_db(self, db_client):
        response = self.vulnerabilities_api.list_vulnerabilities(severity="critical")
        db_response = db_client.list_vulnerabilities_from_db(severity="critical")

        assert [item["id"] for item in response] == [item["id"] for item in db_response]

    def test_get_vulnerability_returns_details_for_existing_record(self, seed_vulnerability):
        response = self.vulnerabilities_api.get_vulnerability(seed_vulnerability["id"])

        assert response["id"] == seed_vulnerability["id"]
        assert response["cve_id"] == seed_vulnerability["cve_id"]
        assert response["title"] == seed_vulnerability["title"]

    def test_get_vulnerability_returns_data_consistent_with_db(self, db_client, seed_vulnerability):
        response = self.vulnerabilities_api.get_vulnerability(seed_vulnerability["id"])
        db_row = db_client.get_vulnerability_by_id(seed_vulnerability["id"])

        assert response["id"] == db_row["id"]
        assert response["cve_id"] == db_row["cve_id"]
        assert response["title"] == db_row["title"]
        assert response["description"] == db_row["description"]
        assert response["severity"] == db_row["severity"]
        assert response["cvss_score"] == db_row["cvss_score"]

    def test_get_nonexistent_vulnerability_returns_error_message(self):
        response = self.vulnerabilities_api.get_vulnerability(999999, is_negative=True)

        assert "Vulnerability not found" in response
