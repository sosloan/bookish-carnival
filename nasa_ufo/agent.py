"""Agent classes for NASA UFO — inspired by Microsoft UFO's dual-agent design.

Architecture mirrors UFO's HostAgent / AppAgent split:

    HostAgent  — high-level planner that receives a natural-language mission,
                 selects the right NASA tool, and delegates to a MissionAgent.
    MissionAgent — executor that calls NASA API tools and formats results.
"""

from __future__ import annotations

import re
from typing import Any

import requests

from nasa_ufo.renderer import render
from nasa_ufo.tools import NASAToolkit


# ---------------------------------------------------------------------------
# Mission result dataclass (lightweight)
# ---------------------------------------------------------------------------

class MissionResult:
    """Encapsulates the outcome of a single agent mission."""

    def __init__(
        self,
        mission: str,
        tool_used: str,
        data: Any,
        summary: str,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        self.mission = mission
        self.tool_used = tool_used
        self.data = data
        self.summary = summary
        self.success = success
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission": self.mission,
            "tool_used": self.tool_used,
            "success": self.success,
            "summary": self.summary,
            "error": self.error,
            "data": self.data,
        }

    def __str__(self) -> str:
        if not self.success:
            return f"❌ Mission failed: {self.error}"
        return self.summary


# ---------------------------------------------------------------------------
# MissionAgent — executes a single tool call
# ---------------------------------------------------------------------------

