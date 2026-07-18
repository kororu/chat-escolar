import re

try:
    from .content_reader import CONTENT_ROOT, normalize_question, strip_front_matter
    from .educational_level import get_educational_level
    from .response_states import (
        CLARIFICATION_REQUIRED,
        LOCAL_LOW_CONFIDENCE,
        LOCAL_RELATED,
        LOCAL_VERIFIED,
        NO_LOCAL_CONTENT,
    )
    from .text_utils import normalize_text
except ImportError:
    from content_reader import CONTENT_ROOT, normalize_question, strip_front_matter
    from educational_level import get_educational_level
    from response_states import (
        CLARIFICATION_REQUIRED,
        LOCAL_LOW_CONFIDENCE,
        LOCAL_RELATED,
        LOCAL_VERIFIED,
        NO_LOCAL_CONTENT,
    )
    from text_utils import normalize_text


EXCLUDED_FALLBACK_SECTIONS = {
    "objetivos de aprendizaje",
    "fuente curricular de referencia",
    "para apoderados",
    "para docentes",
    "como deberia responder chat escolar",
    "notas editoriales",
}

INTERNAL_TEMPLATE_PHRASES = (
    "el ejemplo debe analizarse identificando la idea central",
    "relacionando cada dato o elemento con el concepto",
    "explicando que cambiaria si se modifica una condicion",
    "aplicar el concepto al ejemplo",
    "explicar el procedimiento o evidencia",
    "comprobar la respuesta",
    "que idea matematica explica",
    "instrucciones internas del generador",
)


def _clean_local_text(value: str, limit: int = 620) -> str:
    lines = []
    for line in value.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(">"):
            continue
        line = line.lstrip("- ").strip()
        line = line.replace("**", "").replace("`", "")
        if any(phrase in normalize_text(line) for phrase in INTERNAL_TEMPLATE_PHRASES):
            continue
        if line:
            lines.append(line)
    text = " ".join(lines)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    shortened = text[:limit].rsplit(" ", 1)[0]
    return f"{shortened}."


