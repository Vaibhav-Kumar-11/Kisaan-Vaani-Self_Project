"""UI chrome translations for all 4 supported languages.

Scope decision worth being upfront about: this localizes the primary,
always-visible interface — labels, buttons, instructions, status text,
headings — plus the two most likely user-facing warnings (recording
failed / no speech detected). It does NOT localize the deep fallback
templates inside answer.py/schemes.py/advisory.py that only fire if the
LLM call fails twice in a row (rare, and would mean translating the whole
knowledge base, not just UI copy). The brand name and tagline also stay
fixed across languages, same as most products don't translate their own
name.

Hindi strings are ones I'm confident about. Marathi and Punjabi are my
best effort with standard, simple vocabulary — not verified by a native
speaker, and called out as such in the README.
"""

UI_STRINGS = {
    "en-IN": {
        "select_language": "Select your language",
        "tab_voice": "Voice",
        "tab_type": "Type",
        "voice_instructions": "Click the mic to start recording, click again to stop.",
        "audio_input_label": "Ask your question",
        "heard_label": "Heard",
        "language_label": "Language",
        "type_label": "Type your question here",
        "type_placeholder": "e.g. What is the onion price in Nashik?",
        "ask_button": "Ask",
        "warn_type_first": "Please type a question first.",
        "status_processing": "Processing your question…",
        "status_translating": "Translating to English…",
        "status_understanding": "Understanding your question…",
        "status_fetching": "Fetching your answer…",
        "status_generating": "Putting together your answer…",
        "status_done": "Done!",
        "answer_heading": "Answer",
        "english_translation_expander": "English translation",
        "debug_expander": "Pipeline details",
        "error_generic": "Something went wrong answering that — please try rephrasing your question, or try again in a moment.",
        "footer_sources": "Data sources: data.gov.in · open-meteo.com · Sarvam AI · Groq",
        "err_stt_failed": "Couldn't process that recording. Please try again or type your question.",
        "err_no_speech": "Didn't catch any speech in that recording. Please try again.",
        "record_again_button": "🔄 Record again",
    },
    "hi-IN": {
        "select_language": "अपनी भाषा चुनें",
        "tab_voice": "आवाज़",
        "tab_type": "टाइप करें",
        "voice_instructions": "रिकॉर्डिंग शुरू करने के लिए माइक दबाएँ, रोकने के लिए फिर से दबाएँ।",
        "audio_input_label": "अपना सवाल पूछें",
        "heard_label": "सुना गया",
        "language_label": "भाषा",
        "type_label": "अपना सवाल यहाँ लिखें",
        "type_placeholder": "जैसे: नाशिक में प्याज़ का भाव क्या है?",
        "ask_button": "पूछें",
        "warn_type_first": "कृपया पहले अपना सवाल लिखें।",
        "status_processing": "आपका सवाल समझा जा रहा है…",
        "status_translating": "अंग्रेज़ी में अनुवाद हो रहा है…",
        "status_understanding": "सवाल समझा जा रहा है…",
        "status_fetching": "जानकारी ली जा रही है…",
        "status_generating": "जवाब तैयार किया जा रहा है…",
        "status_done": "हो गया!",
        "answer_heading": "जवाब",
        "english_translation_expander": "अंग्रेज़ी अनुवाद",
        "debug_expander": "तकनीकी जानकारी",
        "error_generic": "जवाब देने में कोई समस्या हुई — कृपया सवाल को दोबारा लिखें या थोड़ी देर बाद फिर कोशिश करें।",
        "footer_sources": "डेटा स्रोत: data.gov.in · open-meteo.com · Sarvam AI · Groq",
        "err_stt_failed": "रिकॉर्डिंग समझ नहीं आई। कृपया फिर से कोशिश करें या अपना सवाल लिखें।",
        "err_no_speech": "रिकॉर्डिंग में कोई आवाज़ नहीं मिली। कृपया फिर से कोशिश करें।",
        "record_again_button": "🔄 फिर से रिकॉर्ड करें",
    },
    "mr-IN": {
        "select_language": "तुमची भाषा निवडा",
        "tab_voice": "आवाज",
        "tab_type": "टाइप करा",
        "voice_instructions": "रेकॉर्डिंग सुरू करण्यासाठी माइकवर दाबा, थांबवण्यासाठी पुन्हा दाबा.",
        "audio_input_label": "तुमचा प्रश्न विचारा",
        "heard_label": "ऐकले",
        "language_label": "भाषा",
        "type_label": "तुमचा प्रश्न इथे लिहा",
        "type_placeholder": "उदा: नाशिकमध्ये कांद्याचा भाव काय आहे?",
        "ask_button": "विचारा",
        "warn_type_first": "कृपया आधी तुमचा प्रश्न लिहा.",
        "status_processing": "तुमचा प्रश्न समजून घेतला जात आहे…",
        "status_translating": "इंग्रजीमध्ये भाषांतर होत आहे…",
        "status_understanding": "प्रश्न समजून घेतला जात आहे…",
        "status_fetching": "माहिती मिळवली जात आहे…",
        "status_generating": "उत्तर तयार केले जात आहे…",
        "status_done": "झाले!",
        "answer_heading": "उत्तर",
        "english_translation_expander": "इंग्रजी भाषांतर",
        "debug_expander": "तांत्रिक माहिती",
        "error_generic": "उत्तर देताना काहीतरी चूक झाली — कृपया प्रश्न पुन्हा लिहा किंवा थोड्या वेळाने पुन्हा प्रयत्न करा.",
        "footer_sources": "डेटा स्रोत: data.gov.in · open-meteo.com · Sarvam AI · Groq",
        "err_stt_failed": "रेकॉर्डिंग समजले नाही. कृपया पुन्हा प्रयत्न करा किंवा प्रश्न लिहा.",
        "err_no_speech": "रेकॉर्डिंगमध्ये आवाज सापडला नाही. कृपया पुन्हा प्रयत्न करा.",
        "record_again_button": "🔄 पुन्हा रेकॉर्ड करा",
    },
    "pa-IN": {
        "select_language": "ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ",
        "tab_voice": "ਆਵਾਜ਼",
        "tab_type": "ਟਾਈਪ ਕਰੋ",
        "voice_instructions": "ਰਿਕਾਰਡਿੰਗ ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਮਾਈਕ ਦਬਾਓ, ਰੋਕਣ ਲਈ ਦੁਬਾਰਾ ਦਬਾਓ।",
        "audio_input_label": "ਆਪਣਾ ਸਵਾਲ ਪੁੱਛੋ",
        "heard_label": "ਸੁਣਿਆ",
        "language_label": "ਭਾਸ਼ਾ",
        "type_label": "ਆਪਣਾ ਸਵਾਲ ਇੱਥੇ ਲਿਖੋ",
        "type_placeholder": "ਜਿਵੇਂ: ਨਾਸਿਕ ਵਿੱਚ ਪਿਆਜ਼ ਦਾ ਭਾਅ ਕੀ ਹੈ?",
        "ask_button": "ਪੁੱਛੋ",
        "warn_type_first": "ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ ਆਪਣਾ ਸਵਾਲ ਲਿਖੋ।",
        "status_processing": "ਤੁਹਾਡਾ ਸਵਾਲ ਸਮਝਿਆ ਜਾ ਰਿਹਾ ਹੈ…",
        "status_translating": "ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਅਨੁਵਾਦ ਹੋ ਰਿਹਾ ਹੈ…",
        "status_understanding": "ਸਵਾਲ ਸਮਝਿਆ ਜਾ ਰਿਹਾ ਹੈ…",
        "status_fetching": "ਜਾਣਕਾਰੀ ਲਈ ਜਾ ਰਹੀ ਹੈ…",
        "status_generating": "ਜਵਾਬ ਤਿਆਰ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ…",
        "status_done": "ਹੋ ਗਿਆ!",
        "answer_heading": "ਜਵਾਬ",
        "english_translation_expander": "ਅੰਗਰੇਜ਼ੀ ਅਨੁਵਾਦ",
        "debug_expander": "ਤਕਨੀਕੀ ਜਾਣਕਾਰੀ",
        "error_generic": "ਜਵਾਬ ਦੇਣ ਵਿੱਚ ਕੋਈ ਸਮੱਸਿਆ ਆਈ — ਕਿਰਪਾ ਕਰਕੇ ਸਵਾਲ ਦੁਬਾਰਾ ਲਿਖੋ ਜਾਂ ਥੋੜ੍ਹੀ ਦੇਰ ਬਾਅਦ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "footer_sources": "ਡਾਟਾ ਸਰੋਤ: data.gov.in · open-meteo.com · Sarvam AI · Groq",
        "err_stt_failed": "ਰਿਕਾਰਡਿੰਗ ਸਮਝ ਨਹੀਂ ਆਈ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ ਜਾਂ ਆਪਣਾ ਸਵਾਲ ਲਿਖੋ।",
        "err_no_speech": "ਰਿਕਾਰਡਿੰਗ ਵਿੱਚ ਕੋਈ ਆਵਾਜ਼ ਨਹੀਂ ਮਿਲੀ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "record_again_button": "🔄 ਦੁਬਾਰਾ ਰਿਕਾਰਡ ਕਰੋ",
    },
}


def t(key: str, language_code: str) -> str:
    strings = UI_STRINGS.get(language_code, UI_STRINGS["en-IN"])
    return strings.get(key, UI_STRINGS["en-IN"].get(key, key))
