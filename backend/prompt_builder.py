"""Construcción y limpieza de prompts educativos para IA local."""

import re

try:
    from .educational_level import get_educational_level
except ImportError:
    from educational_level import get_educational_level


MAX_LOCAL_CONTEXT_CHARACTERS = 3200
SOURCE_INSUFFICIENT_MARKER = "FUENTE_INSUFICIENTE"


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
    role = (payload.user_role or "estudiante").strip().lower()
    format_instruction = (
        "Si el perfil es estudiante, usa: 1. Explicación corta. 2. Ejemplo de la vida diaria. 3. Imagen mental o comparación simple, indicando que es una comparación. 4. Mini resumen. 5. Pregunta de práctica."
        if role == "estudiante" else
        "Si el perfil es apoderado, usa: 1. Qué debe entender el niño. 2. Cómo explicárselo. 3. Ejemplo cotidiano. 4. Actividad breve. 5. Pregunta para comprobar comprensión."
        if role == "apoderado" else
        "Si el perfil es docente, usa: 1. Objetivo de aprendizaje. 2. Explicación breve. 3. Estrategia didáctica. 4. Adecuación TEA. 5. Pregunta de evaluación rápida."
    )
    common = f"""Eres Nexo, un tutor escolar de Chat Escolar.
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
Perfil activo: {role}.
Pregunta original: {payload.question}
Consulta de apoyo: {contextual_question}
{format_instruction}
"""
    if use_local_source:
        context = _local_context(educational_context.get("verified_sources", []))
        return f"""{common}
REGLA DE FUNDAMENTACIÓN OBLIGATORIA:
Responde únicamente usando la información incluida en FUENTE LOCAL.
No uses conocimiento general, memoria externa o interna ni datos externos.
No agregues personas, países, fechas, cargos, barcos, causas, consecuencias, ganadores, derrotados ni ejemplos que no estén escritos en la fuente.
No agregues enemigos o países no mencionados. No uses lenguaje nacionalista, bélico exagerado ni juicios sobre pueblos o países.
No digas quién ganó si la fuente no lo indica. Si una parte no está en la fuente, omítela.
Si necesitas inventar o completar información, responde exactamente:
{SOURCE_INSUFFICIENT_MARKER}

FUENTE LOCAL:
{context}
FIN DE FUENTE LOCAL.

Respeta exactamente el formato indicado para el perfil activo.
"""
    return f"""{common}
MODO EXPLORAR: no hay fuente local verificada para esta pregunta.
Puedes entregar una orientación exploratoria, pero no la presentes como contenido curricular confirmado.
Evita detalles violentos o gráficos y reconoce que la respuesta puede contener errores.

Responde con:
1. Explicación corta.
2. Ejemplo.
3. Dato interesante.
4. Una sola pregunta para seguir explorando.
"""


def is_source_insufficient_response(answer: str) -> bool:
    return SOURCE_INSUFFICIENT_MARKER in answer.upper()


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
