from candidate.tests.ui_tests.base_ui_test import BaseUiTest


class TestDashboardUi(BaseUiTest):

    def test_dashboard_loads_with_findings(self):
        self.dashboard_page.open_dashboard()
        self.dashboard_page.wait_until_loaded()

        assert self.dashboard_page.findings_rows().count() > 0

    def test_change_finding_status_through_dropdown_and_verify_change_is_reflected(
        self,
        created_finding,
    ):
        self.dashboard_page.open_dashboard()
        self.dashboard_page.wait_until_loaded()
        self.dashboard_page.wait_for_status_text(created_finding["id"], "open")

        self.dashboard_page.change_finding_status(created_finding["id"], "confirmed")
        self.dashboard_page.wait_for_success_message(created_finding["id"], "confirmed")
        self.dashboard_page.wait_for_status_text(created_finding["id"], "confirmed")

    def test_filter_findings_by_status(self, api_clients, created_finding):
        api_clients["findings_api"].update_status(created_finding["id"], {"status": "confirmed"})

        self.dashboard_page.open_dashboard()
        self.dashboard_page.wait_until_loaded()
        self.dashboard_page.filter_by_status("confirmed")
        self.dashboard_page.wait_for_only_filtered_status_visible("confirmed")
