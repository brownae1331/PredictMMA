"""
Utility functions for string manipulation.
"""

import unicodedata


def strip_accents(text: str) -> str:
    """Return a copy of *text* with accents/diacritics removed."""
    
    if not isinstance(text, str):
        return text
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)) 