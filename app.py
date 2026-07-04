import os
import tempfile

import streamlit as st

from i18n import t
from pipeline.transcribe import transcribe, from_text
from pipeline.translate import to_english
from pipeline.intent import extract_intent
from pipeline.router import route
from pipeline.answer import generate_answer

st.set_page_config(
    page_title="KisaanVaani",
    page_icon="🌾",
    layout="centered",
)

st.title("🌾 KisaanVaani")
st.caption("किसान की आवाज़ — Farmer's Voice Assistant")

LANG_OPTIONS = {
    "हिंदी (Hindi)": "hi-IN",
    "मराठी (Marathi)": "mr-IN",
    "ਪੰਜਾਬੀ (Punjabi)": "pa-IN",
    "English": "en-IN",
}
selected_lang_label = st.selectbox(
    "अपनी भाषा चुनें / Select your language",
    list(LANG_OPTIONS.keys()),
)
language_code = LANG_OPTIONS[selected_lang_label]

st.divider()

tab_voice, tab_text = st.tabs([t("tab_voice", language_code), t("tab_type", language_code)])

transcription_result = None

with tab_voice:
    st.markdown(t("voice_instructions", language_code))
    audio_value = st.audio_input(t("audio_input_label", language_code))

    if audio_value:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_value.getvalue())
            tmp_path = tmp.name
        try:
            transcription_result = transcribe(tmp_path, ui_language_code=language_code)
        finally:
            os.unlink(tmp_path)

        if transcription_result.get("error"):
            st.warning(transcription_result["error"])
            transcription_result = None
        else:
            st.success(
                f"{t('heard_label', language_code)}: **{transcription_result['text']}**  \n"
                f"{t('language_label', language_code)}: {transcription_result['language_name']}"
            )

with tab_text:
    typed_text = st.text_area(
        t("type_label", language_code),
        placeholder=t("type_placeholder", language_code),
        height=100,
    )
    if st.button(t("ask_button", language_code), type="primary", use_container_width=True):
        if typed_text.strip():
            transcription_result = from_text(typed_text.strip(), language_code)
        else:
            st.warning(t("warn_type_first", language_code))


def run_pipeline(transcription: dict) -> dict | None:
    """Runs translate -> intent -> route -> answer. Each stage already has
    its own fallback for a bad LLM response; this outer try/except is the
    last line of defense against anything else (a network blip, a data
    module raising) so one bad request never takes down the whole app for
    whoever's testing the live link."""
    lang_code = transcription["language_code"]
    raw_text = transcription["text"]

    try:
        with st.status(t("status_processing", language_code), expanded=True) as status:
            st.write(t("status_translating", language_code))
            english_text = to_english(raw_text, lang_code)

            st.write(t("status_understanding", language_code))
            intent = extract_intent(english_text)

            st.write(t("status_fetching", language_code))
            data = route(intent)

            st.write(t("status_generating", language_code))
            answer = generate_answer(intent, data, lang_code)

            status.update(label=t("status_done", language_code), state="complete", expanded=False)

        answer["question_type"] = intent.get("question_type")
        answer["crop"] = intent.get("crop")
        answer["location"] = intent.get("location")
        answer["situation"] = intent.get("situation")
        return answer

    except Exception as e:
        print(f"Pipeline error: {e}")
        st.error(t("error_generic", language_code))
        return None


if transcription_result:
    answer = run_pipeline(transcription_result)

    if answer:
        st.divider()

        local_ans = answer.get("answer_local") or answer.get("answer_english", "")
        eng_ans = answer.get("answer_english", "")

        st.subheader(t("answer_heading", language_code))
        st.info(local_ans)

        with st.expander(t("english_translation_expander", language_code)):
            st.write(eng_ans)

        with st.expander(t("debug_expander", language_code)):
            for key in ["question_type", "crop", "location", "situation"]:
                value = answer.get(key)
                if value:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")

        st.divider()
        st.caption(t("footer_sources", language_code))
