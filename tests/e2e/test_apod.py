"""End-to-end tests for the APOD viewer page.

These tests use Page Object Model fixtures and run against mock HTML content
injected via ``page.set_content()``, so they are fully network-independent and
fast.  When a real web frontend is deployed, replace ``apod.load_mock()`` with
``apod.navigate(base_url)`` to run against the live application.

Best practices demonstrated:
- Page Object Model: every selector lives in ``ApodPage``, not in the test.
- Accessibility-first locators: ``get_by_role`` and ``get_by_label``.
- ``expect()`` assertions: auto-retry on async DOM updates.
- Parametrize: cover multiple scenarios without copy-paste.
- Descriptive test names that read like specifications.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.pages.apod_page import ApodPage


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def apod(page: Page) -> ApodPage:
    """Return a pre-loaded ApodPage with mock content."""
    return ApodPage(page).load_mock()


# ---------------------------------------------------------------------------
# Page rendering
# ---------------------------------------------------------------------------

def test_page_title_is_correct(apod: ApodPage) -> None:
    apod.expect_title_contains("NASA APOD Viewer")


def test_site_heading_is_visible(apod: ApodPage) -> None:
    expect(apod.title_heading).to_be_visible()
    expect(apod.title_heading).to_have_text("NASA APOD Viewer")


def test_apod_card_is_present(apod: ApodPage) -> None:
    expect(apod.apod_card).to_be_visible()


# ---------------------------------------------------------------------------
# APOD content
# ---------------------------------------------------------------------------

def test_apod_title_is_displayed(apod: ApodPage) -> None:
    apod.expect_apod_title("The Milky Way Over Patagonia")


def test_apod_date_is_displayed(apod: ApodPage) -> None:
    apod.expect_apod_date("2024-06-15")


def test_apod_image_is_visible(apod: ApodPage) -> None:
    apod.expect_image_visible()


def test_apod_image_has_alt_text(apod: ApodPage) -> None:
    """Images must have descriptive alt text for accessibility."""
    alt = apod.apod_image.get_attribute("alt")
    assert alt and len(alt) > 0, "Image alt text must not be empty"


def test_apod_explanation_is_not_empty(apod: ApodPage) -> None:
    apod.expect_explanation_not_empty()


# ---------------------------------------------------------------------------
# Navigation controls
# ---------------------------------------------------------------------------

def test_previous_day_button_is_visible(apod: ApodPage) -> None:
    expect(apod.prev_button).to_be_visible()


def test_next_day_button_is_visible(apod: ApodPage) -> None:
    expect(apod.next_button).to_be_visible()


# ---------------------------------------------------------------------------
# Date form
# ---------------------------------------------------------------------------

def test_date_form_has_label_and_input(apod: ApodPage) -> None:
    """Date input must be discoverable by its accessible role and name."""
    expect(apod.date_input).to_be_visible()


def test_date_form_accepts_date_value(apod: ApodPage) -> None:
    apod.date_input.fill("2023-07-04")
    expect(apod.date_input).to_have_value("2023-07-04")


# ---------------------------------------------------------------------------
# Parametrized – APOD card child elements are all rendered
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("selector, description", [
    (".apod-title", "title"),
    (".apod-date", "date"),
    ("img.apod-image", "image"),
    (".apod-explanation", "explanation"),
])
def test_apod_card_child_is_visible(
    apod: ApodPage, selector: str, description: str
) -> None:
    """Every required APOD card element should be visible."""
    expect(apod.page.locator(selector)).to_be_visible()


# ---------------------------------------------------------------------------
# Accessibility – ARIA landmarks
# ---------------------------------------------------------------------------

def test_main_landmark_is_present(apod: ApodPage) -> None:
    expect(apod.page.get_by_role("main")).to_be_visible()


def test_apod_section_has_aria_label(apod: ApodPage) -> None:
    section = apod.page.get_by_role("region", name="Astronomy Picture of the Day")
    expect(section).to_be_visible()


def test_date_form_has_aria_label(apod: ApodPage) -> None:
    form = apod.page.get_by_role("form", name="Jump to date")
    expect(form).to_be_visible()


def test_nav_has_aria_label(apod: ApodPage) -> None:
    nav = apod.page.get_by_role("navigation", name="Browse dates")
    expect(nav).to_be_visible()
