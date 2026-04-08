"""Page Object for a minimal NASA APOD HTML viewer.

In production this would wrap the real deployed page.  During unit-level E2E
tests the page content is injected via ``page.set_content()``, keeping the
suite fast and network-independent.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.e2e.pages.base_page import BasePage


# Minimal HTML that mimics the structure we expect the APOD viewer to have.
# Swap this for a real URL fixture when a web frontend is available.
APOD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>NASA APOD Viewer</title>
</head>
<body>
  <header>
    <h1 class="site-title">NASA APOD Viewer</h1>
  </header>
  <main>
    <section class="apod-card" aria-label="Astronomy Picture of the Day">
      <h2 class="apod-title">The Milky Way Over Patagonia</h2>
      <p class="apod-date">2024-06-15</p>
      <img
        class="apod-image"
        src="https://apod.nasa.gov/apod/image/2406/MilkyWay_sample.jpg"
        alt="The Milky Way galaxy arching over the Patagonian steppe"
      />
      <p class="apod-explanation">
        The band of the Milky Way galaxy arches dramatically across the night sky
        above the flat Patagonian steppe in this breathtaking long-exposure image.
      </p>
    </section>
    <nav aria-label="Browse dates">
      <button id="prev-day">Previous day</button>
      <button id="next-day">Next day</button>
    </nav>
    <form id="date-form" aria-label="Jump to date">
      <label for="date-input">Jump to date</label>
      <input id="date-input" type="date" name="date" />
      <button type="submit">Go</button>
    </form>
  </main>
</body>
</html>
"""


class ApodPage(BasePage):
    """Page Object for the APOD viewer page."""

    PATH = "/apod/"

    # ------------------------------------------------------------------
    # Locators (single source of truth for selectors)
    # ------------------------------------------------------------------

    @property
    def title_heading(self):
        return self._page.locator("h1.site-title")

    @property
    def apod_card(self):
        return self._page.locator(".apod-card")

    @property
    def apod_title(self):
        return self._page.locator(".apod-title")

    @property
    def apod_date(self):
        return self._page.locator(".apod-date")

    @property
    def apod_image(self):
        return self._page.locator("img.apod-image")

    @property
    def apod_explanation(self):
        return self._page.locator(".apod-explanation")

    @property
    def prev_button(self):
        return self._page.get_by_role("button", name="Previous day")

    @property
    def next_button(self):
        return self._page.get_by_role("button", name="Next day")

    @property
    def date_input(self):
        return self._page.get_by_role("textbox", name="Jump to date")

    @property
    def go_button(self):
        return self._page.get_by_role("button", name="Go")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def load_mock(self) -> "ApodPage":
        """Inject mock HTML into the page (no network required)."""
        self._page.set_content(APOD_HTML)
        return self

    def jump_to_date(self, date: str) -> None:
        """Fill the date picker and submit the form."""
        self.date_input.fill(date)
        self.go_button.click()

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def expect_apod_title(self, text: str) -> None:
        expect(self.apod_title).to_have_text(text)

    def expect_apod_date(self, date: str) -> None:
        expect(self.apod_date).to_have_text(date)

    def expect_image_visible(self) -> None:
        expect(self.apod_image).to_be_visible()

    def expect_explanation_not_empty(self) -> None:
        expect(self.apod_explanation).not_to_be_empty()
