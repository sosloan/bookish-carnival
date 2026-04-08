"""Tests for the NASA API tool implementations."""

from __future__ import annotations

import pytest
import responses as resp_mock

from nasa_ufo.tools import NASAToolkit


FAKE_API_KEY = "TEST_KEY"
BASE_URL = "https://api.nasa.gov"


@pytest.fixture
def toolkit():
    return NASAToolkit(api_key=FAKE_API_KEY)


# ---------------------------------------------------------------------------
# list_tools
# ---------------------------------------------------------------------------

def test_list_tools_returns_all_tools(toolkit):
    tools = toolkit.list_tools()
    assert set(tools.keys()) == {"apod", "neo", "mars_photos", "earth_imagery", "epic"}
    for desc in tools.values():
        assert isinstance(desc, str) and len(desc) > 0


# ---------------------------------------------------------------------------
# APOD
# ---------------------------------------------------------------------------

@resp_mock.activate
def test_apod_today(toolkit):
    apod_data = {
        "title": "The Milky Way",
        "date": "2024-01-01",
        "explanation": "A beautiful view of our galaxy.",
        "url": "https://apod.nasa.gov/image.jpg",
        "media_type": "image",
    }
    resp_mock.add(
        resp_mock.GET,
        f"{BASE_URL}/planetary/apod",
        json=apod_data,
        status=200,
    )
    result = toolkit.apod()
    assert result["title"] == "The Milky Way"
    assert result["date"] == "2024-01-01"


@resp_mock.activate
def test_apod_specific_date(toolkit):
    apod_data = {"title": "Galaxy", "date": "2023-06-15", "explanation": "...", "url": "http://x", "media_type": "image"}
    resp_mock.add(resp_mock.GET, f"{BASE_URL}/planetary/apod", json=apod_data, status=200)
    result = toolkit.apod(date="2023-06-15")
    assert result["date"] == "2023-06-15"
    # Verify api_key and date params were sent
    assert resp_mock.calls[0].request.url.count("date=2023-06-15") == 1


@resp_mock.activate
def test_apod_http_error_raises(toolkit):
    resp_mock.add(resp_mock.GET, f"{BASE_URL}/planetary/apod", status=403)
    with pytest.raises(Exception):
        toolkit.apod()


# ---------------------------------------------------------------------------
# NEO
# ---------------------------------------------------------------------------

@resp_mock.activate
def test_neo_default_dates(toolkit):
    neo_data = {
        "element_count": 2,
        "near_earth_objects": {
            "2024-01-01": [
                {"name": "Asteroid A", "is_potentially_hazardous_asteroid": False},
                {"name": "Comet B", "is_potentially_hazardous_asteroid": True},
            ]
        },
    }
    resp_mock.add(resp_mock.GET, f"{BASE_URL}/neo/rest/v1/feed", json=neo_data, status=200)
    result = toolkit.neo()
    assert result["element_count"] == 2
    assert "2024-01-01" in result["near_earth_objects"]


@resp_mock.activate
def test_neo_custom_dates(toolkit):
    neo_data = {"element_count": 0, "near_earth_objects": {}}
    resp_mock.add(resp_mock.GET, f"{BASE_URL}/neo/rest/v1/feed", json=neo_data, status=200)
    result = toolkit.neo(start_date="2024-03-01", end_date="2024-03-07")
    assert result["element_count"] == 0
    url = resp_mock.calls[0].request.url
    assert "start_date=2024-03-01" in url
    assert "end_date=2024-03-07" in url


# ---------------------------------------------------------------------------
# Mars Photos
# ---------------------------------------------------------------------------

@resp_mock.activate
def test_mars_photos_curiosity(toolkit):
    photo_data = {
        "photos": [
            {
                "img_src": "https://mars.nasa.gov/photo1.jpg",
                "camera": {"full_name": "Front Hazard Avoidance Camera"},
                "earth_date": "2023-07-04",
            }
        ]
    }
    resp_mock.add(
        resp_mock.GET,
        f"{BASE_URL}/mars-photos/api/v1/rovers/curiosity/photos",
        json=photo_data,
        status=200,
    )
    result = toolkit.mars_photos(rover="curiosity", sol=500)
    assert len(result["photos"]) == 1
    assert result["photos"][0]["earth_date"] == "2023-07-04"


@resp_mock.activate
def test_mars_photos_with_camera(toolkit):
    resp_mock.add(
        resp_mock.GET,
        f"{BASE_URL}/mars-photos/api/v1/rovers/curiosity/photos",
        json={"photos": []},
        status=200,
    )
    toolkit.mars_photos(rover="curiosity", sol=100, camera="FHAZ")
    url = resp_mock.calls[0].request.url
    assert "camera=fhaz" in url


@resp_mock.activate
def test_mars_photos_rover_name_lowercased(toolkit):
    resp_mock.add(
        resp_mock.GET,
        f"{BASE_URL}/mars-photos/api/v1/rovers/opportunity/photos",
        json={"photos": []},
        status=200,
    )
    result = toolkit.mars_photos(rover="Opportunity", sol=10)
    assert "photos" in result


# ---------------------------------------------------------------------------
# Earth Imagery
# ---------------------------------------------------------------------------

@resp_mock.activate
def test_earth_imagery(toolkit):
    imagery_data = {"url": "https://earthengine.googleapis.com/...", "date": "2023-01-01"}
    resp_mock.add(resp_mock.GET, f"{BASE_URL}/planetary/earth/imagery", json=imagery_data, status=200)
    result = toolkit.earth_imagery(lat=29.978, lon=31.134)
    assert "url" in result or "date" in result


@resp_mock.activate
def test_earth_imagery_with_date(toolkit):
    imagery_data = {"url": "https://example.com/img.png", "date": "2022-06-01"}
    resp_mock.add(resp_mock.GET, f"{BASE_URL}/planetary/earth/imagery", json=imagery_data, status=200)
    toolkit.earth_imagery(lat=40.7, lon=-74.0, date="2022-06-01")
    url = resp_mock.calls[0].request.url
    assert "lat=40.7" in url
    assert "lon=-74.0" in url
    assert "date=2022-06-01" in url


# ---------------------------------------------------------------------------
# EPIC
# ---------------------------------------------------------------------------

@resp_mock.activate
def test_epic_natural(toolkit):
    epic_data = [{"image": "epic_1b_20230101000000", "date": "2023-01-01 00:00:00"}]
    resp_mock.add(resp_mock.GET, f"{BASE_URL}/EPIC/api/natural", json=epic_data, status=200)
    result = toolkit.epic()
    assert isinstance(result, list)
    assert result[0]["image"].startswith("epic_")


@resp_mock.activate
def test_epic_enhanced(toolkit):
    resp_mock.add(resp_mock.GET, f"{BASE_URL}/EPIC/api/enhanced", json=[], status=200)
    result = toolkit.epic(collection="enhanced")
    assert result == []
