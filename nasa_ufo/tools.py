"""NASA API tool implementations for the NASA UFO agent framework."""

from __future__ import annotations

import datetime
from typing import Any

import requests

from nasa_ufo.config import get_api_key, get_base_url


class NASAToolkit:
    """Collection of NASA API tools available to mission agents."""

    TOOLS = {
        "apod": "Astronomy Picture of the Day — fetch today's (or a specific date's) cosmic image and description.",
        "neo": "Near-Earth Object tracker — list asteroids/comets approaching Earth within a date range.",
        "mars_photos": "Mars Rover photo browser — retrieve images from Curiosity, Opportunity, or Spirit.",
        "earth_imagery": "Earth satellite imagery — fetch a Landsat 8 image for a given lat/lon.",
        "epic": "Earth Polychromatic Imaging Camera — latest natural-colour images of the full Earth disc.",
    }

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or get_api_key()
        self.base_url = base_url or get_base_url()
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform a GET request and return the JSON response."""
        url = f"{self.base_url}{path}"
        all_params = {"api_key": self.api_key}
        if params:
            all_params.update(params)
        response = self._session.get(url, params=all_params, timeout=15)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Public tool methods
    # ------------------------------------------------------------------

    def apod(self, date: str | None = None) -> dict[str, Any]:
        """Fetch NASA's Astronomy Picture of the Day.

        Args:
            date: ISO-8601 date string (YYYY-MM-DD). Defaults to today.

        Returns:
            Dict with keys: title, date, explanation, url, media_type.
        """
        params: dict[str, Any] = {}
        if date:
            params["date"] = date
        return self._get("/planetary/apod", params)

    def neo(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Fetch Near-Earth Objects within a date range (max 7 days).

        Args:
            start_date: ISO-8601 start date (YYYY-MM-DD). Defaults to today.
            end_date: ISO-8601 end date (YYYY-MM-DD). Defaults to start_date + 7 days.

        Returns:
            Dict with element_count and near_earth_objects keyed by date.
        """
        today = datetime.date.today()
        start = start_date or today.isoformat()
        if end_date is None:
            end = (today + datetime.timedelta(days=7)).isoformat()
        else:
            end = end_date
        return self._get("/neo/rest/v1/feed", {"start_date": start, "end_date": end})

    def mars_photos(
        self,
        rover: str = "curiosity",
        sol: int = 1000,
        camera: str | None = None,
    ) -> dict[str, Any]:
        """Fetch Mars Rover photos.

        Args:
            rover: Rover name — curiosity, opportunity, or spirit.
            sol: Martian sol (day) number.
            camera: Optional camera abbreviation (e.g. FHAZ, RHAZ, MAST, NAVCAM).

        Returns:
            Dict with a 'photos' list, each photo having img_src, camera, earth_date.
        """
        params: dict[str, Any] = {"sol": sol}
        if camera:
            params["camera"] = camera.lower()
        rover = rover.lower()
        return self._get(f"/mars-photos/api/v1/rovers/{rover}/photos", params)

    def earth_imagery(
        self,
        lat: float,
        lon: float,
        date: str | None = None,
        dim: float = 0.025,
    ) -> dict[str, Any]:
        """Fetch a Landsat 8 satellite image for a given location.

        Args:
            lat: Latitude in decimal degrees.
            lon: Longitude in decimal degrees.
            date: ISO-8601 date (YYYY-MM-DD). Defaults to most recent available.
            dim: Width and height of the image in degrees.

        Returns:
            Dict with url, date, and asset metadata.
        """
        params: dict[str, Any] = {"lat": lat, "lon": lon, "dim": dim}
        if date:
            params["date"] = date
        return self._get("/planetary/earth/imagery", params)

    def epic(self, collection: str = "natural") -> list[dict[str, Any]]:
        """Fetch the latest Earth Polychromatic Imaging Camera images.

        Args:
            collection: Image collection — "natural" or "enhanced".

        Returns:
            List of image metadata dicts.
        """
        return self._get(f"/EPIC/api/{collection}")  # type: ignore[return-value]

    def list_tools(self) -> dict[str, str]:
        """Return the available tools and their descriptions."""
        return dict(self.TOOLS)
