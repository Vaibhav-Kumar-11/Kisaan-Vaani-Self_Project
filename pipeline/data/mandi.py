"""Mandi (market) price lookup against the data.gov.in agmarknet dataset.

The dataset's own filters are exact-string matches server-side, which
means a farmer typing "Nasik" instead of "Nashik" — or the district name
instead of the exact APMC market name — silently gets zero records back.
Instead of filtering by market server-side, we fetch a batch of records
for the crop and fuzzy-rank them against the requested location ourselves.

The public test key also turned out to be genuinely unreliable in
practice — not just slow, completely unresponsive for stretches, since
it's shared by a large number of similar student projects. Two things
handle that: successful live lookups are cached for a few hours (prices
lag 1-2 days anyway, so this doesn't serve stale data in any way that
matters), and if a live call fails outright, a small reference-price
table for the crops in the knowledge base is used instead of returning
nothing — clearly marked as an estimate, not a live quote.
"""
import json
import time
from pathlib import Path

import requests
from rapidfuzz import fuzz
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import get_secret

# Public test key for this dataset — data.gov.in publishes it openly for
# exactly this purpose, so it's fine as a default rather than a real secret.
API_KEY = get_secret("DATA_GOV_API_KEY", default="579b464db66ec23bdd000001aee7d6da7d4b4ca97a9f21e6b212319d")
RESOURCE_ID = "35985678-0d79-46b4-9ed6-6f13308a1d24"  # agmarknet mandi prices
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

FUZZY_MATCH_THRESHOLD = 60

REFERENCE_PRICES_PATH = Path(__file__).resolve().parents[2] / "knowledge" / "mandi_reference.json"
REFERENCE_PRICES = json.loads(REFERENCE_PRICES_PATH.read_text(encoding="utf-8"))

CACHE_TTL_SECONDS = 6 * 60 * 60
_cache: dict[tuple, tuple[float, dict]] = {}


def _cache_get(key: tuple) -> dict | None:
    entry = _cache.get(key)
    if entry is None:
        return None
    cached_at, value = entry
    if time.time() - cached_at > CACHE_TTL_SECONDS:
        del _cache[key]
        return None
    return value


def _cache_set(key: tuple, value: dict) -> None:
    _cache[key] = (time.time(), value)


def _session() -> requests.Session:
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=1,
        connect=1,
        read=1,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
    )))
    return s


def _empty_result(crop, location) -> dict:
    return {
        "crop": crop,
        "location": location,
        "price": None,
        "unit": "per quintal",
        "market": None,
        "date": None,
        "source": "data.gov.in",
    }


def _reference_fallback(crop: str, location) -> dict:
    ref = REFERENCE_PRICES.get(crop.lower())
    if not ref:
        return _empty_result(crop, location)

    return {
        "crop": crop,
        "location": location,
        "price": ref["price"],
        "unit": ref["unit"],
        "market": None,
        "date": None,
        "source": "reference estimate — data.gov.in isn't responding right now, this is not a live quote",
    }


def _best_market_match(records: list[dict], location: str | None) -> dict:
    if not location:
        return records[0]

    scored = [
        (fuzz.partial_ratio(location.lower(), (rec.get("market") or "").lower()), rec)
        for rec in records
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)

    best_score, best_rec = scored[0]
    if best_score >= FUZZY_MATCH_THRESHOLD:
        return best_rec

    # No market name close enough to the requested location — fall back to
    # the most recent record for the crop nationally rather than nothing.
    return records[0]


def get_mandi_price(crop: str | None, location: str | None) -> dict:
    """
    Input : crop, location — either may be None.
    Output: {"crop", "location", "price", "unit", "market", "date", "source"}

    Note: data.gov.in prices lag 1-2 days behind actual mandi trading.
    """
    if not crop:
        print("Mandi        : no crop specified, cannot look up a price")
        return _empty_result(crop, location)

    cache_key = (crop.lower(), (location or "").lower())
    cached = _cache_get(cache_key)
    if cached is not None:
        print(f"Mandi        : serving cached price for {crop}/{location}")
        return cached

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": "50",
        "filters[commodity]": crop.title(),
    }

    print(f"Mandi        : fetching price for {crop} near {location}")

    try:
        response = _session().get(BASE_URL, params=params, timeout=6)
        response.raise_for_status()
        records = response.json().get("records", [])

        if not records:
            print(f"Mandi        : no records found for {crop}, using reference price")
            return _reference_fallback(crop, location)

        rec = _best_market_match(records, location)

        result = {
            "crop": rec.get("commodity", crop),
            "location": rec.get("market", location),
            "price": rec.get("modal_price"),
            "unit": "per quintal",
            "market": rec.get("market"),
            "date": rec.get("arrival_date"),
            "source": "data.gov.in",
        }

        print(f"Mandi        : price = Rs.{result['price']} {result['unit']} at {result['market']} on {result['date']}")
        _cache_set(cache_key, result)
        return result

    except requests.RequestException as e:
        print(f"Mandi        : API error — {e}, using reference price")
        return _reference_fallback(crop, location)
