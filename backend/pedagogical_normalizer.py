"""Reusable safeguards for presenting local Markdown as school-facing text."""

from __future__ import annotations

import re

try:
    from .text_utils import normalize_text
except ImportError:
    from text_utils import normalize_text


INTERNAL_PATTERNS = (
    r"\bevidencia deberias observar\b",
    r"\baplicar el concepto al ejemplo\b",
    r"\bcomprobar la respuesta\b",
    r"\bexplicar el procedimiento o evidencia\b",
    r"\bel ejemplo debe analizarse\b",
    r"\bidentifica quien realiza la accion\b",
    r"\bque idea (matematica )?explica\b",
    r"\b(construye un modelo|analiza el caso|relaciona cada dato)\b",
)

GENERIC_QUESTION_PATTERNS = (
    r"^que evidencia\b", r"^que representacion ayuda\b", r"^que idea explica\b",
)


def is_internal_instruction(text: str) -> bool:
    """True when a line is editorial scaffolding rather than student content."""
    normalized = normalize_text(text)
    if not normalized:
        return True
    return any(re.search(pattern, normalized) for pattern in INTERNAL_PATTERNS)


def is_generic_practice_question(text: str) -> bool:
    normalized = normalize_text(text).rstrip("?")
    return any(re.search(pattern, normalized) for pattern in GENERIC_QUESTION_PATTERNS)


def clean_pedagogical_lines(text: str, *, concept: str | None = None) -> str:
    """Remove headings, planning prompts and unsupported generic activities."""
    accepted: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("- ").replace("**", "").replace("`", "")
        if not line or line.startswith("#") or line.startswith(">"):
            continue
        if is_internal_instruction(line) or is_generic_practice_question(line):
            continue
        accepted.append(line)
    cleaned = " ".join(" ".join(accepted).split())
    if concept and cleaned and normalize_text(concept) not in normalize_text(cleaned):
        # A fragment that never names the requested concept is weaker than an
        # explicit source section and should not become the primary definition.
        return ""
    return cleaned


def detect_intent(question: str) -> str:
    normalized = normalize_text(question)
    intents = (
        ("example", ("dame un ejemplo", "muestrame un ejemplo")),
        ("procedure", ("como se hace", "como se calcula", "como puedo encontrar")),
        ("comparison", ("cual es la diferencia", "compara")),
        ("practice", ("hazme una pregunta", "dame un ejercicio")),
        ("summary", ("resumelo", "haz un resumen")),
        ("cause", ("por que ocurrio", "por que")),
        ("consequence", ("que consecuencias tuvo", "que consecuencia tuvo")),
        ("definition", ("que es", "que significa", "explicame", "explica")),
    )
    return next((name for name, markers in intents if any(marker in normalized for marker in markers)), "definition")
