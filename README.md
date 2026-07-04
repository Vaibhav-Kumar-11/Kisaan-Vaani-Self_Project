# 🌾 KisaanVaani

KisaanVaani is a multilingual voice/text assistant for Indian farmers — ask a question about mandi prices, weather, government schemes, or crop advice, in Hindi, Marathi, Punjabi, or English, and get a spoken-language answer back.

It started as a hackathon project. I've since rebuilt it from scratch as a personal project: same core idea, but with real error handling, real tests, a proper retrieval layer instead of a hardcoded prompt blob, and an interface that actually works in the language you selected — not just the answer text.

## What it does

- **Two ways to ask**: record a voice question or type it.
- **Four languages**: Hindi, Marathi, Punjabi, English — and the *entire* interface (labels, buttons, status messages, not just the final answer) switches with the language you pick.
- **Four advisory modules**, routed automatically based on what you asked:
  - **Mandi prices** — live data from data.gov.in's agmarknet dataset
  - **Weather** — live forecast from Open-Meteo, geocoded for any Indian city/district/village, not a hardcoded list
  - **Government schemes** — PM-KISAN, crop insurance, KCC, irrigation subsidy, eNAM, soil health card
  - **Crop advisory** — sowing windows, fertilizer, common pests, water needs for 6 major crops

## How it's put together

```
voice/text input
   → transcribe (Sarvam STT) / typed text
   → translate to English (Sarvam)
   → extract intent (Groq — crop / location / question type)
   → route to the matching data module
   → generate a farmer-facing answer (Groq) + translate back
   → localized Streamlit UI
```

Each pipeline stage is a small, independently testable module under `pipeline/`. Nothing here needed a multi-agent framework — the four question types are a straightforward classification problem, so a plain if/elif router does the job without pretending it's more complex than it is.

## Decisions I'd actually defend in an interview

A few things I changed from the original that I can explain the reasoning for, not just describe:

- **Retrieval over hardcoded prompts.** Schemes and crop advisory used to be one giant string pasted into every LLM call. Now each scheme/crop is its own record in `knowledge/`, and a small TF-IDF + cosine-similarity retriever (`retrieval.py`) finds the right one before the LLM ever sees the question. I chose TF-IDF over embeddings on purpose — the knowledge base is a handful of short, keyword-heavy documents (crop names, scheme names), so lexical matching works well, and it skips pulling in `torch`/`sentence-transformers`, which would slow down cold starts on a free-tier deploy for no real benefit at this scale.
- **Retrieval carries the facts, the LLM only phrases them.** For schemes specifically, the LLM never generates the benefit amount or eligibility — those come straight from the JSON record. It only writes the 2-3 sentence explanation. A hallucinated scheme benefit is a real harm (wrong money information), so that risk is scoped to phrasing only, not facts.
- **Mandi price lookup is fuzzy-matched, not exact.** The government dataset's own filters are exact-string matches, so a farmer typing "Nasik" instead of "Nashik" used to just get zero results back. Now it fetches a batch of records for the crop and ranks them against the requested location with `rapidfuzz` client-side. There's a test (`test_get_mandi_price_fuzzy_matches_misspelled_market`) that reproduces this exact bug and confirms the fix.
- **Every LLM call that expects JSON back has a real fallback.** The original code did `raw.find("{")` / `json.loads()` with no error handling anywhere — one off-format response would crash the whole request. Now there's a shared retry-once-then-fallback helper (`pipeline/llm_json.py`), and every stage has a sensible degraded answer instead of a stack trace.
- **Full UI localization was a deliberate scope call, not a given.** The original interface mixed languages inconsistently — labels in English even when Hindi was selected, which defeats the point of an app aimed at people who may not read English comfortably. I localized the primary interface (labels, buttons, instructions, status text, the two most common warnings) across all four languages. I'm confident in the Hindi strings; Marathi and Punjabi are my best effort with standard, simple vocabulary, not verified by a native speaker — that's an honest gap, and the natural next step if this gets more use.
- **The mic widget is Streamlit's native `st.audio_input`,** not a third-party component. The original used `audio-recorder-streamlit`, which renders in an iframe with its own styling that never quite matched the rest of the app. Native `st.audio_input` follows the app's own theme automatically and removes a dependency that hadn't been updated in a while.

## Known limitations (said honestly, not hidden)

- **data.gov.in's mandi price API uses a shared public test key** that a huge number of student/hackathon projects use — while building this, I hit stretches where it was completely unresponsive (not just slow; a 30-second one-shot request got nothing back). The app fails fast (~12s worst case) and gives a sensible "couldn't find current price data" answer rather than hanging or crashing, but the honest fix is getting a personal, non-shared API key from data.gov.in.
- **Marathi and Punjabi UI strings** are my own best-effort translations of simple, standard vocabulary, not reviewed by a native speaker.
- **No conversation memory.** Each question is independent — asking about onion prices in Nashik and then "what about wheat?" won't carry the location over. Deliberately out of scope for this version to keep the surface area small and fully testable; a natural next step if it's worth the added state-management complexity.

## Testing

39 automated pytest tests under `tests/`, covering:
- Intent extraction and its fallback when the LLM output can't be parsed
- Routing logic for all four question types
- Weather (geocoding + forecast, including failure paths)
- Mandi price lookup, including the fuzzy-match fix above
- Scheme and advisory retrieval + their LLM-failure fallbacks
- Answer generation and its fallback template
- The shared JSON-retry helper's retry-once behavior specifically
- Translation, including a real quirk I found in testing: Sarvam's translator occasionally emits a CJK-style full stop ("。") in Indic text instead of a normal one — there's a small normalization step and a test for it

External APIs (Groq, Sarvam, data.gov.in, Open-Meteo) are mocked in tests so the suite runs fast and deterministically without needing real API keys. I also ran the full pipeline live with real keys across all four languages and all four modules before calling this done.

Run the suite:
```
pip install -r requirements-dev.txt
pytest
```

## Running it locally

```
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in:
```
GROQ_API_KEY = "..."
SARVAM_API_KEY = "..."
```

Then:
```
streamlit run app.py
```

## Deployment

Deployed on Streamlit Community Cloud: *(link goes here once live)*

## Stack

Streamlit · Groq (Llama 3.3 70B) · Sarvam AI (Saarika STT, Mayura translation) · scikit-learn (TF-IDF retrieval) · rapidfuzz · data.gov.in · Open-Meteo
