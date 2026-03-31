from tests.api_tests.base_api_test import BaseApiTest


class TestHealthApi(BaseApiTest):
    def test_dashboard_health_returns_success(self):
        response = self.dashboard_health_api.get_health()

        assert response is not None

    def test_scanner_health_returns_success(self):
        response = self.scanner_health_api.get_health()

        assert response is not None
