"""Configuration management for NASA UFO."""

import os

NASA_API_BASE_URL = "https://api.nasa.gov"
DEFAULT_API_KEY = "DEMO_KEY"


def get_api_key() -> str:
    """Return the NASA API key from environment or fall back to DEMO_KEY."""
    return os.environ.get("NASA_API_KEY", DEFAULT_API_KEY)


def get_base_url() -> str:
    """Return the NASA API base URL."""
    return os.environ.get("NASA_API_BASE_URL", NASA_API_BASE_URL)
