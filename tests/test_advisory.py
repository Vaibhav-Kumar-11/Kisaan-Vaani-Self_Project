from unittest.mock import patch

from pipeline.data.advisory import get_advisory


@patch("pipeline.data.advisory.call_llm_json")
@patch("pipeline.data.advisory.get_client")
def test_get_advisory_exact_crop_match(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = {
        "problem": "yellow leaves",
        "cause": "nitrogen deficiency",
        "solution": "apply urea",
        "prevention": "balanced fertilizer next season",
        "answer": "Apply urea now and watch for rust.",
    }

    result = get_advisory("wheat", "yellow leaves on wheat plants")

    assert result["crop"] == "wheat"
    assert result["answer"] == "Apply urea now and watch for rust."


@patch("pipeline.data.advisory.call_llm_json")
@patch("pipeline.data.advisory.get_client")
def test_get_advisory_matches_crop_alias(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = {
        "problem": "p", "cause": "c", "solution": "s", "prevention": "pr", "answer": "a",
    }

    result = get_advisory("paddy", "stem borer damage")  # "paddy" is an alias for "rice"

    assert result["crop"] == "rice"


@patch("pipeline.data.advisory.call_llm_json")
@patch("pipeline.data.advisory.get_client")
def test_get_advisory_falls_back_when_llm_fails(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = None

    result = get_advisory("cotton", "bollworm attack")

    assert result["crop"] == "cotton"
    assert "cotton" in result["answer"].lower()


@patch("pipeline.data.advisory.call_llm_json")
@patch("pipeline.data.advisory.get_client")
def test_get_advisory_infers_crop_from_situation_when_not_specified(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = None

    result = get_advisory(None, "brown planthopper on my paddy field")

    assert result["crop"] == "rice"
