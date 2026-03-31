from __future__ import annotations

from playwright.sync_api import Locator, Page, expect


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, selector: str) -> None:
        self.locator(selector).click()

    def select_option(self, selector: str, value: str) -> None:
        self.locator(selector).select_option(value)

    def text_content(self, selector: str) -> str:
        return self.locator(selector).text_content() or ""

    def wait_for_visible(self, selector: str) -> None:
        expect(self.locator(selector)).to_be_visible()
