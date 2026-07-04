from unittest.mock import patch

from pipeline.intent import extract_intent


@patch("pipeline.intent.call_llm_json")
@patch("pipeline.intent.get_client")
def test_extract_intent_happy_path(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = {
        "crop": "onion",
        "location": "Nashik",
        "situation": "price inquiry",
        "question_type": "price",
    }

    result = extract_intent("What is the price of onion in Nashik?")

    assert result["question_type"] == "price"
    assert result["crop"] == "onion"
    assert result["location"] == "Nashik"


@patch("pipeline.intent.call_llm_json")
@patch("pipeline.intent.get_client")
def test_extract_intent_falls_back_on_llm_failure(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = None

    result = extract_intent("some garbled question")

    assert result["question_type"] == "advisory"
    assert result["situation"] == "some garbled question"


@patch("pipeline.intent.call_llm_json")
@patch("pipeline.intent.get_client")
def test_extract_intent_falls_back_on_invalid_question_type(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = {"question_type": "not-a-real-type"}

    result = extract_intent("weird question")

    assert result["question_type"] == "advisory"
