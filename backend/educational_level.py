"""Reglas centrales de lenguaje, lectura fácil y práctica por curso."""

try:
    from .text_utils import normalize_text
except ImportError:
    from text_utils import normalize_text


_LEVELS = {
    1: ("6 a 7 años", "inicial escolar", "frases muy cortas y una idea por bloque", 2, 1, 90),
    2: ("7 a 8 años", "inicial escolar", "frases cortas y ejemplos concretos", 3, 1, 90),
    3: ("8 a 9 años", "básico escolar", "frases simples y explicación breve", 3, 1, 120),
    4: ("9 a 10 años", "básico escolar", "frases simples y explicación breve", 3, 1, 120),
    5: ("10 a 11 años", "intermedio escolar", "lenguaje claro con conceptos explicados", 3, 1, 170),
    6: ("11 a 12 años", "intermedio escolar", "lenguaje claro con conceptos explicados", 3, 1, 170),
    7: ("12 a 13 años", "avanzado escolar", "explicación precisa con relaciones claras", 4, 1, 220),
    8: ("13 a 14 años", "avanzado escolar", "explicación precisa con relaciones claras", 4, 1, 220),
}


def get_educational_level(course: str | None) -> dict:
    normalized = normalize_text(course or "")
    grade = next((number for number in _LEVELS if str(number) in normalized), 5)
    age, reading_level, sentence_style, ideas, questions, max_words = _LEVELS[grade]
    return {
        "course": course or "5° básico",
        "approx_age": age,
        "reading_level": reading_level,
        "sentence_style": sentence_style,
        "max_main_ideas": ideas,
        "practice_questions": questions,
        "max_words": max_words,
        "easy_reading": True,
    }
