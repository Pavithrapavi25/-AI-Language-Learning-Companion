from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator, MyMemoryTranslator
import sqlite3
import os

from nlp.language_detector import detect_language
from nlp.preprocessing import preprocess_text

app = Flask(__name__)
def detect_script(text):
    """Return 'telugu', 'kannada', or 'other' based on unicode range."""
    for char in text:
        code = ord(char)
        # Telugu Unicode block
        if 0x0C00 <= code <= 0x0C7F:
            return "telugu"
        # Kannada Unicode block
        if 0x0C80 <= code <= 0x0CFF:
            return "kannada"
    return "other"


def is_valid_output(translation, target_language):
    """Check if the translated text is in the correct script."""
    if not translation:
        return False

    script = detect_script(translation)

    if target_language == "te":
        return script == "telugu"
    if target_language == "kn":
        return script == "kannada"
    if target_language == "en":
        # English should be ASCII letters
        return all(ord(c) < 128 for c in translation if c.isalpha())

    return True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database", "history.db")


# Common accurate translations for frequently used phrases
# Common accurate translations for frequently used phrases
# Common accurate translations for frequently used phrases
COMMON_TRANSLATIONS = {
    # ---------- English -> Telugu ----------
    ("en", "te", "hello"): "నమస్కారం",
    ("en", "te", "hi"): "హాయ్",
    ("en", "te", "good morning"): "శుభోదయం",
    ("en", "te", "good afternoon"): "శుభ మధ్యాహ్నం",
    ("en", "te", "good evening"): "శుభ సాయంత్రం",
    ("en", "te", "good night"): "శుభరాత్రి",
    ("en", "te", "thank you"): "ధన్యవాదాలు",
    ("en", "te", "thanks"): "ధన్యవాదాలు",
    ("en", "te", "how are you"): "ఎలా ఉన్నారు",
    ("en", "te", "i love you"): "నేను నిన్ను ప్రేమిస్తున్నాను",
    ("en", "te", "what is your name"): "మీ పేరు ఏమిటి",
    ("en", "te", "my name is"): "నా పేరు",
    ("en", "te", "where are you from"): "మీరు ఎక్కడ నుండి వచ్చారు",
    ("en", "te", "how old are you"): "మీకు ఎన్ని సంవత్సరాలు",
    ("en", "te", "nice to meet you"): "మిమ్మల్ని కలవడం సంతోషం",
    ("en", "te", "please"): "దయచేసి",
    ("en", "te", "sorry"): "క్షమించండి",
    ("en", "te", "yes"): "అవును",
    ("en", "te", "no"): "కాదు",
    ("en", "te", "good"): "మంచి",
    ("en", "te", "water"): "నీళ్ళు",
    ("en", "te", "food"): "ఆహారం",

    # ---------- English -> Kannada ----------
    ("en", "kn", "hello"): "ನಮಸ್ಕಾರ",
    ("en", "kn", "hi"): "ಹಾಯ್",
    ("en", "kn", "good morning"): "ಶುಭೋದಯ",
    ("en", "kn", "good afternoon"): "ಶುಭ ಮಧ್ಯಾಹ್ನ",
    ("en", "kn", "good evening"): "ಶುಭ ಸಂಜೆ",
    ("en", "kn", "good night"): "ಶುಭ ರಾತ್ರಿ",
    ("en", "kn", "thank you"): "ಧನ್ಯವಾದ",
    ("en", "kn", "thanks"): "ಧನ್ಯವಾದ",
    ("en", "kn", "how are you"): "ಹೇಗಿದ್ದೀರಾ",
    ("en", "kn", "i love you"): "ನಾನು ನಿನ್ನನ್ನು ಪ್ರೀತಿಸುತ್ತೇನೆ",
    ("en", "kn", "what is your name"): "ನಿಮ್ಮ ಹೆಸರೇನು",
    ("en", "kn", "my name is"): "ನನ್ನ ಹೆಸರು",
    ("en", "kn", "where are you from"): "ನೀವು ಎಲ್ಲಿಂದ ಬಂದಿದ್ದೀರಿ",
    ("en", "kn", "how old are you"): "ನಿಮಗೆ ಎಷ್ಟು ವರ್ಷ",
    ("en", "kn", "nice to meet you"): "ನಿಮ್ಮನ್ನು ಭೇಟಿಯಾಗಿದ್ದು ಸಂತೋಷ",
    ("en", "kn", "please"): "ದಯವಿಟ್ಟು",
    ("en", "kn", "sorry"): "ಕ್ಷಮಿಸಿ",
    ("en", "kn", "yes"): "ಹೌದು",
    ("en", "kn", "no"): "ಇಲ್ಲ",
    ("en", "kn", "good"): "ಒಳ್ಳೆಯ",
    ("en", "kn", "water"): "ನೀರು",
    ("en", "kn", "food"): "ಆಹಾರ",

    # ---------- Telugu -> English ----------
    ("te", "en", "నమస్కారం"): "Hello",
    ("te", "en", "ధన్యవాదాలు"): "Thank you",
    ("te", "en", "శుభోదయం"): "Good morning",
    ("te", "en", "మీ పేరు ఏమిటి"): "What is your name",
    ("te", "en", "ఎలా ఉన్నారు"): "How are you",
    ("te", "en", "నేను నిన్ను ప్రేమిస్తున్నాను"): "I love you",

    # ---------- Kannada -> English ----------
    ("kn", "en", "ನಮಸ್ಕಾರ"): "Hello",
    ("kn", "en", "ಧನ್ಯವಾದ"): "Thank you",
    ("kn", "en", "ಶುಭೋದಯ"): "Good morning",
    ("kn", "en", "ನಿಮ್ಮ ಹೆಸರೇನು"): "What is your name",
    ("kn", "en", "ಹೇಗಿದ್ದೀರಾ"): "How are you",
    ("kn", "en", "ನಾನು ನಿನ್ನನ್ನು ಪ್ರೀತಿಸುತ್ತೇನೆ"): "I love you",

    # ---------- Telugu <-> Kannada ----------
    ("te", "kn", "నమస్కారం"): "ನಮಸ್ಕಾರ",
    ("te", "kn", "ధన్యవాదాలు"): "ಧನ್ಯವಾದ",
    ("te", "kn", "శుభోదయం"): "ಶುಭೋದಯ",

    ("kn", "te", "ನಮಸ್ಕಾರ"): "నమస్కారం",
    ("kn", "te", "ಧನ್ಯವಾದ"): "ధన్యవాదాలు",
    ("kn", "te", "ಶುಭೋದಯ"): "శుభోదయం",
}
def save_translation(
    source_text,
    source_language,
    target_language,
    translated_text
):
    conn = sqlite3.connect(DATABASE)

    conn.execute(
        """
        INSERT INTO translation_history
        (source_text, source_language, target_language, translated_text)
        VALUES (?, ?, ?, ?)
        """,
        (
            source_text,
            source_language,
            target_language,
            translated_text
        )
    )

    conn.commit()
    conn.close()


