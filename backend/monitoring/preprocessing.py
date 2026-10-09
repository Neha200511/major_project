"""
Text Preprocessing Module for Child-Safe Digital Environment Manager.
Provides text cleaning, tokenization, and feature extraction utilities.
"""

import re
import string
from typing import List, Dict

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Emoji pattern for detection
EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"
    "\u3030]+",
    flags=re.UNICODE,
)


def clean_text(text: str) -> str:
    """Clean text: lowercase, remove excessive whitespace, normalize contractions and slang."""
    if not text or not isinstance(text, str):
        return ""
    try:
        from ml.preprocessing import normalize_text
        return normalize_text(text)
    except ImportError:
        # Fallback if ml package not in path
        text = text.lower().strip()
        text = re.sub(r'[\t\r]+', ' ', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r"won[\u2019']t", "will not", text)
        text = re.sub(r"can[\u2019']t", "cannot", text)
        text = re.sub(r"n[\u2019']t", " not", text)
        text = re.sub(r"[\u2019']re", " are", text)
        text = re.sub(r"[\u2019']s", " is", text)
        text = re.sub(r"[\u2019']d", " would", text)
        text = re.sub(r"[\u2019']ll", " will", text)
        text = re.sub(r"[\u2019']ve", " have", text)
        text = re.sub(r"[\u2019']m", " am", text)
        return text.strip()



def tokenize(text: str) -> List[str]:
    """Tokenize text into a list of words."""
    cleaned = clean_text(text)
    if not cleaned:
        return []
    # Split on whitespace and punctuation but keep emoji
    tokens = re.findall(r"[\w]+|[^\w\s]", cleaned)
    # Filter out single punctuation characters
    tokens = [t for t in tokens if len(t) > 0 and (len(t) > 1 or t.isalnum())]
    return tokens


def extract_features(text: str) -> Dict:
    """
    Extract features from text for analysis.
    Returns dict with: word_count, avg_word_length, has_question, 
    has_exclamation, has_emoji, sentiment_score, uppercase_ratio
    """
    if not text or not isinstance(text, str):
        return {
            'word_count': 0,
            'avg_word_length': 0.0,
            'has_question': False,
            'has_exclamation': False,
            'has_emoji': False,
            'sentiment_score': 0.0,
            'uppercase_ratio': 0.0,
        }
    
    words = tokenize(text)
    word_count = len(words)
    
    # Average word length
    alpha_words = [w for w in words if w.isalpha()]
    avg_word_length = (
        sum(len(w) for w in alpha_words) / len(alpha_words)
        if alpha_words else 0.0
    )
    
    # Punctuation detection
    has_question = '?' in text
    has_exclamation = '!' in text
    
    # Emoji detection
    has_emoji = bool(EMOJI_PATTERN.search(text))
    
    # Sentiment score using TextBlob
    sentiment_score = 0.0
    if TEXTBLOB_AVAILABLE:
        try:
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity  # -1.0 to 1.0
        except Exception:
            sentiment_score = 0.0
    
    # Uppercase ratio (on original text)
    alpha_chars = [c for c in text if c.isalpha()]
    uppercase_ratio = (
        sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if alpha_chars else 0.0
    )
    
    return {
        'word_count': word_count,
        'avg_word_length': round(avg_word_length, 2),
        'has_question': has_question,
        'has_exclamation': has_exclamation,
        'has_emoji': has_emoji,
        'sentiment_score': round(sentiment_score, 3),
        'uppercase_ratio': round(uppercase_ratio, 3),
    }


def get_conversation_text(messages: list, window: int = 10) -> str:
    """
    Concatenate recent messages into a context string.
    
    Args:
        messages: List of message dicts with at least 'content' and optionally 'sender_id'
        window: Number of recent messages to include
    
    Returns:
        Concatenated string of recent messages for context analysis
    """
    if not messages:
        return ""
    
    recent = messages[-window:] if len(messages) > window else messages
    
    parts = []
    for msg in recent:
        content = msg.get('content', '')
        sender = msg.get('sender_id', 'unknown')
        if content:
            parts.append(f"[{sender}]: {content}")
    
    return "\n".join(parts)
