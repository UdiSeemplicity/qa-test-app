from __future__ import annotations

import pytest

from candidate.tests.ui_tests.dashboard_page import DashboardPage


class BaseUiTest:
    @pytest.fixture(autouse=True)
    def setup_pages(self, page) -> None:
        self.page = page
        self.dashboard_page = DashboardPage(page)
