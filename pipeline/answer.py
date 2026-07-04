from pipeline.groq_client import get_client, MODEL
from pipeline.llm_json import call_llm_json

LANGUAGE_NAMES = {
    "hi-IN": "Hindi",
    "mr-IN": "Marathi",
    "pa-IN": "Punjabi",
    "en-IN": "English",
}


def _fallback_answer(data: dict, language_code: str) -> dict:
    """Used only if the LLM can't produce valid JSON even after a retry.
    Turns the raw data dict into a plain sentence so the app still answers
    something instead of crashing — just without the LLM's phrasing or
    translation."""
    parts = [f"{k.replace('_', ' ')}: {v}" for k, v in data.items() if v not in (None, "")]
    plain = ". ".join(parts) if parts else "Sorry, I couldn't find specific data for that."
    return {
        "answer_english": plain,
        "answer_local": plain,
        "language_code": language_code,
    }


def generate_answer(intent: dict, data: dict, language_code: str) -> dict:
    """
    Input : intent        = {"crop", "location", "situation", "question_type"}
            data          = raw dict from mandi/weather/schemes/advisory
            language_code = "hi-IN" / "mr-IN" / "pa-IN" / "en-IN"

    Output: {"answer_english", "answer_local", "language_code"}
    """
    question_type = intent.get("question_type", "advisory")
    crop = intent.get("crop")
    location = intent.get("location")
    situation = intent.get("situation")

    data_context = "\n".join(f"{k}: {v}" for k, v in data.items())
    language_name = LANGUAGE_NAMES.get(language_code, "Hindi")

    prompt = f"""You are KisaanVaani, a helpful AI assistant for Indian farmers.
Generate a clear, friendly answer for the farmer using the data provided.

Farmer's question type : {question_type}
Crop                    : {crop if crop else "not specified"}
Location                : {location if location else "not specified"}
Situation               : {situation}

DATA FROM SOURCE:
{data_context}

Instructions:
- Write a clear, simple answer that directly helps the farmer
- Use specific numbers and facts from the data above
- Keep it short — 2 to 3 sentences max
- Avoid technical jargon — farmer must understand it easily

Return ONLY a JSON object in exactly this format:
{{
    "answer_english" : "your answer in English",
    "answer_local"   : "same answer translated to {language_name}",
    "language_code"  : "{language_code}"
}}"""

    print(f"Answer       : generating for question_type={question_type}, language={language_name}")

    result = call_llm_json(get_client(), MODEL, prompt, temperature=0.1)

    if result is None or not result.get("answer_english"):
        print("Answer       : LLM failed to produce a valid answer, using fallback template")
        return _fallback_answer(data, language_code)

    result.setdefault("language_code", language_code)
    print(f"Answer       : {result.get('answer_english')}")
    return result
