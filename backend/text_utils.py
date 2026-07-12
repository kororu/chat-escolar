import re
from unicodedata import normalize


def normalize_text(value: str) -> str:
    without_accents = normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    clean_value = re.sub(r"[^a-z0-9]+", " ", without_accents.lower())
    return " ".join(clean_value.split())