def get_translation_history():
    conn = sqlite3.connect(DATABASE)

    rows = conn.execute(
        """
        SELECT
            id,
            source_text,
            source_language,
            target_language,
            translated_text,
            created_at
        FROM translation_history
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    conn.close()

    history = []

    for row in rows:
        history.append({
            "id": row[0],
            "source_text": row[1],
            "source_language": row[2],
            "target_language": row[3],
            "translated_text": row[4],
            "created_at": row[5]
        })

    return history


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.get_json()

    text = data.get("text", "").strip()
    target_language = data.get("target_language", "en")

    if not text:
        return jsonify({
            "error": "Please enter some text."
        }), 400

    try:
        # Detect input language
        detected_language = detect_language(text)

        language_codes = {
            "English": "en",
            "Telugu": "te",
            "Kannada": "kn"
        }

        source_language = language_codes.get(detected_language)

        if not source_language:
            return jsonify({
                "error": "Only Telugu, Kannada, and English are supported."
            }), 400

        # NLP preprocessing and tokenization
        tokens = preprocess_text(text)

        # Check common translations first
        lookup_text = text.lower().strip()

        common_key = (
            source_language,
            target_language,
            lookup_text
        )

        if common_key in COMMON_TRANSLATIONS:
            translation = COMMON_TRANSLATIONS[common_key]

        elif source_language == target_language:
            translation = text
        else:
            translation = None

            # Try Google first
            try:
                translator = GoogleTranslator(
                    source=source_language,
                    target=target_language
                )
                candidate = translator.translate(text)
                if is_valid_output(candidate, target_language):
                    translation = candidate
            except Exception:
                translation = None

            # Fallback to MyMemory if Google failed or returned wrong script
            if not translation:
                mymemory_codes = {
                    "en": "en-GB",
                    "te": "te-IN",
                    "kn": "kn-IN"
                }

                try:
                    fallback = MyMemoryTranslator(
                        source=mymemory_codes[source_language],
                        target=mymemory_codes[target_language]
                    )
                    candidate = fallback.translate(text)
                    if is_valid_output(candidate, target_language):
                        translation = candidate
                except Exception:
                    translation = None

            # If both failed, give a clear message
            if not translation:
                return jsonify({
                    "error": (
                        "Online translators are busy or returned invalid "
                        "results. Try a common phrase like "
                        "'hello', 'thank you', or 'good morning'."
                    )
                }), 503

        # Save successful translation to SQLite
        save_translation(
            text,
            detected_language,
            target_language,
            translation
        )

        return jsonify({
            "translation": translation,
            "detected_language": detected_language,
            "tokens": tokens
        })

    except Exception as error:
        return jsonify({
            "error": f"Translation failed: {str(error)}"
        }), 500


@app.route("/history", methods=["GET"])
def translation_history():
    try:
        history = get_translation_history()

        return jsonify({
            "history": history
        })

    except Exception as error:
        return jsonify({
            "error": f"Unable to load translation history: {str(error)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)