class MissionAgent:
    """Executor agent that calls NASA API tools and returns structured results.

    Inspired by UFO's *AppAgent* which interacts directly with an application.
    The MissionAgent interacts directly with NASA APIs.
    """

    def __init__(self, toolkit: NASAToolkit | None = None) -> None:
        self.toolkit = toolkit or NASAToolkit()

    # ------------------------------------------------------------------
    # Tool dispatchers
    # ------------------------------------------------------------------

    def run_apod(self, date: str | None = None) -> MissionResult:
        """Execute an APOD mission."""
        data = self.toolkit.apod(date=date)
        summary = render(
            "apod.txt",
            title=data.get("title", "Unknown"),
            date=data.get("date", ""),
            explanation=data.get("explanation", ""),
            url=data.get("url", ""),
        )
        return MissionResult("apod", "apod", data, summary)

    def run_neo(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> MissionResult:
        """Execute a Near-Earth Object tracking mission."""
        data = self.toolkit.neo(start_date=start_date, end_date=end_date)
        count = data.get("element_count", 0)
        neos = data.get("near_earth_objects", {})
        dates = [
            (
                date_str,
                [
                    {
                        "name": obj.get("name", "Unknown"),
                        "hazardous": obj.get("is_potentially_hazardous_asteroid", False),
                    }
                    for obj in objects
                ],
            )
            for date_str, objects in list(neos.items())[:3]
        ]
        summary = render("neo.txt", count=count, dates=dates)
        return MissionResult("neo", "neo", data, summary)

    def run_mars_photos(
        self,
        rover: str = "curiosity",
        sol: int = 1000,
        camera: str | None = None,
    ) -> MissionResult:
        """Execute a Mars Rover photo browsing mission."""
        data = self.toolkit.mars_photos(rover=rover, sol=sol, camera=camera)
        photos = data.get("photos", [])
        photo_items = [
            {
                "camera": p.get("camera", {}).get("full_name", "Unknown"),
                "url": p.get("img_src", ""),
            }
            for p in photos
        ]
        summary = render(
            "mars_photos.txt",
            rover=rover.title(),
            sol=sol,
            total=len(photos),
            photos=photo_items,
        )
        return MissionResult("mars_photos", "mars_photos", data, summary)

    def run_earth_imagery(
        self, lat: float, lon: float, date: str | None = None
    ) -> MissionResult:
        """Execute an Earth satellite imagery mission."""
        data = self.toolkit.earth_imagery(lat=lat, lon=lon, date=date)
        url = data.get("url", data.get("resource", {}).get("dataset", ""))
        summary = render(
            "earth_imagery.txt",
            lat=lat,
            lon=lon,
            date=data.get("date", "N/A"),
            url=url,
        )
        return MissionResult("earth_imagery", "earth_imagery", data, summary)

    def run_epic(self, collection: str = "natural") -> MissionResult:
        """Execute an EPIC Earth imagery mission."""
        data = self.toolkit.epic(collection=collection)
        items = data if isinstance(data, list) else []
        epic_items = [
            {"name": item.get("image", ""), "date": item.get("date", "")}
            for item in items
        ]
        summary = render(
            "epic.txt",
            collection=collection,
            total=len(items),
            items=epic_items,
        )
        return MissionResult("epic", "epic", data, summary)


# ---------------------------------------------------------------------------
# HostAgent — routes missions to the right MissionAgent method
# ---------------------------------------------------------------------------

class HostAgent:
    """High-level planner agent that interprets missions and delegates to MissionAgent.

    Inspired by UFO's *HostAgent* which decides which application to activate
    and what high-level plan to follow.  The HostAgent here parses a
    natural-language mission description and selects the appropriate NASA tool.
    """

    # Keyword routing table:  list of (keywords, tool_name)
    # NOTE: more-specific routes must appear before general ones to avoid false matches.
    _ROUTES: list[tuple[list[str], str]] = [
        (["apod", "astronomy picture", "picture of the day", "daily image", "cosmic image"], "apod"),
        (["neo", "near-earth", "asteroid", "comet", "hazardous", "approaching"], "neo"),
        (["mars", "rover", "curiosity", "opportunity", "spirit", "martian"], "mars_photos"),
        (["epic", "polychromatic", "full earth", "full disc"], "epic"),
        (["earth imagery", "satellite", "landsat", "earth image", "location imagery"], "earth_imagery"),
    ]

    def __init__(
        self,
        mission_agent: MissionAgent | None = None,
        toolkit: NASAToolkit | None = None,
    ) -> None:
        self.mission_agent = mission_agent or MissionAgent(toolkit=toolkit)
        self._history: list[MissionResult] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, mission: str, **kwargs: Any) -> MissionResult:
        """Parse *mission* and delegate to the appropriate MissionAgent method.

        Args:
            mission: Natural-language description of what to explore.
            **kwargs: Optional tool-specific overrides (date, rover, lat, lon, …).

        Returns:
            A MissionResult describing the outcome.
        """
        tool = self._route(mission)
        result = self._execute(tool, mission, **kwargs)
        self._history.append(result)
        return result

    def history(self) -> list[MissionResult]:
        """Return past mission results (agent memory)."""
        return list(self._history)

    def list_tools(self) -> dict[str, str]:
        """Return available tools."""
        return self.mission_agent.toolkit.list_tools()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _route(self, mission: str) -> str:
        """Select a tool name based on keywords in the mission string."""
        lower = mission.lower()
        for keywords, tool in self._ROUTES:
            if any(kw in lower for kw in keywords):
                return tool
        # Default to APOD when no specific tool is identified
        return "apod"

    def _extract_params(self, mission: str, **overrides: Any) -> dict[str, Any]:
        """Extract parameters from mission text and overrides."""
        params: dict[str, Any] = dict(overrides)

        # Date extraction: YYYY-MM-DD
        date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", mission)
        if date_match and "date" not in params:
            params["date"] = date_match.group(1)

        # Rover name
        for rover in ("curiosity", "opportunity", "spirit"):
            if rover in mission.lower() and "rover" not in params:
                params["rover"] = rover

        # Sol number
        sol_match = re.search(r"\bsol[:\s]+(\d+)\b", mission, re.IGNORECASE)
        if sol_match and "sol" not in params:
            params["sol"] = int(sol_match.group(1))

        return params

    def _execute(self, tool: str, mission: str, **kwargs: Any) -> MissionResult:
        """Execute the selected tool with extracted parameters."""
        params = self._extract_params(mission, **kwargs)
        try:
            if tool == "apod":
                return self.mission_agent.run_apod(date=params.get("date"))
            if tool == "neo":
                return self.mission_agent.run_neo(
                    start_date=params.get("start_date") or params.get("date"),
                    end_date=params.get("end_date"),
                )
            if tool == "mars_photos":
                return self.mission_agent.run_mars_photos(
                    rover=params.get("rover", "curiosity"),
                    sol=params.get("sol", 1000),
                    camera=params.get("camera"),
                )
            if tool == "earth_imagery":
                return self.mission_agent.run_earth_imagery(
                    lat=params.get("lat", 29.978),
                    lon=params.get("lon", 31.134),
                    date=params.get("date"),
                )
            if tool == "epic":
                return self.mission_agent.run_epic(
                    collection=params.get("collection", "natural")
                )
        except (OSError, ValueError, RuntimeError, LookupError, requests.exceptions.RequestException) as exc:
            return MissionResult(
                mission=mission,
                tool_used=tool,
                data=None,
                summary="",
                success=False,
                error=str(exc),
            )
        # Should never reach here
        return MissionResult(mission, tool, None, "", False, f"Unknown tool: {tool}")
