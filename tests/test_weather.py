from unittest.mock import MagicMock, patch

from pipeline.data.weather import get_weather


def _fake_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@patch("pipeline.data.weather._session")
def test_get_weather_happy_path(mock_session_factory):
    geocode_resp = _fake_response({
        "results": [{
            "latitude": 18.52, "longitude": 73.85, "name": "Pune",
            "admin1": "Maharashtra", "country": "India", "country_code": "IN",
        }]
    })
    forecast_resp = _fake_response({
        "current": {"temperature_2m": 28, "relative_humidity_2m": 74, "precipitation": 0},
        "daily": {
            "precipitation_sum": [4.2, 8.1, 5.9],
            "temperature_2m_max": [31, 30, 29],
            "temperature_2m_min": [22, 21, 21],
        },
    })
    session = MagicMock()
    session.get.side_effect = [geocode_resp, forecast_resp]
    mock_session_factory.return_value = session

    result = get_weather("Pune")

    assert result["location"] == "Pune, Maharashtra, India"
    assert result["temperature"] == "28°C"
    assert result["forecast"].startswith("Light rain")
    assert result["daily_rain_mm"] == [4.2, 8.1, 5.9]


def test_get_weather_no_location_returns_empty():
    result = get_weather(None)
    assert result["temperature"] is None


@patch("pipeline.data.weather._session")
def test_get_weather_geocode_fails_returns_empty(mock_session_factory):
    session = MagicMock()
    session.get.return_value = _fake_response({"results": []})
    mock_session_factory.return_value = session

    result = get_weather("Nowhereville")

    assert result["temperature"] is None
