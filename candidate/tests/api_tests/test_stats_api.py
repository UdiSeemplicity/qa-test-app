from decimal import Decimal

from tests.api_tests.base_api_test import BaseApiTest


class TestStatsApi(BaseApiTest):
    def test_get_summary_returns_expected_structure(self):
        response = self.stats_api.get_summary()

        assert "total_findings" in response
        assert "open_findings" in response
        assert "confirmed_findings" in response
        assert "in_progress_findings" in response
        assert "resolved_findings" in response
        assert "false_positive_findings" in response
        assert "by_severity" in response
        assert "by_environment" in response

    def test_get_risk_score_returns_expected_structure(self):
        response = self.stats_api.get_risk_score()

        assert "risk_score" in response
        assert "total_findings" in response
        assert "critical_count" in response
        assert "high_count" in response
        assert "medium_count" in response
        assert "low_count" in response
        assert "average_cvss" in response

    def test_summary_reflects_created_confirmed_finding(self, created_finding):
        self.findings_api.update_status(created_finding["id"], {"status": "confirmed"})

        summary = self.stats_api.get_summary()

        assert summary["confirmed_findings"] >= 1
        assert summary["total_findings"] >= summary["confirmed_findings"]

    def test_risk_score_values_have_expected_types(self):
        response = self.stats_api.get_risk_score()

        assert isinstance(response["risk_score"], (int, float))
        assert isinstance(response["average_cvss"], (int, float))
        assert response["risk_score"] >= 0
        assert response["average_cvss"] >= 0

    def test_get_summary_returns_values_consistent_with_db(self, db_client):
        api_response = self.stats_api.get_summary()
        db_response = db_client.get_summary_from_db()

        assert api_response == db_response

    def test_get_risk_score_returns_values_consistent_with_db(self, db_client):
        api_response = self.stats_api.get_risk_score()
        db_response = db_client.get_risk_score_from_db()

        assert api_response["total_findings"] == db_response["total_findings"]
        assert api_response["critical_count"] == db_response["critical_count"]
        assert api_response["high_count"] == db_response["high_count"]
        assert api_response["medium_count"] == db_response["medium_count"]
        assert api_response["low_count"] == db_response["low_count"]
        assert Decimal(str(api_response["average_cvss"])) == db_response["average_cvss"]
        assert Decimal(str(api_response["risk_score"])) == db_response["risk_score"]
