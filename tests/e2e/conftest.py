"""Shared Playwright fixtures and configuration for the e2e test suite.

Best-practice patterns used here:
- Custom ``browser_context_args`` to set a realistic viewport, locale, and
  timezone for every test without repeating boilerplate.
- Automatic screenshot on test failure via the ``_screenshot_on_failure``
  autouse fixture.
- Tracing captured on failure so any broken test can be replayed locally with
  ``playwright show-trace trace.zip``.
- A ``live_server_url`` fixture that tests can use instead of a hard-coded URL;
  swap the implementation for a real local server when the project grows a web
  UI.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Generator

import pytest
from playwright.sync_api import BrowserContext, Page


# ---------------------------------------------------------------------------
# Artifacts directory
# ---------------------------------------------------------------------------

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


@pytest.fixture(scope="session", autouse=True)
def _ensure_artifacts_dir() -> None:
    """Create the artifacts directory once per test session."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Browser context configuration
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Override default browser context args with project-wide settings.

    pytest-playwright merges these kwargs into every ``BrowserContext`` it
    creates, so every ``page`` fixture automatically inherits them.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "en-US",
        "timezone_id": "America/New_York",
        # Record a HAR archive for each context so network traffic is
        # inspectable without running the test again.
        # "record_har_path": str(ARTIFACTS_DIR / "network.har"),
    }


# ---------------------------------------------------------------------------
# Tracing (retain on failure)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _trace_on_failure(
    context: BrowserContext,
    request: pytest.FixtureRequest,
) -> Generator[None, None, None]:
    """Start a Playwright trace before each test and save it on failure.

    The trace can be opened with:
        playwright show-trace tests/e2e/artifacts/<test_name>/trace.zip
    """
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    if failed:
        trace_path = ARTIFACTS_DIR / f"{request.node.name}" / "trace.zip"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        context.tracing.stop(path=str(trace_path))
    else:
        context.tracing.stop()


# ---------------------------------------------------------------------------
# Screenshot on failure
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _screenshot_on_failure(
    page: Page,
    request: pytest.FixtureRequest,
) -> Generator[None, None, None]:
    """Capture a full-page screenshot whenever a test fails."""
    yield
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    if failed:
        screenshot_path = ARTIFACTS_DIR / f"{request.node.name}" / "screenshot.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path), full_page=True)


# ---------------------------------------------------------------------------
# pytest hook – populate rep_call so fixtures can inspect test outcome
# ---------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo  # noqa: ARG001
) -> Generator[None, Any, None]:
    """Attach the test phase report to the item so fixtures can read it."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ---------------------------------------------------------------------------
# Convenience fixture: base URL for tests that navigate to the app
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the web application under test.

    Override with the ``BASE_URL`` environment variable or the
    ``--base-url`` pytest CLI flag when pointing at a staging/production
    environment.
    """
    return os.environ.get("BASE_URL", "https://apod.nasa.gov")
