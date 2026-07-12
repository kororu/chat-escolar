"""Construcción y limpieza de prompts educativos para IA local."""

import re

try:
    from .educational_level import get_educational_level
except ImportError:
    from educational_level import get_educational_level


MAX_LOCAL_CONTEXT_CHARACTERS = 3200


def _local_context(sources: list[dict]) -> str:
    chunks = []
    remaining = MAX_LOCAL_CONTEXT_CHARACTERS
    for source in sources[:3]:
        text = (source.get("excerpt") or source.get("summary") or "").strip()
        if not text or remaining <= 0:
            continue
        fragment = text[:remaining]
        chunks.append(f"Fuente: {source.get('title', 'Contenido local')}\n{fragment}")
        remaining -= len(fragment)
    return "\n\n".join(chunks)


def build_ollama_prompt(payload, educational_context: dict, *, use_local_source: bool) -> str:
    contextual_question = educational_context["conversation_context"].get("contextual_question") or payload.question
    student_name = (payload.user_name or "Estudiante").strip()
    level = get_educational_level(educational_context.get("active_course") or payload.course)
    common = f"""Eres Chat Escolar, un tutor educativo local.
Responde solo en español de Chile, claro, amable y apropiado para el curso.
No muestres razonamiento interno, análisis, pasos internos, ni escribas 'Thinking'.
No inventes fuentes. Estudiante de {level['course']}, edad aproximada {level['approx_age']}.
Nivel de lectura: {level['reading_level']}. Usa {level['sentence_style']}.
Si usas una palabra difícil, explíquela. Una idea principal por bloque y solo una pregunta de práctica.
Máximo {level['max_words']} palabras. Mantén lectura fácil y evita ambigüedades.
Estudiante: {student_name}.
Curso: {educational_context.get('active_course') or payload.course}.
Materia: {payload.subject}.
Modo: {payload.mode}.
Pregunta original: {payload.question}
Consulta de apoyo: {contextual_question}
"""
    if use_local_source:
        context = _local_context(educational_context.get("verified_sources", []))
        return f"""{common}
Usa SOLO la fuente local verificada entregada. No agregues datos externos.

Fuente local verificada:
{context}

Responde con:
1. Explicación corta.
2. Ejemplo.
3. Mini resumen.
4. Una sola pregunta de práctica.
"""
    return f"""{common}
No hay fuente local verificada para esta pregunta. Entrega una explicación general segura y educativa, e indica brevemente que no usaste una fuente local verificada. Evita detalles violentos o gráficos.

Responde con:
1. Explicación corta.
2. Ejemplo.
3. Dato interesante.
4. Una sola pregunta para seguir explorando.
"""


def clean_ollama_response(answer: str) -> str:
    """Elimina etiquetas/bloques de razonamiento que un modelo pudiera filtrar."""
    cleaned = re.sub(r"<think>.*?</think>\s*", "", answer, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(
        r"^\s*(?:thinking(?:\s+process)?|análisis|razonamiento)\s*:\s*.*?(?:\n\s*\n|$)",
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return cleaned.strip()
