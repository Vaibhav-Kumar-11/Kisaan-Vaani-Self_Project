"""Live weather forecast for any Indian city.

Uses Open-Meteo's free geocoding + forecast APIs — no API key needed, and
no hardcoded city list, so it works for any city/district/village name
instead of only the handful someone thought to hardcode.
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _session() -> requests.Session:
    """HTTP session with automatic retry on server errors."""
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
    )))
    return s


def _geocode(location: str):
    """
    City/district/village name -> (lat, lon, resolved display name).

    Biases toward Indian results but falls back to any country if the
    location isn't found in India. Returns (None, None, None) if nothing
    matches.
    """
    params = {"name": location, "count": 10, "language": "en", "format": "json"}

    try:
        resp = _session().get(GEOCODING_URL, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        if not results:
            return None, None, None

        india = [r for r in results if r.get("country_code") == "IN"]
        best = india[0] if india else results[0]

        lat = best.get("latitude")
        lon = best.get("longitude")
        parts = [best.get("name"), best.get("admin1"), best.get("country")]
        full_name = ", ".join(p for p in parts if p)

        print(f"Weather      : geocoded {location!r} -> {full_name} ({lat}, {lon})")
        return lat, lon, full_name

    except requests.RequestException as e:
        print(f"Weather      : geocoding error — {e}")
        return None, None, None


def _empty_result(location) -> dict:
    return {
        "location": location,
        "temperature": None,
        "rainfall_mm": None,
        "humidity": None,
        "condition": None,
        "forecast": None,
        "source": "open-meteo.com",
    }


def get_weather(location: str | None) -> dict:
    """
    Fetch current weather + 3-day forecast for any city.

    Output:
        {
            "location"      : "Pune, Maharashtra, India",
            "temperature"   : "28°C",
            "rainfall_mm"   : "2.4",
            "humidity"      : "74%",
            "condition"     : "Currently 28°C, humidity 74%",
            "forecast"      : "Light rain expected — 18.2mm over 3 days",
            "daily_rain_mm" : [4.2, 8.1, 5.9],
            "temp_max"      : ["31°C", "30°C", "29°C"],
            "temp_min"      : ["22°C", "21°C", "21°C"],
            "source"        : "open-meteo.com",
        }

    Fields come back as None if geocoding or the forecast call fails.
    """
    if not location:
        print("Weather      : no location provided")
        return _empty_result(location)

    lat, lon, resolved_name = _geocode(location)
    if lat is None or lon is None:
        print(f"Weather      : could not geocode {location!r}")
        return _empty_result(location)

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Kolkata",
        "forecast_days": 3,
    }

    try:
        resp = _session().get(FORECAST_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        temp = current.get("temperature_2m", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        rainfall = current.get("precipitation", 0)

        daily_rain = daily.get("precipitation_sum", [0, 0, 0])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        total_rain = sum(r for r in daily_rain if r is not None)

        if total_rain > 20:
            forecast = f"Heavy rain expected — {total_rain:.1f}mm over 3 days"
        elif total_rain > 5:
            forecast = f"Light rain expected — {total_rain:.1f}mm over 3 days"
        else:
            forecast = "Mostly dry for next 3 days"

        result = {
            "location": resolved_name,
            "temperature": f"{temp}°C",
            "rainfall_mm": str(rainfall),
            "humidity": f"{humidity}%",
            "condition": f"Currently {temp}°C, humidity {humidity}%",
            "forecast": forecast,
            "daily_rain_mm": daily_rain,
            "temp_max": [f"{t}°C" for t in temp_max],
            "temp_min": [f"{t}°C" for t in temp_min],
            "source": "open-meteo.com",
        }

        print(f"Weather      : {result['condition']}")
        print(f"Weather      : {result['forecast']}")
        return result

    except requests.RequestException as e:
        print(f"Weather      : forecast error — {e}")
        return _empty_result(resolved_name)
