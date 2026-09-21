from langdetect import detect


def detect_language(text):
    """
    Detect whether the text is English, Telugu, or Kannada.
    """

    text = text.strip()

    if not text:
        return "Unsupported language"

    # 1. Check Telugu Unicode range
    for char in text:
        if 0x0C00 <= ord(char) <= 0x0C7F:
            return "Telugu"

    # 2. Check Kannada Unicode range
    for char in text:
        if 0x0C80 <= ord(char) <= 0x0CFF:
            return "Kannada"

    # 3. If all remaining letters are Latin (a-z, A-Z),
    #    treat it as English. This handles short English
    #    sentences that langdetect often misclassifies.
    letters = [c for c in text if c.isalpha()]

    if letters and all(ord(c) < 128 for c in letters):
        return "English"

    # 4. Fallback to langdetect for anything else
    try:
        language = detect(text)
    except Exception:
        return "Unsupported language"

    language_names = {
        "en": "English",
        "te": "Telugu",
        "kn": "Kannada"
    }

    return language_names.get(language, "Unsupported language")