from unittest.mock import patch

from pipeline.answer import generate_answer


@patch("pipeline.answer.call_llm_json")
@patch("pipeline.answer.get_client")
def test_generate_answer_happy_path(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = {
        "answer_english": "Onion is ₹1200 per quintal in Nashik.",
        "answer_local": "नासिक में प्याज़ ₹1200 प्रति क्विंटल है।",
        "language_code": "hi-IN",
    }

    result = generate_answer(
        intent={"crop": "onion", "location": "Nashik", "situation": "price inquiry", "question_type": "price"},
        data={
            "crop": "onion", "location": "Nashik", "price": "1200", "unit": "per quintal",
            "market": "Nashik APMC", "date": "2026-07-01", "source": "data.gov.in",
        },
        language_code="hi-IN",
    )

    assert result["answer_english"].startswith("Onion")
    assert result["language_code"] == "hi-IN"


@patch("pipeline.answer.call_llm_json")
@patch("pipeline.answer.get_client")
def test_generate_answer_falls_back_when_llm_fails(mock_get_client, mock_call_llm_json):
    mock_call_llm_json.return_value = None

    result = generate_answer(
        intent={"crop": "onion", "location": "Nashik", "situation": "price inquiry", "question_type": "price"},
        data={"price": "1200", "market": "Nashik APMC"},
        language_code="hi-IN",
    )

    assert "1200" in result["answer_english"]
    assert result["language_code"] == "hi-IN"
