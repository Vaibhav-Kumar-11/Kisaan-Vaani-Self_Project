"""Shared helper for Groq calls that expect a JSON object back.

The original hackathon code did `raw.find("{")` / `json.loads()` with no
error handling anywhere — one off-format response from the model would
crash the whole Streamlit request. This retries once with the model's own
bad output fed back to it and a stricter correction, then gives up and lets
the caller decide its own fallback (each pipeline stage has a different
safe default, so this module doesn't own that decision).
"""
import json


def extract_json(raw: str) -> dict | None:
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError:
        return None


def call_llm_json(client, model: str, prompt: str, temperature: float = 0.0) -> dict | None:
    messages = [{"role": "user", "content": prompt}]

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
        except Exception as e:
            print(f"LLM call failed (attempt {attempt + 1}): {e}")
            continue

        raw = response.choices[0].message.content.strip()
        result = extract_json(raw)
        if result is not None:
            return result

        print(f"LLM returned unparseable JSON (attempt {attempt + 1}): {raw[:200]!r}")
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": raw},
            {"role": "user", "content": (
                "That was not valid JSON. Return ONLY a valid JSON object, "
                "with no extra text, no markdown code fences, nothing else."
            )},
        ]

    return None
