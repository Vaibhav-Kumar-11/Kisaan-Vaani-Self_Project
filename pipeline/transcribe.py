"""Voice/text input -> a common {text, language_code, language_name} shape
so the rest of the pipeline doesn't care which input mode was used."""
from i18n import t
from pipeline.sarvam_client import get_client

LANG_MAP = {
    "hi-IN": "Hindi",
    "mr-IN": "Marathi",
    "pa-IN": "Punjabi",
    "en-IN": "English",
}

STT_MODEL = "saarika:v2.5"


def transcribe(audio_path: str, ui_language_code: str = "en-IN") -> dict:
    """
    Input : path to a recorded audio file. ui_language_code is the
            language the user has the *interface* set to (not necessarily
            what they spoke) — used only to localize the two warnings
            below, since those are common enough to be worth translating.
    Output: {"text", "language_code", "language_name", "error"}.
            "error" is None on success, or a short farmer-facing message
            if Sarvam couldn't make sense of the recording — the caller
            shows this instead of letting an exception crash the request.
    """
    try:
        with open(audio_path, "rb") as f:
            response = get_client().speech_to_text.transcribe(
                file=("audio.wav", f, "audio/wav"),
                model=STT_MODEL,
                language_code="unknown",
            )
    except Exception as e:
        print(f"Transcribe   : STT call failed — {e}")
        return {
            "text": "",
            "language_code": None,
            "language_name": None,
            "error": t("err_stt_failed", ui_language_code),
        }

    text = (response.transcript or "").strip()
    language_name = LANG_MAP.get(response.language_code, response.language_code)

    if not text:
        return {
            "text": "",
            "language_code": response.language_code,
            "language_name": language_name,
            "error": t("err_no_speech", ui_language_code),
        }

    print(f"Transcribed  : {text}")
    print(f"Language     : {language_name}")
    return {
        "text": text,
        "language_code": response.language_code,
        "language_name": language_name,
        "error": None,
    }


def from_text(text: str, language_code: str = "hi-IN") -> dict:
    """Typed input -> same dict shape as transcribe()."""
    return {
        "text": text,
        "language_code": language_code,
        "language_name": LANG_MAP.get(language_code, language_code),
        "error": None,
    }
