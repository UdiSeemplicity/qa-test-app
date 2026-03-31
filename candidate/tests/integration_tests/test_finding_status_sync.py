from tests.integration_tests.base_integration_test import BaseIntegrationTest


class TestFindingStatusSync(BaseIntegrationTest):
    def test_update_finding_status_via_api_verifies_db_state_matches(self, created_finding):
        response = self.api_clients["findings_api"].update_status(
            created_finding["id"],
            {"status": "confirmed", "notes": "integration verification"},
        )

        db_row = self.db_client.get_finding_by_id(created_finding["id"])

        assert response["status"] == "confirmed"
        assert response["notes"] == "integration verification"
        assert db_row["status"] == "confirmed"
        assert db_row["notes"] == "integration verification"

    def test_resolving_finding_via_api_verifies_resolved_timestamp_in_db(self, created_finding):
        self.api_clients["findings_api"].update_status(created_finding["id"], {"status": "confirmed"})
        self.api_clients["findings_api"].update_status(created_finding["id"], {"status": "in_progress"})
        response = self.api_clients["findings_api"].update_status(
            created_finding["id"],
            {"status": "resolved", "notes": "resolved by integration flow"},
        )

        db_row = self.db_client.get_finding_by_id(created_finding["id"])

        assert response["status"] == "resolved"
        assert response["resolved_at"] is not None
        assert db_row["status"] == "resolved"
        assert db_row["resolved_at"] is not None
