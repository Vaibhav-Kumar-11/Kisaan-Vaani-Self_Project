from pipeline.sarvam_client import get_client

TRANSLATE_MODEL = "mayura:v1"

# Observed in real testing: Sarvam's translator occasionally emits a
# CJK-style full stop ("。") in Indic output instead of a normal one —
# looks like a stray bug to anyone reading the answer closely, so it's
# worth normalizing rather than passing through verbatim.
_PUNCTUATION_FIXES = {"。": "."}


def _normalize(text: str) -> str:
    for wrong, right in _PUNCTUATION_FIXES.items():
        text = text.replace(wrong, right)
    return text


def _translate(text: str, source: str, target: str) -> str:
    if source == target:
        return text

    try:
        response = get_client().text.translate(
            input=text,
            source_language_code=source,
            target_language_code=target,
            speaker_gender="Male",
            mode="formal",
            model=TRANSLATE_MODEL,
        )
        return _normalize(response.translated_text)
    except Exception as e:
        print(f"Translate    : {source}->{target} failed — {e}; falling back to original text")
        return text


def to_english(text: str, language_code: str) -> str:
    return _translate(text, source=language_code, target="en-IN")


def to_indic(text: str, language_code: str) -> str:
    return _translate(text, source="en-IN", target=language_code)
