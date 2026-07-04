from unittest.mock import patch

from pipeline.data.schemes import get_scheme_info


@patch("pipeline.data.schemes.call_llm_json")
@patch("pipeline.data.schemes.get_client")
def test_get_scheme_info_retrieves_correct_scheme(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = {"answer": "You get ₹6000 a year in three parts."}

    result = get_scheme_info("How do I apply for PM Kisan?")

    assert "PM-KISAN" in result["scheme_name"]
    assert result["answer"] == "You get ₹6000 a year in three parts."


@patch("pipeline.data.schemes.call_llm_json")
@patch("pipeline.data.schemes.get_client")
def test_get_scheme_info_falls_back_when_llm_fails(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = None

    result = get_scheme_info("I want crop insurance for my wheat")

    assert "Fasal Bima" in result["scheme_name"]
    assert result["benefit"] in result["answer"]


def test_get_scheme_info_no_match_for_empty_situation():
    result = get_scheme_info("")
    assert result["scheme_name"] is None
