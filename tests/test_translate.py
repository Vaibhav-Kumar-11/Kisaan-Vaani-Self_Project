from unittest.mock import MagicMock, patch

from pipeline.translate import to_english, to_indic


def test_to_english_same_language_short_circuits():
    assert to_english("Hello", "en-IN") == "Hello"


def test_to_indic_same_language_short_circuits():
    assert to_indic("Hello", "en-IN") == "Hello"


@patch("pipeline.translate.get_client")
def test_to_english_translates(mock_get_client):
    mock_client = MagicMock()
    mock_client.text.translate.return_value = MagicMock(translated_text="What is the onion price?")
    mock_get_client.return_value = mock_client

    result = to_english("प्याज का भाव क्या है", "hi-IN")

    assert result == "What is the onion price?"


@patch("pipeline.translate.get_client")
def test_to_english_falls_back_to_original_on_error(mock_get_client):
    mock_client = MagicMock()
    mock_client.text.translate.side_effect = Exception("api down")
    mock_get_client.return_value = mock_client

    original = "प्याज का भाव क्या है"
    result = to_english(original, "hi-IN")

    assert result == original


@patch("pipeline.translate.get_client")
def test_to_indic_normalizes_stray_cjk_punctuation(mock_get_client):
    # Observed in real testing: Sarvam's translator occasionally emits a
    # CJK full stop ("。") in Indic output instead of a normal period.
    mock_client = MagicMock()
    mock_client.text.translate.return_value = MagicMock(translated_text="ਸਲਾਹ ਲਈ ਸੰਪਰਕ ਕਰੋ。")
    mock_get_client.return_value = mock_client

    result = to_indic("Contact for advice.", "pa-IN")

    assert "。" not in result
    assert result.endswith(".")
