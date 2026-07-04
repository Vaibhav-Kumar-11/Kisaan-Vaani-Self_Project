from unittest.mock import MagicMock

from pipeline.llm_json import call_llm_json, extract_json


def test_extract_json_valid():
    assert extract_json('{"a": 1, "b": "two"}') == {"a": 1, "b": "two"}


def test_extract_json_with_surrounding_prose():
    raw = 'Here is the answer:\n{"a": 1}\nHope that helps!'
    assert extract_json(raw) == {"a": 1}


def test_extract_json_invalid_returns_none():
    assert extract_json("not json at all") is None
    assert extract_json("{broken json") is None


def _mock_response(content: str):
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = content
    return resp


def test_call_llm_json_success_first_try():
    client = MagicMock()
    client.chat.completions.create.return_value = _mock_response('{"answer": "ok"}')

    result = call_llm_json(client, "test-model", "prompt")

    assert result == {"answer": "ok"}
    assert client.chat.completions.create.call_count == 1


def test_call_llm_json_retries_once_then_succeeds():
    client = MagicMock()
    client.chat.completions.create.side_effect = [
        _mock_response("not valid json"),
        _mock_response('{"answer": "recovered"}'),
    ]

    result = call_llm_json(client, "test-model", "prompt")

    assert result == {"answer": "recovered"}
    assert client.chat.completions.create.call_count == 2


def test_call_llm_json_gives_up_after_two_failures():
    client = MagicMock()
    client.chat.completions.create.side_effect = [
        _mock_response("nope"),
        _mock_response("still nope"),
    ]

    result = call_llm_json(client, "test-model", "prompt")

    assert result is None
    assert client.chat.completions.create.call_count == 2
