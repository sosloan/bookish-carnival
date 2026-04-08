"""Base page object – common helpers shared by all page objects.

The Page Object Model (POM) pattern keeps selectors and low-level Playwright
calls out of tests.  Tests stay readable; selector changes only touch one file.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect


class BasePage:
    """Thin wrapper around a Playwright ``Page`` with reusable helpers."""

    # Subclasses declare their canonical path (e.g. "/apod/").
    PATH: str = "/"

    def __init__(self, page: Page) -> None:
        self._page = page

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def navigate(self, base_url: str = "") -> "BasePage":
        """Navigate to ``base_url + PATH``."""
        self._page.goto(f"{base_url.rstrip('/')}{self.PATH}")
        return self

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def expect_title_contains(self, text: str) -> None:
        """Assert that the page <title> contains *text*."""
        expect(self._page).to_have_title(text)

    def expect_url_contains(self, fragment: str) -> None:
        """Assert that the current URL contains *fragment*."""
        expect(self._page).to_have_url(f".*{fragment}.*")

    def expect_visible(self, selector: str) -> None:
        """Assert that the element identified by *selector* is visible."""
        expect(self._page.locator(selector)).to_be_visible()

    # ------------------------------------------------------------------
    # Interactions
    # ------------------------------------------------------------------

    def click(self, selector: str) -> None:
        self._page.locator(selector).click()

    def fill(self, selector: str, value: str) -> None:
        self._page.locator(selector).fill(value)

    def text_content(self, selector: str) -> str:
        """Return the text content of the element matching *selector*."""
        return self._page.locator(selector).text_content() or ""

    # ------------------------------------------------------------------
    # Accessibility
    # ------------------------------------------------------------------

    def get_by_role(self, role: str, **kwargs) -> Locator:
        return self._page.get_by_role(role, **kwargs)

    def get_by_label(self, label: str) -> Locator:
        return self._page.get_by_label(label)

    def get_by_text(self, text: str, **kwargs) -> Locator:
        return self._page.get_by_text(text, **kwargs)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @property
    def page(self) -> Page:
        """Expose the underlying Playwright ``Page`` for advanced use."""
        return self._page
