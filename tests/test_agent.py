"""Tests for the NASA UFO agent classes."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from nasa_ufo.agent import HostAgent, MissionAgent, MissionResult
from nasa_ufo.tools import NASAToolkit


# ---------------------------------------------------------------------------
# MissionResult
# ---------------------------------------------------------------------------

def test_mission_result_str_success():
    r = MissionResult("apod", "apod", {}, "Great success!", success=True)
    assert str(r) == "Great success!"


def test_mission_result_str_failure():
    r = MissionResult("apod", "apod", None, "", success=False, error="Network error")
    assert "Mission failed" in str(r)
    assert "Network error" in str(r)


def test_mission_result_to_dict():
    r = MissionResult("neo", "neo", {"count": 3}, "Found 3 NEOs", success=True)
    d = r.to_dict()
    assert d["tool_used"] == "neo"
    assert d["success"] is True
    assert d["data"] == {"count": 3}


# ---------------------------------------------------------------------------
# MissionAgent
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_toolkit():
    toolkit = MagicMock(spec=NASAToolkit)
    toolkit.apod.return_value = {
        "title": "Test Star",
        "date": "2024-01-01",
        "explanation": "A test star image.",
        "url": "https://apod.nasa.gov/test.jpg",
        "media_type": "image",
    }
    toolkit.neo.return_value = {
        "element_count": 1,
        "near_earth_objects": {
            "2024-01-01": [{"name": "Asteroid X", "is_potentially_hazardous_asteroid": False}]
        },
    }
    toolkit.mars_photos.return_value = {
        "photos": [
            {
                "img_src": "https://mars.nasa.gov/img.jpg",
                "camera": {"full_name": "Mast Camera"},
                "earth_date": "2023-07-04",
            }
        ]
    }
    toolkit.earth_imagery.return_value = {"url": "https://earth.example.com/img.png", "date": "2023-01-01"}
    toolkit.epic.return_value = [{"image": "epic_img_01", "date": "2023-01-01 00:00:00"}]
    toolkit.list_tools.return_value = NASAToolkit.TOOLS
    return toolkit


@pytest.fixture
def mission_agent(mock_toolkit):
    return MissionAgent(toolkit=mock_toolkit)


def test_run_apod(mission_agent, mock_toolkit):
    result = mission_agent.run_apod()
    mock_toolkit.apod.assert_called_once_with(date=None)
    assert result.tool_used == "apod"
    assert result.success is True
    assert "Test Star" in result.summary


def test_run_apod_with_date(mission_agent, mock_toolkit):
    mission_agent.run_apod(date="2024-06-01")
    mock_toolkit.apod.assert_called_once_with(date="2024-06-01")


def test_run_neo(mission_agent, mock_toolkit):
    result = mission_agent.run_neo()
    mock_toolkit.neo.assert_called_once_with(start_date=None, end_date=None)
    assert result.tool_used == "neo"
    assert "1 near-Earth objects" in result.summary


def test_run_neo_hazardous_flag(mission_agent, mock_toolkit):
    mock_toolkit.neo.return_value = {
        "element_count": 1,
        "near_earth_objects": {
            "2024-01-01": [{"name": "Doomsday Rock", "is_potentially_hazardous_asteroid": True}]
        },
    }
    result = mission_agent.run_neo()
    assert "POTENTIALLY HAZARDOUS" in result.summary


def test_run_mars_photos(mission_agent, mock_toolkit):
    result = mission_agent.run_mars_photos(rover="curiosity", sol=500)
    mock_toolkit.mars_photos.assert_called_once_with(rover="curiosity", sol=500, camera=None)
    assert result.tool_used == "mars_photos"
    assert "Curiosity" in result.summary
    assert "1 photo(s)" in result.summary


def test_run_earth_imagery(mission_agent, mock_toolkit):
    result = mission_agent.run_earth_imagery(lat=51.5, lon=-0.1)
    mock_toolkit.earth_imagery.assert_called_once_with(lat=51.5, lon=-0.1, date=None)
    assert result.tool_used == "earth_imagery"
    assert "51.5" in result.summary


def test_run_epic(mission_agent, mock_toolkit):
    result = mission_agent.run_epic()
    mock_toolkit.epic.assert_called_once_with(collection="natural")
    assert result.tool_used == "epic"
    assert "1 image(s)" in result.summary


# ---------------------------------------------------------------------------
# HostAgent — routing
# ---------------------------------------------------------------------------

@pytest.fixture
def host_agent(mock_toolkit):
    agent = MissionAgent(toolkit=mock_toolkit)
    return HostAgent(mission_agent=agent)


def test_route_apod_keywords(host_agent):
    assert host_agent._route("show me the astronomy picture of the day") == "apod"
    assert host_agent._route("get today's APOD") == "apod"


def test_route_neo_keywords(host_agent):
    assert host_agent._route("track asteroids near Earth") == "neo"
    assert host_agent._route("any hazardous NEOs this week?") == "neo"
    assert host_agent._route("show approaching comets") == "neo"


def test_route_mars_keywords(host_agent):
    assert host_agent._route("show mars rover images") == "mars_photos"
    assert host_agent._route("Curiosity photos from sol 500") == "mars_photos"
    assert host_agent._route("Spirit rover on Mars") == "mars_photos"


def test_route_earth_keywords(host_agent):
    assert host_agent._route("get satellite imagery of Earth") == "earth_imagery"
    assert host_agent._route("show Landsat image at lat 40 lon -74") == "earth_imagery"


def test_route_epic_keywords(host_agent):
    assert host_agent._route("fetch EPIC full earth disc image") == "epic"
    assert host_agent._route("polychromatic Earth image") == "epic"


def test_route_default_apod(host_agent):
    assert host_agent._route("something completely unrelated") == "apod"


# ---------------------------------------------------------------------------
# HostAgent — param extraction
# ---------------------------------------------------------------------------

def test_extract_date(host_agent):
    params = host_agent._extract_params("Show APOD for 2024-03-15")
    assert params["date"] == "2024-03-15"


def test_extract_rover(host_agent):
    params = host_agent._extract_params("Show curiosity photos")
    assert params["rover"] == "curiosity"


def test_extract_sol(host_agent):
    params = host_agent._extract_params("Curiosity photos sol: 750")
    assert params["sol"] == 750


def test_extract_overrides_not_replaced(host_agent):
    params = host_agent._extract_params("Show APOD for 2024-03-15", date="2023-01-01")
    # override should win
    assert params["date"] == "2023-01-01"


# ---------------------------------------------------------------------------
# HostAgent — run() integration
# ---------------------------------------------------------------------------

def test_run_dispatches_apod(host_agent):
    result = host_agent.run("today's astronomy picture of the day")
    assert result.tool_used == "apod"
    assert result.success is True


def test_run_dispatches_neo(host_agent):
    result = host_agent.run("show me asteroids near Earth")
    assert result.tool_used == "neo"


def test_run_dispatches_mars(host_agent):
    result = host_agent.run("curiosity rover photos")
    assert result.tool_used == "mars_photos"


def test_run_records_history(host_agent):
    host_agent.run("today's astronomy picture of the day")
    host_agent.run("show asteroids near Earth")
    assert len(host_agent.history()) == 2


def test_run_handles_tool_exception(host_agent):
    host_agent.mission_agent.toolkit.apod.side_effect = ConnectionError("timeout")
    result = host_agent.run("get the APOD")
    assert result.success is False
    assert "timeout" in result.error


def test_list_tools(host_agent):
    tools = host_agent.list_tools()
    assert "apod" in tools
    assert "neo" in tools
    assert "mars_photos" in tools
