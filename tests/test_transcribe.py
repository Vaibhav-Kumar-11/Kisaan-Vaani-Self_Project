from unittest.mock import MagicMock, patch

from pipeline.transcribe import from_text, transcribe


def test_from_text_shapes_result():
    result = from_text("What is the onion price?", "hi-IN")

    assert result["text"] == "What is the onion price?"
    assert result["language_name"] == "Hindi"
    assert result["error"] is None


@patch("pipeline.transcribe.get_client")
def test_transcribe_handles_stt_failure_gracefully(mock_get_client):
    mock_client = MagicMock()
    mock_client.speech_to_text.transcribe.side_effect = Exception("network error")
    mock_get_client.return_value = mock_client

    result = transcribe("nonexistent_file.wav")

    assert result["error"] is not None
    assert result["text"] == ""


@patch("pipeline.transcribe.get_client")
def test_transcribe_handles_empty_speech(mock_get_client, tmp_path):
    audio_file = tmp_path / "silence.wav"
    audio_file.write_bytes(b"fake audio bytes")

    mock_response = MagicMock()
    mock_response.transcript = "   "
    mock_response.language_code = "hi-IN"
    mock_client = MagicMock()
    mock_client.speech_to_text.transcribe.return_value = mock_response
    mock_get_client.return_value = mock_client

    result = transcribe(str(audio_file))

    assert result["error"] is not None
    assert result["text"] == ""
