
import re
import nltk

from nltk.tokenize import word_tokenize

# Ensure the tokenizer data is available on Render
nltk.download("punkt_tab", quiet=True)


def preprocess_text(text):
    """
    Clean text and tokenize it.
    """

    # Convert multiple spaces into a single space
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenize the text
    tokens = word_tokenize(text)

    return tokens
