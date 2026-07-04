from pipeline.groq_client import get_client, MODEL
from pipeline.llm_json import call_llm_json

QUESTION_TYPES = {"price", "weather", "scheme", "advisory"}

FALLBACK_INTENT = {
    "crop": None,
    "location": None,
    "situation": None,
    "question_type": "advisory",
}


def extract_intent(english_text: str) -> dict:
    """
    Input  : English text (already translated).
    Output : {"crop", "location", "situation", "question_type"}.
             question_type is always one of price/weather/scheme/advisory.

    Falls back to a generic advisory intent (raw text as the situation) if
    the LLM can't produce valid JSON even after a retry, so the app keeps
    answering instead of crashing.
    """
    prompt = f"""
You are an AI assistant that extracts farming information.
Extract information from the farmer's question and return ONLY a JSON object.
No explanation, no extra text, just the JSON.

question_type must be ONE of: "price", "weather", "scheme", "advisory"

Rules:
- price    -> farmer asking about crop prices or mandi rates
- weather  -> farmer asking about rain, temperature, forecast
- scheme   -> farmer asking about government schemes or subsidies
- advisory -> farmer asking about farming advice, pest control, sowing

If any field is not mentioned, use null.

Farmer question: "{english_text}"

Return exactly this format:
{{
    "crop": "crop name or null",
    "location": "city or district or null",
    "situation": "one line description",
    "question_type": "price/weather/scheme/advisory"
}}
"""

    result = call_llm_json(get_client(), MODEL, prompt, temperature=0.0)

    if result is None or result.get("question_type") not in QUESTION_TYPES:
        print(f"Intent       : extraction failed, falling back to generic advisory for: {english_text!r}")
        return {**FALLBACK_INTENT, "situation": english_text}

    print(f"Question     : {english_text}")
    print(f"Crop         : {result.get('crop')}")
    print(f"Location     : {result.get('location')}")
    print(f"Question Type: {result.get('question_type')}")
    return result
