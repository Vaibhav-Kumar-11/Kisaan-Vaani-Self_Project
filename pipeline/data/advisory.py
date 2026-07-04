"""Crop advisory lookup.

Retrieval finds the matching crop's facts (sowing/harvest window,
fertilizer, common pests, water needs) from knowledge/crops.json; the LLM
then diagnoses the farmer's specific situation against those facts. Unlike
schemes.py, this genuinely needs LLM reasoning (matching a described
symptom to a likely cause), not just phrasing — so it stays in the prompt.
"""
import json
from pathlib import Path

from pipeline.groq_client import get_client, MODEL
from pipeline.llm_json import call_llm_json
from retrieval import DocumentRetriever

CROPS_PATH = Path(__file__).resolve().parents[2] / "knowledge" / "crops.json"
CROPS = json.loads(CROPS_PATH.read_text(encoding="utf-8"))

GENERAL_ADVICE = (
    "Neem-based pesticides are safe and effective for most pests. Never "
    "spray pesticides during flowering — it kills pollinators. Rotate "
    "pesticide groups to prevent resistance. Contact your nearest Krishi "
    "Vigyan Kendra (KVK) for free soil testing."
)


def _crop_text(doc: dict) -> str:
    aliases = " ".join(doc.get("aliases", []))
    return f"{doc['crop']} {aliases} {doc['pests']} {doc['fertilizer']}"


_retriever = DocumentRetriever(CROPS, _crop_text)


def _match_crop(crop: str | None, situation: str | None) -> dict | None:
    if crop:
        crop_lower = crop.lower()
        for c in CROPS:
            names = [c["crop"]] + c.get("aliases", [])
            if crop_lower in [n.lower() for n in names]:
                return c

    query = f"{crop or ''} {situation or ''}".strip()
    matches = _retriever.search(query, top_k=1)
    return matches[0] if matches else None


def _not_found(crop, situation) -> dict:
    crop_names = ", ".join(c["crop"] for c in CROPS)
    return {
        "crop": crop,
        "problem": situation,
        "cause": None,
        "solution": None,
        "prevention": None,
        "answer": f"I don't have specific guidance for that crop yet. Try: {crop_names}.",
    }


def get_advisory(crop: str | None, situation: str) -> dict:
    """
    Input : crop, situation = "wheat", "yellow leaves on wheat plants"
    Output: {"crop", "problem", "cause", "solution", "prevention", "answer"}
    """
    matched = _match_crop(crop, situation)
    if matched is None:
        return _not_found(crop, situation)

    print(f"Advisory     : matched crop '{matched['crop']}' for situation: {situation!r}")

    prompt = f"""You are an expert agricultural advisor for Indian farmers.
Use the crop information below to diagnose the farmer's situation and give
practical advice.

CROP INFORMATION:
Crop      : {matched['crop']}
Sowing    : {matched['sowing']}
Harvest   : {matched['harvest']}
Pests     : {matched['pests']}
Fertilizer: {matched['fertilizer']}
Water     : {matched['water']}

General guidance: {GENERAL_ADVICE}

Farmer's situation: "{situation}"

Return ONLY a JSON object in exactly this format:
{{
    "problem"    : "identified problem in one line",
    "cause"      : "most likely cause",
    "solution"   : "immediate action the farmer should take",
    "prevention" : "how to prevent this in future",
    "answer"     : "2-3 sentence practical advice in simple language"
}}"""

    result = call_llm_json(get_client(), MODEL, prompt, temperature=0.0)

    if result is None:
        return {
            "crop": matched["crop"],
            "problem": situation,
            "cause": None,
            "solution": None,
            "prevention": None,
            "answer": (
                f"For {matched['crop']}: fertilizer {matched['fertilizer']}. "
                f"Water needs: {matched['water']}. Watch for {matched['pests']}."
            ),
        }

    result["crop"] = matched["crop"]
    return result
