from __future__ import annotations

import pytest


class BaseDbTest:
    @pytest.fixture(autouse=True)
    def setup_db_resources(self, db_client, api_clients) -> None:
        self.db_client = db_client
        self.api_clients = api_clients
