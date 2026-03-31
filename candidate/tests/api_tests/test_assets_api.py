from tests.api_tests.base_api_test import BaseApiTest


class TestAssetsApi(BaseApiTest):
    def test_list_assets_returns_paginated_payload(self):
        response = self.assets_api.list_assets(per_page=10)

        assert "items" in response
        assert "total" in response
        assert "page" in response
        assert "per_page" in response
        assert "pages" in response
        assert isinstance(response["items"], list)

    def test_list_assets_can_filter_by_environment(self):
        response = self.assets_api.list_assets(environment="production", per_page=50)

        assert all(item["environment"] == "production" for item in response["items"])

    def test_list_assets_can_filter_by_asset_type(self):
        response = self.assets_api.list_assets(asset_type="server", per_page=50)

        assert all(item["asset_type"] == "server" for item in response["items"])

    def test_list_assets_returns_data_consistent_with_db(self, db_client):
        response = self.assets_api.list_assets(page=1, per_page=10)
        db_response = db_client.list_assets_from_db(page=1, per_page=10)

        assert response["total"] == db_response["total"]
        assert response["page"] == db_response["page"]
        assert response["per_page"] == db_response["per_page"]
        assert response["pages"] == db_response["pages"]
        assert [item["id"] for item in response["items"]] == [item["id"] for item in db_response["items"]]

    def test_list_assets_filter_returns_data_consistent_with_db(self, db_client):
        response = self.assets_api.list_assets(environment="production", asset_type="server", per_page=50)
        db_response = db_client.list_assets_from_db(environment="production", asset_type="server", per_page=50)

        assert response["total"] == db_response["total"]
        assert [item["id"] for item in response["items"]] == [item["id"] for item in db_response["items"]]

    def test_get_asset_returns_existing_asset(self, seed_asset):
        response = self.assets_api.get_asset(seed_asset["id"])

        assert response["id"] == seed_asset["id"]
        assert response["hostname"] == seed_asset["hostname"]

    def test_get_asset_returns_data_consistent_with_db(self, db_client, seed_asset):
        response = self.assets_api.get_asset(seed_asset["id"])
        db_row = db_client.get_asset_by_id(seed_asset["id"])

        assert response["id"] == db_row["id"]
        assert response["hostname"] == db_row["hostname"]
        assert response["ip_address"] == db_row["ip_address"]
        assert response["asset_type"] == db_row["asset_type"]
        assert response["environment"] == db_row["environment"]
        assert response["os"] == db_row["os"]
        assert response["is_active"] == db_row["is_active"]

    def test_create_asset_creates_active_asset(self, unique_suffix):
        payload = {
            "hostname": f"asset-create-{unique_suffix}",
            "ip_address": "10.0.10.10",
            "asset_type": "server",
            "environment": "development",
            "os": "Ubuntu 22.04",
        }

        response = self.assets_api.create_asset(payload)

        assert response["hostname"] == payload["hostname"]
        assert response["asset_type"] == payload["asset_type"]
        assert response["environment"] == payload["environment"]
        assert response["is_active"] is True

    def test_create_asset_persists_correct_data_in_db(self, db_client, unique_suffix):
        payload = {
            "hostname": f"asset-db-{unique_suffix}",
            "ip_address": "10.0.10.12",
            "asset_type": "server",
            "environment": "development",
            "os": "Ubuntu 22.04",
        }

        response = self.assets_api.create_asset(payload)
        db_row = db_client.get_asset_by_id(response["id"])

        assert db_row is not None
        assert db_row["hostname"] == payload["hostname"]
        assert db_row["ip_address"] == payload["ip_address"]
        assert db_row["asset_type"] == payload["asset_type"]
        assert db_row["environment"] == payload["environment"]
        assert db_row["os"] == payload["os"]
        assert db_row["is_active"] is True

    def test_update_asset_updates_fields(self, created_asset):
        response = self.assets_api.update_asset(
            created_asset["id"],
            {"hostname": f'{created_asset["hostname"]}-updated', "environment": "production"},
        )

        assert response["hostname"].endswith("-updated")
        assert response["environment"] == "production"

    def test_update_asset_is_persisted_in_db(self, db_client, created_asset):
        response = self.assets_api.update_asset(
            created_asset["id"],
            {"hostname": f'{created_asset["hostname"]}-db-updated', "environment": "production"},
        )

        db_row = db_client.get_asset_by_id(created_asset["id"])

        assert db_row["hostname"] == response["hostname"]
        assert db_row["environment"] == "production"

    def test_deactivate_asset_makes_asset_inaccessible(self, created_asset):
        result = self.assets_api.deactivate_asset(created_asset["id"])
        error = self.assets_api.get_asset(created_asset["id"], is_negative=True)

        assert result is None
        assert "Asset not found" in error

    def test_deactivate_asset_sets_inactive_flag_in_db(self, db_client, created_asset):
        self.assets_api.deactivate_asset(created_asset["id"])

        db_row = db_client.get_asset_by_id(created_asset["id"])

        assert db_row["is_active"] is False

    def test_create_asset_with_invalid_asset_type_returns_error_message(self, unique_suffix):
        payload = {
            "hostname": f"asset-invalid-type-{unique_suffix}",
            "ip_address": "10.0.10.11",
            "asset_type": "database",
            "environment": "development",
            "os": "Ubuntu 22.04",
        }

        response = self.assets_api.create_asset(payload, is_negative=True)

        assert "string_pattern_mismatch" in response or "asset_type" in response

    def test_get_nonexistent_asset_returns_error_message(self):
        response = self.assets_api.get_asset(999999, is_negative=True)

        assert "Asset not found" in response
