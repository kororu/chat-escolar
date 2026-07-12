try:
    from .content_reader import normalize_question
    from .response_states import (
        CLARIFICATION_REQUIRED,
        LOCAL_LOW_CONFIDENCE,
        LOCAL_RELATED,
        LOCAL_VERIFIED,
        NO_LOCAL_CONTENT,
    )
    from .text_utils import normalize_text
except ImportError:
    from content_reader import normalize_question
    from response_states import (
        CLARIFICATION_REQUIRED,
        LOCAL_LOW_CONFIDENCE,
        LOCAL_RELATED,
        LOCAL_VERIFIED,
        NO_LOCAL_CONTENT,
    )
    from text_utils import normalize_text


def detect_topic(question: str) -> str:
    analysis = normalize_question(question)
    clean_question = analysis["normalized_text"]

    if "habitat" in clean_question:
        return "Habitat"
    if "fraccion" in clean_question or "fracciones" in clean_question:
        return "Fracciones"
    if "agujero negro" in clean_question:
        return "Agujero negro"
    if "segunda guerra" in clean_question:
        return "Segunda Guerra Mundial"
    if "tanque" in clean_question:
        return "Tanques"

    return "Tema demo"


def make_demo_answer(
    payload,
    local_content: dict | None = None,
    related_content: dict | None = None,
    query_analysis: dict | None = None,
    provenance_status: str = "demo_fallback",
    source_course: str | None = None,
    found_in_other_course: bool = False,
) -> dict[str, str]:
    query_analysis = query_analysis or normalize_question(payload.question)
    question = query_analysis["normalized_text"]

    if "habitat" in question:
        answer = (
            "Explicacion corta:\n"
            "Un habitat es el lugar donde vive un ser vivo.\n\n"
            "Ejemplo:\n"
            "Un pez vive en el agua. Un cactus vive en el desierto.\n\n"
            "Mini resumen:\n"
            "El habitat es el hogar natural de un ser vivo.\n\n"
            "Pregunta de practica:\n"
            "Donde vive un pez?"
        )
        summary = "Un habitat es el lugar donde vive un ser vivo."
    elif "fraccion" in question or "fracciones" in question:
        answer = (
            "Explicacion corta:\n"
            "Una fraccion muestra partes de un entero.\n\n"
            "Ejemplo:\n"
            "Si una pizza se divide en 4 partes iguales y comes 1, comiste 1/4.\n\n"
            "Mini resumen:\n"
            "La fraccion dice cuantas partes tomamos y en cuantas partes se dividio el entero.\n\n"
            "Pregunta de practica:\n"
            "En 1/4, que numero indica las partes totales?"
        )
        summary = "Una fraccion representa partes de un entero."
    elif "agujero negro" in question:
        answer = (
            "Explicacion corta:\n"
            "Un agujero negro es una zona del espacio con muchisima gravedad.\n\n"
            "Ejemplo:\n"
            "Su gravedad es tan fuerte que ni la luz puede escapar si esta muy cerca.\n\n"
            "Mini resumen:\n"
            "Un agujero negro atrae con mucha fuerza lo que esta cerca.\n\n"
            "Pregunta de practica:\n"
            "Que fuerza es muy fuerte en un agujero negro?"
        )
        summary = "Un agujero negro es una zona del espacio con muchisima gravedad."
    elif "segunda guerra" in question:
        answer = (
            "Explicacion corta:\n"
            "La Segunda Guerra Mundial fue una guerra muy grande que ocurrio entre 1939 y 1945.\n\n"
            "Ejemplo:\n"
            "Muchos paises participaron. Algunos querian conquistar y otros se unieron para detenerlos.\n\n"
            "Mini resumen:\n"
            "Fue una etapa dificil y triste que se estudia con respeto.\n\n"
            "Pregunta de practica:\n"
            "Quieres aprender primero sobre paises, fechas o consecuencias?"
        )
        summary = "La Segunda Guerra Mundial ocurrio entre 1939 y 1945 y se estudia con respeto."
    elif "tanque" in question:
        answer = (
            "Explicacion corta:\n"
            "Un tanque es una maquina blindada usada en guerras.\n\n"
            "Ejemplo:\n"
            "Podemos estudiarlo desde la historia, la tecnologia y la ingenieria.\n\n"
            "Mini resumen:\n"
            "Los tanques ayudan a aprender tecnologia historica, sin celebrar la violencia.\n\n"
            "Pregunta de practica:\n"
            "Que materia se relaciona mas con estudiar tanques: Historia o Lenguaje?"
        )
        summary = "Un tanque puede estudiarse como historia y tecnologia, sin glorificar la guerra."
    else:
        if local_content and provenance_status == LOCAL_VERIFIED:
            answer = (
                "Explicacion corta:\n"
                "Encontré una fuente local verificada para esta pregunta y la usaré como apoyo principal.\n\n"
                "Mini resumen:\n"
                "Esta respuesta se apoya en contenido local revisado.\n\n"
                "Pregunta de practica:\n"
                "Puedes explicar la idea principal con tus palabras?"
            )
            summary = f"Respuesta apoyada en el contenido local: {local_content['title']}."
        else:
            answer = (
                "Explicacion corta:\n"
                "Todavia no tengo una explicacion completa sobre ese tema en los contenidos locales seleccionados.\n\n"
                "Ejemplo:\n"
                f"Si estas estudiando {payload.subject}, podemos partir por las palabras clave y revisar un paso a la vez.\n\n"
                "Mini resumen:\n"
                "Cuando un tema parece dificil, lo revisamos paso a paso.\n\n"
                "Pregunta de practica:\n"
                "Que parte de tu pregunta quieres revisar primero?"
            )
            summary = "Respuesta demo general para estudiar el tema paso a paso."

    name = (payload.user_name or "").strip()
    role = normalize_text(payload.user_role or "")
    display_name = name or ""

    if role == "apoderado":
        introduction = (
            f"Claro{', ' + display_name if display_name else ''}. "
            "Te explico una forma simple para enseñárselo al estudiante."
        )
    elif role == "docente":
        introduction = (
            f"Claro{', ' + display_name if display_name else ''}. "
            "Puedes trabajarlo con una explicación breve y una actividad simple."
        )
    elif role == "estudiante":
        introduction = (
            f"Claro{', ' + display_name if display_name else ''}. Vamos paso a paso."
        )
    else:
        introduction = "Vamos paso a paso."

    local_support = ""
    if local_content and provenance_status == LOCAL_VERIFIED:
        source_message = (
            f"No encontré una fuente principal en {payload.course}, pero sí una fuente local verificada en {source_course}."
            if found_in_other_course and source_course
            else f"Revisé la base local de {payload.course} para ayudarte."
        )
        local_support = (
            f"{source_message}\n\n"
            f"Información de apoyo:\n{local_content['excerpt']}\n\n"
        )
        summary = f"{summary} Apoyada en el contenido local: {local_content['title']}."

    if provenance_status == CLARIFICATION_REQUIRED:
        answer = (
            "No quiero adivinar el tema y darte una respuesta equivocada. "
            "¿Puedes decirme a qué tema o elemento te refieres?"
        )
        summary = "La pregunta necesita una aclaración antes de buscar contenido."
    elif provenance_status == LOCAL_LOW_CONFIDENCE:
        local_support = (
            "Encontré una coincidencia local débil, pero no la usaré como fuente "
            "porque podría no corresponder a tu pregunta.\n\n"
        )
    elif provenance_status == LOCAL_RELATED:
        related_detail = ""
        if related_content:
            related_detail = (
                f" Encontré una relación cercana en \"{related_content['title']}\" "
                f"({related_content['section']}), pero no una fuente principal."
            )
        local_support = (
            f"Todavía no tengo una explicación completa sobre ese tema en los contenidos locales de {payload.course}."
            f"{related_detail} Podemos continuar con contenidos curriculares relacionados sin tratar esa mención como fuente verificada.\n\n"
        )
    elif provenance_status == NO_LOCAL_CONTENT:
        if "explor" in normalize_text(payload.mode):
            local_support = (
                "Todavía no tengo una colección exploratoria local verificada para este tema. "
                "Te comparto una orientación demo con enfoque educativo y seguro.\n\n"
            )
        else:
            local_support = (
                "Este tema no tiene contenido curricular local verificado para la selección actual. "
                "Te comparto una orientación demo, sin presentarla como fuente curricular.\n\n"
            )

    return {
        "answer": f"{introduction}\n\n{local_support}{answer}",
        "summary": summary,
        "status": "ok",
    }
