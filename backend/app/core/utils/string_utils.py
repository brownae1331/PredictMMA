import unicodedata
from app.schemas.predict_schemas import Method
import pycountry

def strip_accents(text: str) -> str:
    """Return a copy of *text* with accents/diacritics removed."""
    
    if not isinstance(text, str):
        return text
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))

def get_flag_image_url(location: str) -> str:
    """
    Finds a flag image from the location string using flagcdn.com.
    """
    SPECIAL_CASES = {
        "England": "gb-eng",
        "Scotland": "gb-sct",
        "Wales": "gb-wls",
        "Northern Ireland": "gb-nir",
        "Russia": "ru",
    }

    country_name = location.split(",")[-1].strip()
    country = pycountry.countries.get(name=country_name)
    country_code = country.alpha_2 if country else ""

    if country_name in SPECIAL_CASES:
        country_code = SPECIAL_CASES[country_name]

    if not country_code:
        return ""

    return f"https://flagcdn.com/w320/{country_code.lower()}.png"

def simplify_method(method: str) -> Method:
    """Simplify a method string to the simplified :class:`Method` enum."""

    method_lower = method.lower()

    if "submission" in method_lower:
        return Method.SUBMISSION
    if "tko" in method_lower or "ko" in method_lower:
        return Method.KO
    if "decision" in method_lower:
        return Method.DECISION

    return Method.KO