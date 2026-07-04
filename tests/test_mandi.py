from unittest.mock import MagicMock, patch

from pipeline.data.mandi import get_mandi_price


def _fake_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@patch("pipeline.data.mandi._session")
def test_get_mandi_price_fuzzy_matches_misspelled_market(mock_session_factory):
    # This is the exact bug from the original code: the API's exact-match
    # filter would return zero records for "Nasik" (missing the 'h'). The
    # fix fetches a broader batch and fuzzy-ranks it client-side instead.
    session = MagicMock()
    session.get.return_value = _fake_response({
        "records": [
            {"commodity": "Onion", "market": "Pune", "modal_price": "1500", "arrival_date": "2026-07-01"},
            {"commodity": "Onion", "market": "Nashik", "modal_price": "1200", "arrival_date": "2026-07-02"},
        ]
    })
    mock_session_factory.return_value = session

    result = get_mandi_price("onion", "Nasik")

    assert result["market"] == "Nashik"
    assert result["price"] == "1200"


@patch("pipeline.data.mandi._session")
def test_get_mandi_price_no_records_returns_empty(mock_session_factory):
    session = MagicMock()
    session.get.return_value = _fake_response({"records": []})
    mock_session_factory.return_value = session

    result = get_mandi_price("dragonfruit", "Nowhere")

    assert result["price"] is None


def test_get_mandi_price_no_crop_returns_empty_without_calling_api():
    result = get_mandi_price(None, "Nashik")
    assert result["price"] is None
