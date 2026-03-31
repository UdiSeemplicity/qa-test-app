from __future__ import annotations

import pytest


class BaseIntegrationTest:
    @pytest.fixture(autouse=True)
    def setup_integration_resources(self, db_client, api_clients) -> None:
        self.db_client = db_client
        self.api_clients = api_clients
