"""Government scheme lookup.

Retrieval handles the facts (scheme name, benefit, eligibility, how to
apply) deterministically from knowledge/schemes.json — the LLM is only
asked to phrase a short answer around them. That split matters: a
hallucinated scheme benefit is a real harm (wrong money/eligibility info),
so the facts never pass through the LLM at all, only through retrieval.
"""
import json
from pathlib import Path

from pipeline.groq_client import get_client, MODEL
from pipeline.llm_json import call_llm_json
from retrieval import DocumentRetriever

SCHEMES_PATH = Path(__file__).resolve().parents[2] / "knowledge" / "schemes.json"
SCHEMES = json.loads(SCHEMES_PATH.read_text(encoding="utf-8"))


def _scheme_text(doc: dict) -> str:
    return f"{doc['name']} {doc['benefit']} {doc['eligibility']}"


_retriever = DocumentRetriever(SCHEMES, _scheme_text)


def _not_found(situation: str) -> dict:
    scheme_names = ", ".join(s["name"].split(" (")[0] for s in SCHEMES)
    return {
        "scheme_name": None,
        "benefit": None,
        "eligibility": None,
        "how_to_apply": None,
        "documents": None,
        "answer": f"I couldn't match that to a specific scheme. Try asking about: {scheme_names}.",
    }


def get_scheme_info(situation: str) -> dict:
    """
    Input : situation = "PM Kisan application help"
    Output: {"scheme_name", "benefit", "eligibility", "how_to_apply",
             "documents", "answer"}
    """
    matches = _retriever.search(situation or "", top_k=1)
    if not matches:
        return _not_found(situation)

    scheme = matches[0]
    print(f"Schemes      : retrieved '{scheme['name']}' for situation: {situation!r}")

    prompt = f"""You are a helpful assistant for Indian farmers.
Write a short, friendly 2-3 sentence answer for the farmer's situation
below, using only the scheme information provided. No jargon.

Scheme       : {scheme['name']}
Benefit      : {scheme['benefit']}
Eligibility  : {scheme['eligibility']}
How to apply : {scheme['how_to_apply']}

Farmer's situation: "{situation}"

Return ONLY a JSON object in exactly this format:
{{
    "answer": "your 2-3 sentence explanation here"
}}"""

    result = call_llm_json(get_client(), MODEL, prompt, temperature=0.0)
    answer = (result or {}).get("answer") or (
        f"{scheme['name']}: {scheme['benefit']}. Eligibility: {scheme['eligibility']}. "
        f"How to apply: {scheme['how_to_apply']}."
    )

    return {
        "scheme_name": scheme["name"],
        "benefit": scheme["benefit"],
        "eligibility": scheme["eligibility"],
        "how_to_apply": scheme["how_to_apply"],
        "documents": scheme["documents"],
        "answer": answer,
    }
