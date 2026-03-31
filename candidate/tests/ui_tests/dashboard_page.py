from __future__ import annotations

from playwright.sync_api import expect

from tests.ui_tests.base_page import BasePage


class DashboardPage(BasePage):
    URL = "http://localhost:8000/"

    HEADER = "h1"
    FINDINGS_TABLE_ROWS = "#findings-table tr"
    ASSETS_TABLE_ROWS = "#assets-table tr"
    FINDINGS_MESSAGE = "#findings-message"
    FILTER_STATUS = "#filter-status"
    REFRESH_BUTTON = "button:has-text('Refresh')"
    TOTAL_COUNT = "#total-count"

    def open_dashboard(self) -> None:
        self.open(self.URL)

    def wait_until_loaded(self) -> None:
        expect(self.page).to_have_title("Vulnerability Dashboard")
        expect(self.locator(self.HEADER)).to_have_text("Vulnerability Dashboard")
        expect(self.locator(self.TOTAL_COUNT)).not_to_have_text("-")
        expect(self.locator(self.FINDINGS_TABLE_ROWS).first).to_be_visible()

    def findings_rows(self):
        return self.locator(self.FINDINGS_TABLE_ROWS)

    def status_filter(self):
        return self.locator(self.FILTER_STATUS)

    def filter_by_status(self, status: str) -> None:
        with self.page.expect_response(
            lambda response: response.request.method == "GET"
            and "/findings?" in response.url
            and f"status={status}" in response.url
            and response.ok
        ):
            self.select_option(self.FILTER_STATUS, status)

        # self.wait_for_findings_table_update()

    def refresh_findings(self) -> None:
        self.click(self.REFRESH_BUTTON)

    def row_by_finding_id(self, finding_id: int):
        return self.page.locator("#findings-table tr").filter(has_text=f"#{finding_id}")

    def status_badge_for_finding(self, finding_id: int):
        return self.row_by_finding_id(finding_id).locator(".status")

    def status_select_for_finding(self, finding_id: int):
        return self.row_by_finding_id(finding_id).locator(".status-select")

    def change_finding_status(self, finding_id: int, status: str) -> None:
        self.status_select_for_finding(finding_id).select_option(status)

    def wait_for_success_message(self, finding_id: int, status: str) -> None:
        expected_text = f"Finding #{finding_id} updated to {status}"
        expect(self.locator(self.FINDINGS_MESSAGE)).to_contain_text(expected_text)

    def get_status_text(self, finding_id: int) -> str:
        return (self.status_badge_for_finding(finding_id).text_content() or "").strip()

    def wait_for_status_text(self, finding_id: int, expected_status: str) -> None:
        expect(self.status_badge_for_finding(finding_id)).to_have_text(expected_status.replace("_", " "))

    def wait_for_only_filtered_status_visible(self, expected_status: str) -> None:
        rows = self.findings_rows()
        expect(rows.first).to_be_visible()
        status_badges = rows.locator(".status")
        count = status_badges.count()
        expected_text = expected_status.replace("_", " ")
        for index in range(count):
            expect(status_badges.nth(index)).to_have_text(expected_text)