def _markdown_sections(local_content: dict) -> dict[str, str]:
    relative_path = local_content.get("path")
    if not relative_path:
        return {}
    try:
        file_path = (CONTENT_ROOT / relative_path).resolve()
        if CONTENT_ROOT.resolve() not in file_path.parents:
            return {}
        content = strip_front_matter(file_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return {}

    sections: dict[str, list[str]] = {}
    current_heading = ""
    for line in content.splitlines():
        if line.startswith("## "):
            current_heading = normalize_text(line[3:])
            sections.setdefault(current_heading, [])
        elif current_heading:
            sections[current_heading].append(line)
    return {
        heading: _clean_local_text("\n".join(lines))
        for heading, lines in sections.items()
        if heading not in EXCLUDED_FALLBACK_SECTIONS and _clean_local_text("\n".join(lines))
    }


def _first_section(sections: dict[str, str], *priorities: str) -> str:
    for priority in priorities:
        target = normalize_text(priority)
        for heading, text in sections.items():
            if target in heading:
                return text
    return ""


def _limit_sentences(text: str, maximum: int) -> str:
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
    return " ".join(sentences[:maximum]) if sentences else text


def _limit_words(text: str, maximum: int) -> str:
    words = text.split()
    if len(words) <= maximum:
        return text
    shortened = " ".join(words[:maximum]).rstrip(" ,;:")
    return f"{shortened}."


def _simplify_for_level(text: str, level: dict) -> str:
    """Aclara expresiones frecuentes sin ocultar el concepto escolar."""
    grade = int(next((number for number in range(1, 9) if str(number) in normalize_text(level["course"])), 5))
    if grade >= 7:
        return text
    replacements = {
        "Nutrientes cumplen funciones energéticas, estructurales y reguladoras.": "Los nutrientes ayudan al cuerpo a tener energía, crecer y funcionar bien.",
        "nutriente usado principalmente como fuente de energía.": "Un nutriente es una parte del alimento que ayuda al cuerpo. Los carbohidratos dan energía.",
        "nutriente relacionado con formación y reparación.": "Las proteínas ayudan al cuerpo a crecer y reparar partes que lo necesitan.",
        "nutriente energético y estructural.": "Los lípidos también dan energía y ayudan a formar partes del cuerpo.",
        "La variedad ayuda a cubrir necesidades.": "Comer alimentos variados ayuda al cuerpo a recibir lo que necesita.",
        "porciones y frecuencia dependen del contexto.": "La cantidad y frecuencia pueden cambiar según cada persona y situación.",
        "salud no se evalúa por apariencia corporal.": "La salud no se puede saber solo por la apariencia de una persona.",
    }
    simplified = text
    for original, replacement in replacements.items():
        simplified = re.sub(re.escape(original), replacement, simplified, flags=re.IGNORECASE)
    return simplified


def _single_practice_question(text: str) -> str:
    question = re.search(r"¿[^?]+\?", text)
    return question.group(0) if question else "¿Cómo explicarías esta idea con tus propias palabras?"


def _student_introduction(payload) -> str:
    name = (payload.user_name or "").strip()
    role = normalize_text(payload.user_role or "")
    if role == "apoderado":
        return f"Claro{', ' + name if name else ''}. Te explico una forma simple para enseñárselo al estudiante."
    if role == "docente":
        return f"Claro{', ' + name if name else ''}. Puedes trabajarlo con una explicación breve y una actividad simple."
    return f"Claro{', ' + name if name else ''}. Vamos paso a paso." if name else "Vamos paso a paso."


def build_local_content_fallback(payload, local_content: dict) -> dict[str, str]:
    """Construye una explicación útil desde un Markdown local verificado."""
    sections = _markdown_sections(local_content)
    level = get_educational_level(payload.course)
    explanation = _first_section(
        sections,
        "respuesta breve",
        "explicacion completa para estudiante",
        "como explicarlo si todavia no se entiende",
    ) or _clean_local_text(local_content.get("excerpt", ""))
    example = _first_section(sections, "ejemplo explicado", "ejemplo")
    summary = _first_section(sections, "mini resumen", "ideas fundamentales") or explanation
    practice = _first_section(sections, "preguntas de practica", "pregunta de practica")

    explanation = _simplify_for_level(explanation, level)
    example = _simplify_for_level(example, level)
    summary = _simplify_for_level(summary, level)

    if not example:
        example = "Piensa en una situación cotidiana relacionada con esta idea y explica cómo se aplica."
    practice = _single_practice_question(practice)
    main_ideas = level["max_main_ideas"]
    explanation = _limit_sentences(explanation, main_ideas)
    example = _limit_sentences(example, 2 if main_ideas >= 3 else 1)
    summary = _limit_sentences(summary, min(2, main_ideas))
    # Reserve space for labels and the single final practice question.
    explanation = _limit_words(explanation, max(24, int(level["max_words"] * 0.42)))
    example = _limit_words(example, max(16, int(level["max_words"] * 0.24)))
    summary = _limit_words(summary, max(14, int(level["max_words"] * 0.18)))

    role = normalize_text(payload.user_role or "estudiante")
    subject = normalize_text(local_content.get("subject") or payload.subject or "")
    example_heading = (
        "Contexto histórico" if "historia" in subject
        else "Ejemplo paso a paso" if "matematica" in subject
        else "Ejemplo" if "lenguaje" in subject
        else "Ejemplo de la vida diaria"
    )
    source_note = ""
    if local_content.get("course") and local_content["course"] != payload.course:
        source_course = local_content["course"]
        is_encyclopedia = (
            source_course.startswith("Enciclopedia ")
            or str(local_content.get("metadata", {}).get("content_type", "")).startswith("enciclopedia")
        )
        if is_encyclopedia:
            source_note = (
                f"Fuente enciclopédica: {source_course.removeprefix('Enciclopedia ')}. "
                f"Adaptado para {payload.course}.\n\n"
            )
        else:
            source_note = f"Encontrado en otro curso: {source_course}. Adaptado para {payload.course}.\n\n"
    if role == "apoderado":
        answer = (f"{_student_introduction(payload)}\n\n{source_note}"
                  f"Qué debe entender el niño:\n{explanation}\n\nCómo explicárselo:\n{example}\n\n"
                  f"Actividad breve:\nComenten el ejemplo y pidan que lo represente con un dibujo o sus palabras.\n\n"
                  f"Pregunta para comprobar comprensión:\n{practice}")
    elif role == "docente":
        answer = (f"{_student_introduction(payload)}\n\n{source_note}"
                  f"Objetivo de aprendizaje:\nComprender la idea principal: {summary}\n\nExplicación breve:\n{explanation}\n\n"
                  f"Estrategia didáctica:\n{example}\n\nAdecuación TEA:\nUna instrucción por vez, apoyo visual y opción de responder oralmente, con dibujo o selección.\n\n"
                  f"Pregunta de evaluación rápida:\n{practice}")
    else:
        answer = (f"{_student_introduction(payload)}\n\n{source_note}"
                  f"Explicación corta:\n{explanation}\n\n{example_heading}:\n{example}\n\n"
                  f"Mini resumen:\n{summary}\n\nPregunta de práctica:\n{practice}")
    return {
        "answer": answer,
        "summary": summary[:220],
        "status": "ok",
    }


def build_grounded_math_answer(payload, local_content: dict) -> dict[str, str]:
    """Uses stable definitions for basic Math questions with a verified source."""
    question = normalize_text(getattr(payload, "question", ""))
    templates = (
        (
            ("probabilidad experimental",),
            lambda text: True,
            "La probabilidad experimental se estima repitiendo una acción, registrando los resultados y observando con qué frecuencia ocurre cada uno.",
            "Si lanzas una moneda 10 veces y sale cara 6 veces, la frecuencia observada de cara es 6 de 10 lanzamientos.",
            "La probabilidad experimental usa resultados observados al repetir una experiencia.",
            "Si una moneda sale sello 4 veces en 10 lanzamientos, ¿cuál fue su frecuencia observada?",
        ),
        (
            ("probabilidad",),
            lambda text: "experimental" not in text and "frecuencia" not in text,
            "La probabilidad sirve para estimar qué tan posible es que ocurra un resultado.",
            "Si lanzas una moneda, puede salir cara o sello. Como hay 2 resultados posibles, la probabilidad de que salga cara es 1 de 2.",
            "La probabilidad ayuda a pensar si algo es seguro, posible, poco probable o imposible.",
            "Si una bolsa tiene 1 pelota roja y 3 azules, ¿qué color es más probable sacar?",
        ),
        (
            ("promedio",),
            lambda text: True,
            "El promedio es un valor que representa un conjunto de datos al repartir el total en partes iguales.",
            "Con los datos 2, 4 y 6, sumamos 12 y dividimos entre 3. El promedio es 4.",
            "Para calcular un promedio, se suma todo y se divide por la cantidad de datos.",
            "Si tus datos son 2, 4 y 6, ¿cuál es el promedio?",
        ),
        (
            ("volumen",),
            lambda text: True,
            "El volumen mide cuánto espacio ocupa un cuerpo u objeto. Se puede imaginar como la cantidad de cubitos que caben dentro o forman una figura de tres dimensiones.",
            "Imagina una caja hecha con cubitos. Si tiene 3 cubitos de largo, 2 de ancho y 2 de alto, ocupa 12 cubitos en total.",
            "El volumen indica cuánto espacio ocupa un objeto de tres dimensiones.",
            "Si una caja tiene 2 cubitos de largo, 2 de ancho y 2 de alto, ¿cuántos cubitos ocupa en total?",
        ),
        (
            ("fraccion", "fracciones"),
            lambda text: "equivalente" not in text,
            "Una fracción representa una parte de un entero o de un grupo dividido en partes iguales.",
            "Imagina una pizza dividida en 4 partes iguales. Si comes 1 parte, comiste 1/4 de la pizza.",
            "Una fracción muestra cuántas partes tomamos de un total dividido en partes iguales.",
            "Si una torta está dividida en 8 partes iguales y comes 2, ¿qué fracción comiste?",
        ),
        (
            ("fraccion equivalente", "fracciones equivalentes"),
            lambda text: True,
            "Las fracciones equivalentes son fracciones distintas que representan la misma cantidad.",
            "Por ejemplo, 1/2 y 2/4 representan la misma parte de un entero: la mitad.",
            "Fracciones distintas pueden tener el mismo valor.",
            "¿Qué fracción equivalente a 1/2 puedes formar si divides el entero en 4 partes iguales?",
        ),
        (
            ("ecuacion", "ecuaciones"),
            lambda text: True,
            "Una ecuación es una igualdad que contiene un número desconocido. Resolverla es encontrar el valor que hace verdadera la igualdad.",
            "En x + 2 = 10, buscamos el número que, al sumarle 2, da 10. Ese número es 8.",
            "Una ecuación busca un valor desconocido que mantiene una igualdad.",
            "¿Qué número debe ocupar x en x + 3 = 9?",
        ),
        (
            ("funcion lineal", "funcion afin", "pendiente"),
            lambda text: True,
            "Una función lineal relaciona una entrada con una salida siguiendo una regla que cambia siempre de la misma manera.",
            "En y = 3x, la salida se obtiene multiplicando la entrada por 3. Si x vale 2, y vale 6.",
            "Una función lineal sigue una regla constante entre entrada y salida.",
            "En y = 2x, ¿cuál es la salida cuando x vale 4?",
        ),
        (
            ("funcion", "funciones"),
            lambda text: not any(term in text for term in ("lineal", "afin", "pendiente", "y=")),
            "Una función es una relación donde a cada valor de entrada le corresponde un solo valor de salida.",
            "Imagina una máquina que duplica números. Si entra 1, sale 2; si entra 2, sale 4; y si entra 3, sale 6.",
            "Una función relaciona una entrada con una salida siguiendo una regla.",
            "Si una máquina suma 3 a cada número, ¿qué sale si entra el número 5?",
        ),
        (
            ("area",),
            lambda text: True,
            "El área mide la superficie que cubre una figura plana.",
            "Un rectángulo de 3 cuadrados de largo y 2 de ancho cubre 6 cuadrados. Su área es 6 unidades cuadradas.",
            "El área indica cuánto espacio ocupa una superficie plana.",
            "Si un rectángulo mide 4 cuadrados por 2 cuadrados, ¿cuál es su área?",
        ),
    )
    for terms, condition, explanation, example, summary, practice in templates:
        if any(term in question for term in terms) and condition(question):
            source_note = ""
            if local_content.get("course") and local_content["course"] != payload.course:
                source_note = f"Encontrado en otro curso: {local_content['course']}. Adaptado para {payload.course}.\n\n"
            answer = (
                f"{_student_introduction(payload)}\n\n{source_note}"
                f"Explicación corta:\n{explanation}\n\n"
                f"Ejemplo paso a paso:\n{example}\n\n"
                f"Mini resumen:\n{summary}\n\n"
                f"Pregunta de práctica:\n{practice}"
            )
            return {"answer": answer, "summary": summary, "status": "ok"}
    return build_local_content_fallback(payload, local_content)


def build_grounded_history_answer(payload, local_content: dict) -> dict[str, str]:
    """Construye una respuesta histórica solo desde las secciones locales verificadas."""
    return build_local_content_fallback(payload, local_content)


def build_grounded_science_answer(payload, local_content: dict) -> dict[str, str]:
    question = normalize_text(getattr(payload, "question", ""))
    title = normalize_text(local_content.get("title", ""))
    templates = (
        (("ciclo del agua",), "ciclo del agua", "El ciclo del agua es el recorrido que hace el agua en la naturaleza. Puede evaporarse, formar nubes, caer como lluvia y volver a ríos, lagos o mares.", "Cuando el Sol calienta un charco, parte del agua se evapora y sube al aire. Después puede formar nubes y volver a caer como lluvia.", "El ciclo del agua muestra cómo el agua cambia de lugar y de estado en la naturaleza.", "¿Qué pasa con el agua cuando el Sol la calienta?"),
        (("agujero negro", "agujeros negros"), "agujero negro", "Un agujero negro es una región del espacio donde la gravedad es extremadamente fuerte. Si algo se acerca demasiado, es muy difícil que escape; incluso la luz no puede salir de una zona llamada horizonte de sucesos.", "Imagina una aspiradora muy poderosa. No es igual a un agujero negro, pero ayuda a imaginar que atrae con mucha fuerza las cosas que están muy cerca.", "Una zona del espacio con gravedad tan intensa que la luz no puede salir.", "¿Por qué crees que ni siquiera la luz puede escapar de un agujero negro?"),
        (("gravedad",), "gravedad", "La gravedad es la fuerza que atrae los objetos entre sí. En la Tierra hace que las cosas caigan hacia el suelo y ayuda a que la Luna se mantenga orbitando nuestro planeta.", "Cuando sueltas una pelota, la gravedad hace que caiga al suelo.", "La gravedad atrae los objetos.", "¿Qué ejemplo de gravedad puedes observar cerca de ti?"),
        (("celula", "celulas"), "celula", "Una célula es la unidad más pequeña que forma a los seres vivos. Los animales, las plantas y otros seres vivos están formados por células.", "Puedes imaginar las células como pequeñas piezas que, juntas, forman partes de un ser vivo.", "Los seres vivos están formados por células.", "¿Qué ser vivo crees que está formado por células?"),
        (("fotosintesis",), "fotosintesis", "La fotosíntesis es el proceso por el que las plantas usan la luz del Sol, agua y aire para producir su propio alimento.", "Una planta cerca de una ventana recibe luz, toma agua por sus raíces y usa esos elementos para alimentarse.", "Las plantas usan la luz del Sol para fabricar su alimento.", "¿Qué necesita una planta para realizar la fotosíntesis?"),
    )

    for question_terms, title_term, explanation, example, summary, practice in templates:
        title_matches = title_term in title or (
            title_term == "agujero negro" and "agujeros negros" in title
        )
        if any(term in question for term in question_terms) and title_matches:
            source_area = local_content.get("metadata", {}).get("area")
            source_note = (
                f"Encontrado en contenido de {source_area}. Adaptado para {payload.course}.\n\n"
                if source_area else ""
            )
            answer = (
                f"{_student_introduction(payload)}\n\n{source_note}"
                f"Explicación corta:\n{explanation}\n\n"
                f"Ejemplo de la vida diaria:\n{example}\n\n"
                f"Mini resumen:\n{summary}\n\n"
                f"Pregunta de práctica:\n{practice}"
            )
            return {"answer": answer, "summary": summary, "status": "ok"}
    return build_local_content_fallback(payload, local_content)


def build_contextual_followup(payload, action: str, local_content: dict | None) -> dict[str, str]:
    """Respuesta breve anclada al último tema y fuente local, sin IA ni tema demo."""
    if not local_content:
        return {"answer": "Primero hazme una pregunta sobre un tema y luego puedo explicarlo más fácil, darte un ejemplo o hacerte una pregunta de práctica.", "summary": "Falta un tema previo.", "status": "ok"}
    topic = normalize_text(
        getattr(payload, "question", "") or getattr(payload, "last_user_question", "")
    )
    source_title = normalize_text(local_content.get("title", ""))
    asks_equation = bool(re.search(r"\becuacion(?:es)?\b", topic))
    asks_inequality = bool(re.search(r"\binecuacion(?:es)?\b", topic))
    if "ciclo del agua" in topic and "ciclo del agua" in source_title:
        followups = {
            "simplify": ("Más fácil:", "El agua viaja: sube al aire, forma nubes, cae como lluvia y vuelve a la Tierra."),
            "explain_again": ("Vamos más lento:", "El Sol calienta el agua y una parte se evapora. Luego el vapor forma nubes y puede caer como lluvia."),
            "give_example": ("Ejemplo:", "Un charco se seca con el Sol porque parte de su agua se evapora. Más tarde esa agua puede volver como lluvia."),
            "ask_question": ("Pregunta de práctica:", "¿Qué ocurre con el agua cuando el Sol la calienta?"),
        }
        heading, text = followups.get(action, followups["explain_again"])
        return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text, "status": "ok"}
    if "volumen" in topic:
        followups = {
            "simplify": ("Más fácil:", "El volumen dice cuánto espacio ocupa una figura de tres dimensiones, como una caja."),
            "explain_again": ("Vamos más lento:", "El volumen cuenta cuántos cubitos forman o caben dentro de una figura de tres dimensiones."),
            "give_example": ("Ejemplo:", "Si una caja tiene 2 cubitos de largo, 3 de ancho y 1 de alto, ocupa 6 cubitos."),
            "ask_question": ("Pregunta de práctica:", "Si una figura tiene 2 cubitos de largo, 2 de ancho y 2 de alto, ¿cuántos cubitos ocupa?"),
        }
        heading, text = followups.get(action, followups["explain_again"])
        return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text, "status": "ok"}
    if "funcion" in topic and not any(term in topic for term in ("lineal", "afin", "pendiente", "y=")):
        followups = {
            "simplify": ("Más fácil:", "Una función es como una máquina: recibe un número y entrega un solo resultado siguiendo una regla."),
            "explain_again": ("Vamos más lento:", "Primero entra un número a la máquina. Luego la regla de la máquina produce un número de salida."),
            "give_example": ("Ejemplo:", "Imagina una máquina que suma 2. Si entra 4, sale 6; si entra 5, sale 7."),
            "ask_question": ("Pregunta de práctica:", "Si una máquina duplica el número que entra, ¿qué sale si entra 4?"),
        }
        heading, text = followups.get(action, followups["explain_again"])
        return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text, "status": "ok"}
    if "probabilidad" in topic:
        followups = {
            "simplify": ("Más fácil:", "La probabilidad nos dice qué tan posible es que ocurra algo."),
            "explain_again": ("Vamos más lento:", "Para pensar en una probabilidad, miramos los resultados posibles y vemos cuáles pueden ocurrir."),
            "give_example": ("Ejemplo:", "Al lanzar una moneda hay dos resultados posibles: cara o sello. Por eso cara tiene una posibilidad de 1 de 2."),
            "ask_question": ("Pregunta de práctica:", "En una bolsa hay 2 pelotas rojas y 1 azul. ¿Qué color es más probable sacar?"),
        }
        heading, text = followups.get(action, followups["explain_again"])
        return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text, "status": "ok"}
    if asks_equation and not asks_inequality:
        followups = {
            "simplify": ("Más fácil:", "Una ecuación es una igualdad con un número desconocido que debemos encontrar."),
            "explain_again": ("Vamos más lento:", "En una ecuación buscamos el número que hace verdadera la igualdad."),
            "give_example": ("Ejemplo paso a paso:", "Si tenemos x + 2 = 10, buscamos qué número puede ir en x. Como 8 + 2 = 10, entonces x = 8."),
            "ask_question": ("Pregunta de práctica:", "¿Qué número debe ocupar x en x + 4 = 9?"),
        }
        heading, text = followups.get(action, followups["explain_again"])
        return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text, "status": "ok"}
    if asks_inequality and not asks_equation:
        followups = {
            "simplify": ("Más fácil:", "Una inecuación compara cantidades y muestra que una puede ser mayor o menor que otra."),
            "explain_again": ("Vamos más lento:", "En una inecuación buscamos los números que cumplen una comparación."),
            "give_example": ("Ejemplo paso a paso:", "En x + 2 > 6, restamos 2 a ambos lados. Entonces x > 4."),
            "ask_question": ("Pregunta de práctica:", "¿Qué números cumplen x + 1 > 5?"),
        }
        heading, text = followups.get(action, followups["explain_again"])
        return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text, "status": "ok"}
    if "fraccion" in topic and "fraccion" in source_title:
        followups = {
            "simplify": ("Más fácil:", "Una fracción dice cuántas partes iguales tomamos de un todo."),
            "explain_again": ("Vamos más lento:", "Primero dividimos un entero en partes iguales. Después contamos cuántas partes tomamos."),
            "give_example": ("Ejemplo:", "Si una pizza tiene 4 partes iguales y tomas 1, la fracción es 1/4."),
            "ask_question": ("Pregunta de práctica:", "Si una barra se divide en 6 partes iguales y tomas 3, ¿qué fracción tomaste?"),
        }
        heading, text = followups.get(action, followups["explain_again"])
        return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text, "status": "ok"}
    if "fotosintesis" in topic and "fotosintesis" in source_title:
        followups = {
            "simplify": ("Más fácil:", "La fotosíntesis es la forma en que las plantas usan la luz del Sol, agua y aire para fabricar su alimento."),
            "explain_again": ("Vamos más lento:", "La planta recibe luz, toma agua por sus raíces y usa aire para producir su alimento."),
            "give_example": ("Ejemplo:", "Una planta junto a una ventana recibe luz del Sol. Si también tiene agua, puede realizar la fotosíntesis."),
            "ask_question": ("Pregunta de práctica:", "¿Qué necesita una planta para realizar la fotosíntesis?"),
        }
        heading, text = followups.get(action, followups["explain_again"])
        return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text, "status": "ok"}
    sections = _markdown_sections(local_content)
    level = get_educational_level(payload.course)
    explanation = _first_section(sections, "respuesta breve", "explicacion clara") or _clean_local_text(local_content.get("excerpt", ""))
    example = _first_section(sections, "ejemplo cotidiano", "ejemplo explicado", "ejemplo") or explanation
    practice = _single_practice_question(_first_section(sections, "preguntas de practica", "pregunta de practica"))
    explanation = _limit_words(_simplify_for_level(_limit_sentences(explanation, 2), level), 90)
    example = _limit_words(_simplify_for_level(_limit_sentences(example, 2), level), 75)
    labels = {
        "simplify": ("Más fácil:", explanation),
        "explain_again": ("Vamos más lento:", explanation),
        "give_example": ("Ejemplo:", example),
        "ask_question": ("Pregunta de práctica:", practice),
    }
    heading, text = labels.get(action, labels["explain_again"])
    return {"answer": f"{_student_introduction(payload)}\n\n{heading}\n{text}", "summary": text[:220], "status": "ok"}


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
    elif any(term in question for term in ("combate naval", "iquique", "arturo prat", "21 de mayo", "guerra del pacifico")):
        answer = (
            "Explicacion corta:\n"
            "Detecte que esta pregunta es de Historia. No encontre una fuente local exacta sobre el Combate Naval de Iquique en los contenidos instalados.\n\n"
            "Mini resumen:\n"
            "Puedes activar IA local o agregar este tema a la base de Historia para obtener una explicacion completa.\n\n"
            "Pregunta de practica:\n"
            "Quieres revisar primero la fecha, los participantes o el contexto historico?"
        )
        summary = "Tema de Historia sin fuente curricular local exacta."
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
            "¿Puedes decirme qué quieres repasar? Por ejemplo: ‘explícame las fracciones’ "
            "o ‘qué es la fotosíntesis’."
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
