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

## Why some things are built the way they are

- **Retrieval instead of one giant prompt.** Schemes and crop advisory used to be one big string pasted into every LLM call. Now each scheme/crop is its own record under `knowledge/`, and a small TF-IDF + cosine-similarity search (`retrieval.py`) finds the right one before the LLM even sees the question. I went with TF-IDF over embeddings mainly because the knowledge base is small and the queries are keyword-heavy (crop names, scheme names) — pulling in `sentence-transformers`/`torch` for this would slow down cold starts on a free-tier deploy without actually improving the results.
- **Retrieval carries the facts, the LLM only writes the phrasing.** For schemes specifically, the LLM never invents the benefit amount or eligibility — those always come straight from the JSON record, and the model only writes the short explanation around them. Getting a scheme's benefit wrong is a real problem (it's someone's money), so I didn't want that part depending on the model getting it right every time.
- **Mandi price lookup is fuzzy-matched, not exact.** The government dataset's own filters only match commodity/market names exactly, so someone typing "Nasik" instead of "Nashik" used to just get nothing back. Now it pulls a batch of records for the crop and ranks them against whatever location was given, using `rapidfuzz`. There's a test that reproduces this exact typo and checks the fix.
- **The mandi API also turned out to be genuinely unreliable, not just slow.** It's a public test key shared by a huge number of similar projects, and I had stretches during development where even a 30-second request got nothing back. Rather than show "price unavailable" every time that happens, successful lookups are cached for a few hours (prices lag 1-2 days anyway, so this doesn't serve stale data in any way that matters), and if a live call fails outright, there's a small reference-price table for the crops in the knowledge base — clearly labeled as an estimate, not a live number, so it's still honest.
- **Every LLM call that expects JSON back has a real fallback.** The original code did `raw.find("{")` / `json.loads()` with nothing around it — one slightly off response would crash the whole request. There's a small retry-once helper (`pipeline/llm_json.py`) now, and every stage has an actual fallback answer instead of a stack trace.
- **The interface itself changes language, not just the answer.** The original mixed languages — English labels even when Hindi was selected, which kind of defeats the point for someone who might not read English comfortably. Labels, buttons, instructions, and status messages all switch with the language dropdown now. Hindi I'm confident about. Marathi and Punjabi are my own translations using fairly standard, simple words — I haven't had a native speaker check them yet, so the phrasing could probably be tightened.
- **The mic widget is Streamlit's own `st.audio_input`,** not a third-party component. The old one (`audio-recorder-streamlit`) rendered in an iframe with its own styling that never quite matched the rest of the page; the native one just follows the app's theme.

## Known limitations

- **data.gov.in's mandi API is shared and unreliable.** Even with the caching and reference-price fallback above, live prices won't always be current — the real fix is getting a personal (non-shared) API key from data.gov.in instead of using the public test key.
- **Marathi and Punjabi interface text** is my own translation, not checked by a native speaker.
- **No conversation memory.** Each question is independent — asking about onion prices in Nashik and then "what about wheat?" won't carry the location over. Left out on purpose to keep the scope small and fully testable; would add if this ever needed to feel more like a conversation.

## Testing

42 automated pytest tests under `tests/`, covering:
- Intent extraction and its fallback when the LLM output can't be parsed
- Routing logic for all four question types
- Weather (geocoding + forecast, including failure paths)
- Mandi price lookup — the fuzzy-match fix, the caching, and the reference-price fallback
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

Live on Streamlit Community Cloud: **[kisaan-vaani.streamlit.app](https://kisaan-vaani.streamlit.app/)**

If it's been quiet for a while, the first load can take 30-60 seconds while the free-tier instance wakes up — that's normal, not a bug.

## Stack

Streamlit · Groq (Llama 3.3 70B) · Sarvam AI (Saarika STT, Mayura translation) · scikit-learn (TF-IDF retrieval) · rapidfuzz · data.gov.in · Open-Meteo
