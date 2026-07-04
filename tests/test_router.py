from unittest.mock import patch

from pipeline.router import route


@patch("pipeline.router.get_mandi_price")
def test_route_price(mock_get_mandi_price):
    mock_get_mandi_price.return_value = {"price": 100}

    result = route({"question_type": "price", "crop": "onion", "location": "Nashik"})

    mock_get_mandi_price.assert_called_once_with("onion", "Nashik")
    assert result == {"price": 100}


@patch("pipeline.router.get_weather")
def test_route_weather(mock_get_weather):
    mock_get_weather.return_value = {"temperature": "28°C"}

    result = route({"question_type": "weather", "location": "Pune"})

    mock_get_weather.assert_called_once_with("Pune")
    assert result == {"temperature": "28°C"}


@patch("pipeline.router.get_scheme_info")
def test_route_scheme(mock_get_scheme_info):
    mock_get_scheme_info.return_value = {"scheme_name": "PM-KISAN"}

    result = route({"question_type": "scheme", "situation": "PM Kisan help"})

    mock_get_scheme_info.assert_called_once_with("PM Kisan help")
    assert result == {"scheme_name": "PM-KISAN"}


@patch("pipeline.router.get_advisory")
def test_route_unknown_type_defaults_to_advisory(mock_get_advisory):
    mock_get_advisory.return_value = {"problem": "yellow leaves"}

    result = route({"question_type": "unknown-type", "crop": "wheat", "situation": "yellow leaves"})

    mock_get_advisory.assert_called_once_with("wheat", "yellow leaves")
    assert result == {"problem": "yellow leaves"}
