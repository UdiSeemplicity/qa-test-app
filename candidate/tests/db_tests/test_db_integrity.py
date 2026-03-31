from tests.db_tests.base_db_test import BaseDbTest


class TestDbIntegrity(BaseDbTest):
    def test_dismiss_finding_via_api_sets_is_dismissed_true_in_db(self, created_finding):
        self.api_clients["findings_api"].dismiss_finding(created_finding["id"])

        db_row = self.db_client.get_finding_by_id(created_finding["id"])

        assert db_row is not None
        assert db_row["is_dismissed"] is True

    def test_update_finding_status_via_api_updates_db_state(self, created_finding):
        self.api_clients["findings_api"].update_status(
            created_finding["id"],
            {"status": "confirmed", "notes": "db integrity verification"},
        )

        db_row = self.db_client.get_finding_by_id(created_finding["id"])

        assert db_row["status"] == "confirmed"
        assert db_row["notes"] == "db integrity verification"

    def test_resolve_finding_via_api_sets_resolved_at_in_db(self, created_finding):
        self.api_clients["findings_api"].update_status(created_finding["id"], {"status": "confirmed"})
        self.api_clients["findings_api"].update_status(created_finding["id"], {"status": "in_progress"})
        self.api_clients["findings_api"].update_status(created_finding["id"], {"status": "resolved"})

        db_row = self.db_client.get_finding_by_id(created_finding["id"])

        assert db_row["status"] == "resolved"
        assert db_row["resolved_at"] is not None

    def test_deactivate_asset_via_api_sets_is_active_false_in_db(self, created_asset):
        self.api_clients["assets_api"].deactivate_asset(created_asset["id"])

        db_row = self.db_client.get_asset_by_id(created_asset["id"])

        assert db_row is not None
        assert db_row["is_active"] is False
