"""Shared deterministic text normalization used by training and inference."""
import re
import html

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def validate_text(text: str, min_chars: int = 40) -> str:
    cleaned = clean_text(text)
    if len(cleaned) < min_chars or len(cleaned.split()) < 7:
        raise ValueError(f'Please enter at least {min_chars} characters and 7 words of news text.')
    if len(cleaned) > 100_000:
        raise ValueError('Text exceeds 100,000 characters.')
    return cleaned
