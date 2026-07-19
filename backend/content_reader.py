import re
from difflib import SequenceMatcher
from pathlib import Path
from threading import Lock

try:
    from .educational_config import (
        COURSE_LABELS,
        course_to_folder,
        folder_to_course_label,
        is_all_courses,
        is_explorer_mode,
        subject_to_folder,
    )
    from .response_states import (
        CLARIFICATION_REQUIRED,
        DEMO_FALLBACK,
        LOCAL_LOW_CONFIDENCE,
        LOCAL_RELATED,
        LOCAL_VERIFIED,
        NO_LOCAL_CONTENT,
    )
    from .text_utils import normalize_text
except ImportError:
    from educational_config import (
        COURSE_LABELS,
        course_to_folder,
        folder_to_course_label,
        is_all_courses,
        is_explorer_mode,
        subject_to_folder,
    )
    from response_states import (
        CLARIFICATION_REQUIRED,
        DEMO_FALLBACK,
        LOCAL_LOW_CONFIDENCE,
        LOCAL_RELATED,
        LOCAL_VERIFIED,
        NO_LOCAL_CONTENT,
    )
    from text_utils import normalize_text

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "contenidos"
MIN_RELEVANCE_SCORE = 24
MAX_RESULTS = 3
NON_PRIMARY_SOURCE_PARTS = {"00_documentacion", "bancos", "compendios", "evaluaciones"}
NON_PRIMARY_FILE_PREFIXES = ("00_indice",)

STOP_WORDS = {
    "al", "algo", "como", "con", "cual", "cuando", "de", "del", "desde",
    "donde", "el", "ella", "en", "es", "esta", "este", "esto", "fue",
    "gustaria", "hay", "la", "las", "lo", "los", "mas", "me", "mi", "para",
    "por", "que", "saber", "se", "sin", "son", "su", "sus", "un", "una",
    "unas", "unos", "usado", "usada", "y",
}

# Diccionario pequeño y explícito: solo corrige conceptos educativos conocidos.
# Se puede ampliar sin incorporar un corrector ortográfico agresivo.
EDUCATIONAL_CONCEPTS = {
    "habitat": {
        "aliases": {"habitat", "habitats", "havitat", "abitad"},
        "subject": "ciencias_naturales",
        "external": False,
    },
    "fracciones": {
        "aliases": {"fraccion", "fracciones"},
        "subject": "matematica",
        "external": False,
    },
    "fotosintesis": {
        "aliases": {"fotosintesis", "fotosintetico", "fotosintetica"},
        "subject": "ciencias_naturales",
        "external": False,
    },
    "metafora": {
        "aliases": {"metafora", "metaforas", "lenguaje figurado"},
        "subject": "lenguaje",
        "external": False,
    },
    "sistema respiratorio": {
        "aliases": {"sistema respiratorio", "respiratorio"},
        "subject": "ciencias_naturales",
        "external": False,
    },
    "promedio aritmetico": {
        "aliases": {"promedio aritmetico", "promedio"},
        "subject": "matematica",
        "external": False,
    },
    "ecosistemas": {
        "aliases": {"ecosistema", "ecosistemas"},
        "subject": "ciencias_naturales",
        "external": False,
    },
    "tanques": {
        "aliases": {"tanque", "tanques"},
        "subject": "modo_explorador",
        "external": True,
    },
    "segunda guerra mundial": {
        "aliases": {"segunda guerra", "segunda guerra mundial"},
        "subject": "modo_explorador",
        "external": True,
    },
    "aviones": {
        "aliases": {"avion", "aviones"},
        "subject": "modo_explorador",
        "external": True,
    },
    "espacio": {
        "aliases": {"espacio", "espacial"},
        "subject": "modo_explorador",
        "external": True,
    },
    "dinosaurios": {
        "aliases": {"dinosaurio", "dinosaurios"},
        "subject": "modo_explorador",
        "external": True,
    },
    "robots": {
        "aliases": {"robot", "robots"},
        "subject": "modo_explorador",
        "external": True,
    },
    "inventos": {
        "aliases": {"invento", "inventos"},
        "subject": "modo_explorador",
        "external": True,
    },
}

RELATED_SECTION_HINTS = {
    "conexion",
    "conexiones",
    "relacion",
    "relaciones",
    "relacionado",
    "relacionados",
    "tema relacionado",
    "temas relacionados",
    "glosario",
}

SUBJECT_KEYWORDS = {
    "Matemática": ("suma", "resta", "multiplicacion", "division", "fraccion", "fracciones", "decimal", "porcentaje", "numero", "numeros", "multiplo", "divisor", "potencia", "raiz", "ecuacion", "inecuacion", "variable", "incognita", "expresion algebraica", "patron", "funcion", "geometria", "figura", "triangulo", "cuadrado", "rectangulo", "circulo", "circunferencia", "angulo", "area", "perimetro", "volumen", "cuerpo geometrico", "plano cartesiano", "promedio", "media", "mediana", "moda", "grafico", "tabla", "datos", "probabilidad", "azar", "posibilidad", "frecuencia", "medida", "medicion"),
    "Ciencias Naturales": ("fotosintesis", "planta", "celula", "cuerpo humano", "sistema respiratorio", "sistema digestivo", "sistema circulatorio", "ecosistema", "habitat", "animales", "energia", "fuerza", "materia", "agua", "planeta", "planetas", "sistema solar", "universo", "cosmos", "agujero negro", "agujeros negros", "galaxia", "galaxias", "estrella", "estrellas", "luna", "sol", "eclipse", "orbit", "satelite", "asteroide", "cometa", "meteorito", "nebulosa", "via lactea", "gravedad", "espacio", "astronomia", "volcan", "terremoto", "alimentacion", "nutrientes", "saludable"),
    "Historia": ("historia", "pasado", "chile", "independencia", "colonia", "pueblos originarios", "mapuche", "incas", "mayas", "aztecas", "guerra", "segunda guerra mundial", "arturo prat", "bernardo ohiggins", "civilizacion", "democracia", "derechos", "constitucion", "region", "geografia", "mapa", "territorio"),
    "Lenguaje": ("metafora", "lenguaje figurado", "sustantivo", "verbo", "adjetivo", "oracion", "texto", "cuento", "poema", "fabula", "leyenda", "mito", "resumen", "idea principal", "sujeto", "predicado", "comprension lectora", "lectura", "escritura", "sinonimo", "antonimo", "narrador", "personaje", "parrafo", "acento", "tilde", "puntuacion"),
}

CONCEPT_SUBJECT_LABELS = {
    "ciencias_naturales": "Ciencias Naturales",
    "matematica": "Matemática",
    "lenguaje": "Lenguaje",
    "historia": "Historia",
}

# Frases históricas específicas: se revisan antes de los términos generales para
# evitar que un desempate de búsqueda cambie la materia cuando no hay fuente local.
HISTORY_PRIORITY_PHRASES = (
    "combate naval de iquique",
    "combate naval",
    "arturo prat",
    "21 de mayo",
    "guerra del pacifico",
    "esmeralda",
    "covadonga",
    "miguel grau",
    "huascar",
    "heroes navales",
    "historia de chile",
    "iquique",
)

ASTRONOMY_PRIORITY_PHRASES = (
    "agujero negro", "agujeros negros", "galaxia", "galaxias", "universo", "cosmos",
    "estrella", "estrellas", "planeta", "planetas", "sistema solar", "luna", "eclipse",
    "orbita", "satelite", "asteroide", "cometa", "meteorito", "nebulosa", "via lactea",
    "gravedad", "fuerza de gravedad", "espacio", "astronomia",
)

HISTORY_CANONICAL_TOPICS = {
    phrase: "combate naval de iquique"
    for phrase in (
        "combate naval de iquique",
        "combate naval",
        "arturo prat",
        "21 de mayo",
        "guerra del pacifico",
        "esmeralda",
        "miguel grau",
        "huascar",
        "iquique",
    )
}

# Equivalencias deliberadamente pequeñas: ayudan a recuperar contenido escolar
# sin convertir palabras genéricas en una coincidencia fuerte por sí solas.
SEARCH_EQUIVALENCES = {
    "fotosintesis": ("plantas", "luz", "clorofila"),
    "habitat": ("ambiente", "ecosistema"),
    "fraccion": ("numerador", "denominador", "entero"),
    "fracciones": ("numerador", "denominador", "entero"),
    "perimetro": ("contorno", "borde"),
    "area": ("superficie",),
    "multiplicacion": ("multiplicar", "producto"),
    "sustantivo": ("nombre", "persona", "animal", "cosa", "lugar"),
    "verbo": ("accion",),
    "resumen": ("resumir", "idea principal"),
    "arturo": ("arturo prat", "combate naval de iquique"),
    "pueblos": ("pueblos originarios", "mapuche", "aymara", "rapa nui"),
    "alimentacion": ("alimentos", "nutrientes", "habitos saludables"),
    "saludable": ("nutrientes", "habitos saludables"),
    "respiratorio": ("respiracion", "pulmones", "oxigeno"),
    "ciclo": ("evaporacion", "condensacion", "precipitacion"),
}

# El contenido curricular cambia poco durante una sesión. Mantenerlo en memoria
# evita recorrer y releer cientos de Markdown en cada pregunta. La recarga queda
# explícita para conservar un comportamiento predecible al editar contenidos.
_content_index: dict[tuple[str, str], tuple[dict, ...]] = {}
_content_index_lock = Lock()
_library_index: tuple[dict, ...] = ()
_library_term_index: dict[str, tuple[dict, ...]] = {}

# Mapa central para cualquier futura carpeta Enciclopedia_*. Cada entrada define
# palabras de ruta, materia escolar y categoría de respaldo.
ENCYCLOPEDIA_AREA_KEYWORDS = (
    (("astronomia", "espacio"), "Ciencias Naturales", "Astronomía y espacio"),
    (("biologia",), "Ciencias Naturales", "Biología"),
    (("fisica",), "Ciencias Naturales", "Física"),
    (("quimica",), "Ciencias Naturales", "Química"),
    (("tierra", "ecologia", "medioambiente"), "Ciencias Naturales", "Ciencias de la Tierra, ecología y medioambiente"),
    (("ciencias", "naturales"), "Ciencias Naturales", "Ciencias Naturales generales"),
    (("estadistica", "probabilidad"), "Matemática", "Estadística y probabilidad"),
    (("medicion",), "Matemática", "Medición"),
    (("funciones",), "Matemática", "Funciones"),
    (("algebra",), "Matemática", "Álgebra"),
    (("aritmetica",), "Matemática", "Aritmética"),
    (("geometria",), "Matemática", "Geometría"),
    (("matematica", "resolucion problemas"), "Matemática", "Matemática general"),
    (("literatura", "lenguaje", "comunicacion"), "Lenguaje", "Literatura"),
    (("tecnologia", "informatica", "programacion"), "Tecnología", "Informática"),
    (("historia", "geografia", "conflictos", "guerras", "ciudadana", "derecho"), "Historia", "Historia, Geografía y Ciencias Sociales"),
)

ENCYCLOPEDIA_FOLDERS = {
    "Enciclopedia_Astronomia_Espacio_1B_a_4M_Chat_Escolar": ("Ciencias Naturales", "Astronomía y espacio"),
    "Enciclopedia_Biologia_1B_a_4M_Chat_Escolar": ("Ciencias Naturales", "Biología"),
    "Enciclopedia_Ciencias_Naturales_Generales_1B_a_4M_Chat_Escolar": ("Ciencias Naturales", "Ciencias Naturales generales"),
    "Enciclopedia_Ciencias_Tierra_Ecologia_Medioambiente_1B_a_4M_Chat_Escolar": ("Ciencias Naturales", "Ciencias de la Tierra, ecología y medioambiente"),
    "Enciclopedia_Fisica_1B_a_4M_Chat_Escolar": ("Ciencias Naturales", "Física"),
    "Enciclopedia_Quimica_1B_a_4M_Chat_Escolar": ("Ciencias Naturales", "Química"),
    "Enciclopedia_Historia_de_Chile_1B_a_4M_Chat_Escolar": ("Historia", "Historia de Chile"),
    "Enciclopedia_Historia_Universal_1B_a_4M_Chat_Escolar": ("Historia", "Historia Universal"),
    "Enciclopedia_Geografia_Chile_Universal_1B_a_4M_Chat_Escolar": ("Historia", "Geografía"),
    "Enciclopedia_Conflictos_Historicos_Guerras_1B_a_4M_Chat_Escolar": ("Historia", "Conflictos históricos y guerras"),
    "Enciclopedia_Educacion_Ciudadana_Formacion_Civica_Derecho_1B_a_4M_Chat_Escolar": ("Historia", "Formación Cívica y Derecho básico"),
}

MATH_CATEGORY_KEYWORDS = (
    (("estadistica", "probabilidad", "promedio", "mediana", "moda", "frecuencia", "datos", "grafico"), "Estadística y probabilidad"),
    (("geometria", "triangulo", "rectangulo", "circulo", "angulo", "perimetro", "area", "volumen", "figura"), "Geometría"),
    (("algebra", "ecuacion", "inecuacion", "variable", "incognita", "expresion", "patron", "funcion"), "Álgebra"),
    (("aritmetica", "fraccion", "decimal", "suma", "resta", "multiplicacion", "division", "porcentaje", "numero"), "Aritmética"),
    (("medicion", "medida", "longitud", "masa", "tiempo", "capacidad"), "Medición"),
)


def _infer_math_category(*values: str) -> str:
    """Provide a stable display category when a Math document omits one."""
    searchable = normalize_text(" ".join(str(value or "") for value in values))
    for keywords, category in MATH_CATEGORY_KEYWORDS:
        if any(keyword in searchable for keyword in keywords):
            return category
    return "Matemática general"


def _encyclopedia_info(relative_path: Path) -> tuple[str, str] | None:
    if not relative_path.parts:
        return None
    folder = relative_path.parts[0]
    if folder in ENCYCLOPEDIA_FOLDERS:
        return ENCYCLOPEDIA_FOLDERS[folder]
    if not folder.startswith("Enciclopedia_"):
        return None
    normalized = normalize_text(folder.removeprefix("Enciclopedia_").replace("1B_a_4M_Chat_Escolar", ""))
    for keywords, area, category in ENCYCLOPEDIA_AREA_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            return area, category
    category = " ".join(word.capitalize() for word in normalized.split()) or "Enciclopedia"
    return "General", category


def _metadata_value(metadata: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\"'\n]+)", metadata)
    if not match:
        return ""
    value = match.group(1).strip()
    try:
        return value.encode("latin-1").decode("utf-8") if "Â" in value else value
    except UnicodeError:
        return value


def _course_number(value: str | None) -> int | None:
    """Orden común para básico y medio, incluso si el documento no usa la ruta antigua."""
    normalized = normalize_text(value or "")
    number = re.search(r"\b([1-8])\D*basico", normalized)
    if number:
        return int(number.group(1))
    number = re.search(r"\b([1-4])\D*medio", normalized)
    return 8 + int(number.group(1)) if number else None


def _infer_library_subject(relative_path: Path, metadata: dict) -> str:
    # Los metadatos del documento prevalecen sobre el nombre de su carpeta.
    declared = normalize_text(metadata.get("area") or metadata.get("asignatura") or "")
    if declared:
        if any(term in declared for term in ("historia", "geografia", "ciudadana")):
            return "Historia"
        if any(term in declared for term in ("matematica", "aritmetica", "algebra", "geometria", "estadistica", "probabilidad", "medicion", "funciones")):
            return "Matemática"
        if any(term in declared for term in ("lenguaje", "literatura", "comunicacion")):
            return "Lenguaje"
        if "tecnologia" in declared:
            return "Tecnología"
        if any(term in declared for term in ("ciencia", "fisica", "quimica", "biologia", "astronomia")):
            return "Ciencias Naturales"
    encyclopedia = _encyclopedia_info(relative_path)
    if encyclopedia:
        return encyclopedia[0]
    area = normalize_text(metadata.get("area") or metadata.get("asignatura") or "")
    path = normalize_text(" ".join(relative_path.parts))
    if any(term in f"{area} {path}" for term in ("historia", "geografia", "ciudadana", "conflictos")):
        return "Historia"
    if any(term in f"{area} {path}" for term in ("matematica", "aritmetica", "algebra", "geometria", "estadistica", "probabilidad", "medicion", "funciones")):
        return "Matemática"
    if any(term in f"{area} {path}" for term in ("lenguaje", "literatura", "comunicacion")):
        return "Lenguaje"
    return "Ciencias Naturales"


def _infer_library_course(relative_path: Path, metadata: dict) -> str:
    return (
        metadata.get("curso_origen")
        or metadata.get("apto_desde")
        or next((folder_to_course_label(part) for part in relative_path.parts if part in COURSE_LABELS), "")
        or ("Enciclopedia 1° básico a 4° medio" if _encyclopedia_info(relative_path) else "Sin curso declarado")
    )


def _single_word_aliases() -> dict[str, str]:
    aliases = {}
    for canonical, concept in EDUCATIONAL_CONCEPTS.items():
        for alias in concept["aliases"]:
            if " " not in alias:
                aliases[alias] = canonical
    return aliases


def _correct_known_token(token: str) -> tuple[str, float]:
    aliases = _single_word_aliases()
    if token in aliases:
        canonical = aliases[token]
        return canonical if " " not in canonical else token, 1.0
    if len(token) < 5:
        return token, 1.0

    best_alias = None
    best_ratio = 0.0
    for alias in aliases:
        if abs(len(alias) - len(token)) > 2:
            continue
        ratio = SequenceMatcher(None, token, alias).ratio()
        if ratio > best_ratio:
            best_alias = alias
            best_ratio = ratio

    # Un umbral bajo confundía palabras válidas (por ejemplo, "consiste") con
    # conceptos no mencionados ("ecosistemas"). Los errores frecuentes que
    # requieren más tolerancia se mantienen como alias explícitos arriba.
    if best_alias and best_ratio >= 0.82:
        canonical = aliases[best_alias]
        return canonical if " " not in canonical else best_alias, best_ratio
    return token, 1.0


def _detect_topic(normalized_question: str) -> str | None:
    for canonical, concept in EDUCATIONAL_CONCEPTS.items():
        if any(alias in normalized_question for alias in sorted(concept["aliases"], key=len, reverse=True)):
            return canonical
    return None


def normalize_question(question: str) -> dict:
    original_text = question
    analysis_text = normalize_text(question)
    raw_tokens = analysis_text.split()
    correction_confidences = []
    corrected_tokens = []

    for index, token in enumerate(raw_tokens):
        if token in {"q", "k", "ke"} and (index == 0 or (index + 1 < len(raw_tokens) and raw_tokens[index + 1] == "es")):
            corrected_tokens.append("que")
            correction_confidences.append(0.95)
            continue
        corrected, confidence = _correct_known_token(token)
        corrected_tokens.append(corrected)
        if corrected != token:
            correction_confidences.append(confidence)

    normalized_question = " ".join(corrected_tokens)
    possible_topic = _detect_topic(normalized_question)
    intent = "definition" if normalized_question.startswith(("que es ", "que son ")) else None
    if intent is None and any(word in corrected_tokens for word in ("saber", "conocer", "explicar")):
        intent = "exploration"

    # Todas las variantes conocidas de la pregunta de hábitat convergen al mismo análisis.
    if intent == "definition" and possible_topic == "habitat":
        normalized_question = "que es un habitat"

    keywords = []
    for token in normalized_question.split():
        if len(token) < 3 or token in STOP_WORDS:
            continue
        keywords.append(token)
        if token.startswith("sum"):
            keywords.append("adicion")
        elif token.startswith("rest"):
            keywords.append("sustraccion")

    if possible_topic:
        keywords.extend(possible_topic.split())

    # Las entidades del mismo hecho histórico convergen al título canónico para
    # que una consulta breve ("Esmeralda" o "21 de mayo") recupere la fuente
    # específica y no una coincidencia débil de otra materia.
    for phrase, canonical_topic in HISTORY_CANONICAL_TOPICS.items():
        if phrase in normalized_question:
            keywords.append(canonical_topic)
            break

    # Las equivalencias se conservan como contexto relacionado, pero no se
    # mezclan con las palabras principales: así una mención de "plantas" no
    # puede convertir una referencia secundaria a fotosíntesis en fuente exacta.
    equivalent_keywords = [
        equivalent
        for keyword in keywords
        for equivalent in SEARCH_EQUIVALENCES.get(keyword, ())
    ]

    possible_subject = (
        EDUCATIONAL_CONCEPTS[possible_topic]["subject"] if possible_topic else None
    )
    confidence = min(correction_confidences, default=1.0)

    return {
        "original_text": original_text,
        "normalized_text": normalized_question,
        "intent": intent,
        "keywords": list(dict.fromkeys(keywords)),
        "equivalent_keywords": list(dict.fromkeys(equivalent_keywords)),
        "possible_subject": possible_subject,
        "possible_topic": possible_topic,
        "confidence": round(confidence, 2),
    }


def detect_subject_from_question(question: str) -> tuple[str | None, float]:
    """Return a conservative local subject guess and its keyword confidence."""
    analysis = normalize_question(question)
    normalized = analysis["normalized_text"]
    concept_subject = CONCEPT_SUBJECT_LABELS.get(analysis.get("possible_subject", ""))
    if concept_subject:
        return concept_subject, 1.0
    if any(phrase in normalized for phrase in HISTORY_PRIORITY_PHRASES):
        return "Historia", 1.0
    if any(phrase in normalized for phrase in ASTRONOMY_PRIORITY_PHRASES):
        return "Ciencias Naturales", 1.0
    scores = {
        subject: sum(1 for keyword in keywords if keyword in normalized)
        for subject, keywords in SUBJECT_KEYWORDS.items()
    }
    best_subject, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return None, 0.0
    second_score = sorted(scores.values(), reverse=True)[1]
    confidence = 0.9 if best_score > second_score else 0.6
    return best_subject, confidence


def question_keywords(question: str) -> list[str]:
    return normalize_question(question)["keywords"]


def strip_front_matter(content: str) -> str:
    if not content.startswith("---"):
        return content
    parts = content.split("---", 2)
    return parts[2].lstrip() if len(parts) == 3 else content


def parse_front_matter(content: str) -> dict:
    if not content.startswith("---"):
        return {"topic": "", "subject": "", "keywords": []}
    parts = content.split("---", 2)
    if len(parts) != 3:
        return {"topic": "", "subject": "", "keywords": []}

    metadata = parts[1]
    topic = _metadata_value(metadata, "tema") or _metadata_value(metadata, "titulo")
    subject = _metadata_value(metadata, "asignatura") or _metadata_value(metadata, "area")
    keyword_block = re.search(r"(?ms)^palabras_clave:\s*\n((?:\s+-[^\n]*\n?)*)", metadata)
    keywords = []
    if keyword_block:
        keywords = [
            item.strip().strip('"\'')
            for item in re.findall(r"(?m)^\s+-\s*(.+)$", keyword_block.group(1))
        ]
    return {
        "topic": topic,
        "subject": subject,
        "keywords": keywords,
        "area": _metadata_value(metadata, "area"),
        "category": _metadata_value(metadata, "categoria"),
        "course_origin": _metadata_value(metadata, "curso_origen"),
        "origin_level": _metadata_value(metadata, "nivel_origen") or _metadata_value(metadata, "nivel"),
        "suitable_from": _metadata_value(metadata, "apto_desde"),
        "content_type": _metadata_value(metadata, "tipo_contenido"),
        "requires_verified_source": _metadata_value(metadata, "requiere_fuente_verificada"),
    }


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            return re.sub(r"^Tema:\s*", "", title, flags=re.IGNORECASE)
    return fallback.replace("_", " ").strip().title()


def extract_headings(content: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"(?m)^#{1,6}\s+(.+)$", content)
    ]


def _is_related_section(heading: str) -> bool:
    normalized_heading = normalize_text(heading)
    return any(hint in normalized_heading for hint in RELATED_SECTION_HINTS)


def is_primary_content_file(file_path: Path) -> bool:
    parts = {normalize_text(part) for part in file_path.parts}
    if parts.intersection(NON_PRIMARY_SOURCE_PARTS):
        return False
    return not file_path.stem.startswith(NON_PRIMARY_FILE_PREFIXES)


def extract_sections(content: str) -> list[dict]:
    sections = []
    current_heading = "Contenido principal"
    current_lines = []

    for line in content.splitlines():
        heading_match = re.match(r"^#{1,6}\s+(.+)$", line)
        if heading_match:
            if current_lines:
                sections.append(
                    {"heading": current_heading, "text": "\n".join(current_lines)}
                )
            current_heading = heading_match.group(1).strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_lines:
        sections.append({"heading": current_heading, "text": "\n".join(current_lines)})
    return sections


def find_related_section(content: str, keywords: list[str], sections: list[dict] | None = None) -> dict | None:
    matches = []
    for section in sections or extract_sections(content):
        normalized_heading = section.get("normalized_heading") or normalize_text(section["heading"])
        normalized_text = section.get("normalized_text") or normalize_text(section["text"])
        if not any(keyword in normalized_text or keyword in normalized_heading for keyword in keywords):
            continue
        heading_match = any(keyword in normalized_heading for keyword in keywords)
        matches.append(
            {
                "heading": section["heading"],
                "text": section["text"],
                "heading_match": heading_match,
                "explicit_related_section": section.get("explicit_related_section", _is_related_section(section["heading"])),
            }
        )

    if not matches:
        return None

    matches.sort(
        key=lambda item: (
            not item["explicit_related_section"],
            item["heading_match"],
        )
    )
    selected = matches[0]
    heading = selected["heading"]
    if selected["explicit_related_section"]:
        reason = f"El tema aparece en la sección \"{heading}\" como conexión o relación con otro contenido."
    elif selected["heading_match"]:
        reason = f"El tema aparece como subtítulo en \"{heading}\", pero no alcanzó la confianza para usarlo como fuente principal."
    else:
        reason = f"El tema se menciona dentro de \"{heading}\", pero no es el foco principal del archivo."

    return {
        "section": heading,
        "summary": reason,
        "excerpt": make_excerpt(selected["text"], keywords, max_length=360),
    }


def clean_excerpt(value: str) -> str:
    value = re.sub(r"(?m)^#{1,6}\s*", "", value)
    value = re.sub(r"(?m)^[-*>]+\s*", "", value)
    value = value.replace("`", "")
    return " ".join(value.split())


def make_excerpt(content: str, keywords: list[str], max_length: int = 800) -> str:
    plain_content = clean_excerpt(content)
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", plain_content) if item.strip()]
    if not sentences:
        return ""

    best_index = max(
        range(len(sentences)),
        key=lambda index: sum(normalize_text(sentences[index]).count(keyword) for keyword in keywords),
    )
    selected = []
    for sentence in sentences[best_index:]:
        candidate = " ".join([*selected, sentence])
        if len(candidate) > max_length:
            break
        selected.append(sentence)
        if len(candidate) >= max_length * 0.65:
            break

    excerpt = " ".join(selected)
    if excerpt:
        return excerpt

    shortened = sentences[best_index][:max_length]
    boundary = max(shortened.rfind(". "), shortened.rfind("; "), shortened.rfind(": "))
    if boundary >= max_length // 3:
        shortened = shortened[: boundary + 1]
    else:
        shortened = shortened.rsplit(" ", 1)[0]
    return f"{shortened.rstrip()}…"


def _score_document(document: dict, keywords: list[str]) -> dict:
    content = document["content"]
    fields = document["fields"]
    weights = {
        "filename": 14,
        "path": 14,
        "title": 14,
        "topic": 12,
        "category": 12,
        "collection": 16,
        "headings": 8,
        "explicit_keywords": 10,
    }
    score = 0
    high_signal_matches = set()
    matched_terms = set()
    for keyword in keywords:
        for field, weight in weights.items():
            if keyword in fields[field]:
                score += weight
                high_signal_matches.add(keyword)
                matched_terms.add(keyword)
        score += min(fields["body"].count(keyword), 2)
        if keyword in fields["body"]:
            matched_terms.add(keyword)

    if high_signal_matches:
        score += 4  # La carpeta de materia ya fue validada antes de puntuar.

    # Analizar todas las secciones de miles de documentos solo es necesario
    # cuando no existe una señal principal; de otro modo la búsqueda transversal
    # se vuelve innecesariamente lenta.
    related_section = None if high_signal_matches else find_related_section(
        content, keywords, sections=document["sections"]
    )
    return {
        "title": document["title"],
        "content": content,
        "score": score,
        "high_signal_matches": high_signal_matches,
        "matched_terms": matched_terms,
        "is_exact_match": any(
            keyword in fields["title"] or keyword in fields["topic"]
            for keyword in keywords
        ),
        "related_section": related_section,
    }


def _make_base_result(analysis: dict, minimum_score: int) -> dict:
    return {
        "provenance_status": DEMO_FALLBACK,
        "results": [],
        "related_results": [],
        "query_analysis": analysis,
        "minimum_score": minimum_score,
        "best_score": 0,
        "effective_course": None,
        "source_course": None,
        "source_subject": None,
        "found_in_other_course": False,
        "searched_courses": [],
        "confidence": "none",
        "reason": "No se encontró una fuente local útil para esta pregunta.",
    }


def _build_content_index(search_scopes: list[tuple[str, str]] | None = None) -> dict[tuple[str, str], tuple[dict, ...]]:
    if not CONTENT_ROOT.is_dir():
        return {}

    requested_scopes = set(search_scopes) if search_scopes is not None else None
    documents_by_scope: dict[tuple[str, str], list[dict]] = {
        scope: [] for scope in requested_scopes or ()
    }
    for file_path in sorted(CONTENT_ROOT.rglob("*.md")):
        try:
            relative_path = file_path.relative_to(CONTENT_ROOT)
        except ValueError:
            continue
        if len(relative_path.parts) < 3 or not is_primary_content_file(relative_path):
            continue
        scope = (relative_path.parts[0], relative_path.parts[1])
        if requested_scopes is not None and scope not in requested_scopes:
            continue
        try:
            raw_content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue

        content = strip_front_matter(raw_content)
        metadata = parse_front_matter(raw_content)
        encyclopedia = _encyclopedia_info(relative_path)
        if encyclopedia:
            metadata["area"] = metadata.get("area") or encyclopedia[0]
            metadata["category"] = metadata.get("category") or encyclopedia[1]
        title = extract_title(content, file_path.stem)
        direct_headings = [
            heading for heading in extract_headings(content) if not _is_related_section(heading)
        ]
        sections = [
            {
                **section,
                "normalized_heading": normalize_text(section["heading"]),
                "normalized_text": normalize_text(section["text"]),
                "explicit_related_section": _is_related_section(section["heading"]),
            }
            for section in extract_sections(content)
        ]
        documents_by_scope.setdefault(scope, []).append({
            "file_path": file_path,
            "relative_path": relative_path.as_posix(),
            "course_folder": relative_path.parts[0],
            "subject_folder": relative_path.parts[1],
            "content": content,
            "title": title,
            "sections": sections,
            "fields": {
                "filename": normalize_text(file_path.stem),
                "path": normalize_text(relative_path.as_posix()),
                "title": normalize_text(title),
                "topic": normalize_text(metadata["topic"]),
                "category": normalize_text(metadata.get("category", "")),
                "collection": "",
                "headings": normalize_text(" ".join(direct_headings)),
                "explicit_keywords": normalize_text(" ".join(metadata["keywords"])),
                "body": normalize_text(content),
            },
        })
    return {
        scope: tuple(documents)
        for scope, documents in documents_by_scope.items()
    }


def _is_library_document(relative_path: Path) -> bool:
    """Exclude navigation and maintenance files, never a curricular Markdown by folder name."""
    normalized_parts = {normalize_text(part) for part in relative_path.parts}
    if normalized_parts.intersection({"00_documentacion", "documentacion", "bancos"}):
        return False
    name = normalize_text(relative_path.name)
    return not (
        name.startswith(("00_indice", "readme", "changelog"))
        or "indice_maestro" in name
    )


def _build_library_index() -> tuple[dict, ...]:
    if not CONTENT_ROOT.is_dir():
        return ()
    documents = []
    for file_path in sorted(CONTENT_ROOT.rglob("*.md")):
        try:
            relative_path = file_path.relative_to(CONTENT_ROOT)
        except ValueError:
            continue
        if not _is_library_document(relative_path):
            continue
        try:
            raw_content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        content = strip_front_matter(raw_content)
        metadata = parse_front_matter(raw_content)
        encyclopedia = _encyclopedia_info(relative_path)
        if encyclopedia:
            metadata["area"] = metadata.get("area") or encyclopedia[0]
            metadata["category"] = metadata.get("category") or encyclopedia[1]
        title = extract_title(content, file_path.stem)
        headings = [heading for heading in extract_headings(content) if not _is_related_section(heading)]
        course = _infer_library_course(relative_path, metadata)
        subject = _infer_library_subject(relative_path, metadata)
        if subject == "Ciencias Naturales" and any(
            term in normalize_text(f"{metadata.get('area', '')} {metadata.get('category', '')} {relative_path}")
            for term in ("ciencias de la tierra", "ecologia", "medioambiente", "hidrolog")
        ):
            metadata["display_category"] = "Ciencias de la Tierra"
        if subject == "Matemática":
            metadata["category"] = _infer_math_category(
                metadata.get("area", ""), metadata.get("category", ""),
                relative_path.as_posix(), title,
            )
        documents.append({
            "file_path": file_path,
            "relative_path": relative_path.as_posix(),
            "content": content,
            "title": title,
            "course": course,
            "course_number": _course_number(course),
            "subject": subject,
            "collection_category": encyclopedia[1] if encyclopedia else "",
            "metadata": metadata,
            "sections": [
                {**section, "normalized_heading": normalize_text(section["heading"]),
                 "normalized_text": normalize_text(section["text"]),
                 "explicit_related_section": _is_related_section(section["heading"])}
                for section in extract_sections(content)
            ],
            "fields": {
                "filename": normalize_text(file_path.stem), "title": normalize_text(title),
                "path": normalize_text(relative_path.as_posix()),
                "topic": normalize_text(metadata.get("topic", "")),
                "category": normalize_text(metadata.get("category", "")),
                "collection": normalize_text(encyclopedia[1] if encyclopedia else ""),
                "headings": normalize_text(" ".join(headings)),
                "explicit_keywords": normalize_text(" ".join(metadata.get("keywords", []))),
                "body": normalize_text(content),
            },
        })
    return tuple(documents)


def reload_local_content_index() -> int:
    """Recarga el índice local después de editar archivos Markdown en caliente."""
    global _content_index, _library_index, _library_term_index
    with _content_index_lock:
        # La búsqueda actual usa el índice transversal; conservar el contenedor
        # antiguo vacío evita leer dos veces los mismos Markdown al recargar.
        _content_index = {}
        _library_index = _build_library_index()
        _library_term_index = _build_library_term_index(_library_index)
        return len(_library_index)


def _get_library_index() -> tuple[dict, ...]:
    global _library_index, _library_term_index
    if not _library_index:
        with _content_index_lock:
            if not _library_index:
                _library_index = _build_library_index()
                _library_term_index = _build_library_term_index(_library_index)
    return _library_index


def _build_library_term_index(documents: tuple[dict, ...]) -> dict[str, tuple[dict, ...]]:
    terms: dict[str, list[dict]] = {}
    for document in documents:
        # El índice inverso usa solo señales editoriales. El cuerpo se evalúa
        # después, únicamente para los documentos candidatos.
        signal = " ".join(document["fields"][field] for field in ("filename", "path", "title", "topic", "category", "collection", "headings", "explicit_keywords"))
        for term in set(signal.split()):
            if len(term) >= 3:
                terms.setdefault(term, []).append(document)
    return {term: tuple(items) for term, items in terms.items()}


def _get_content_index(search_scopes: list[tuple[str, str]]) -> tuple[dict, ...]:
    requested_scopes = set(search_scopes)
    missing_scopes = requested_scopes.difference(_content_index)
    if missing_scopes:
        with _content_index_lock:
            missing_scopes = requested_scopes.difference(_content_index)
            if missing_scopes:
                _content_index.update(_build_content_index(list(missing_scopes)))
    return tuple(
        document
        for scope in requested_scopes
        for document in _content_index.get(scope, ())
    )


def _candidate_from_document(
    document: dict,
    course_folder: str,
    subject_folder: str,
    keywords: list[str],
) -> dict | None:
    file_path = document["file_path"]
    scored = _score_document(document, keywords)
    if scored["score"] <= 0:
        return None

    return {
        "title": scored["title"],
        "path": document["relative_path"],
        "score": scored["score"],
        "excerpt": make_excerpt(scored["content"], keywords),
        "coherent": bool(scored["high_signal_matches"]),
        "matched_terms": sorted(scored["matched_terms"]),
        "is_exact_match": scored["is_exact_match"],
        "related_section": scored["related_section"],
        "course": folder_to_course_label(course_folder),
        "course_folder": course_folder,
        "subject": subject_folder,
    }


def _collect_candidates(search_scopes: list[tuple[str, str]], keywords: list[str]) -> list[dict]:
    candidates = []
    scope_set = set(search_scopes)
    for document in _get_content_index(search_scopes):
        course_folder = document["course_folder"]
        subject_folder = document["subject_folder"]
        if (course_folder, subject_folder) not in scope_set:
            continue
        candidate = _candidate_from_document(document, course_folder, subject_folder, keywords)
        if candidate:
            candidates.append(candidate)
    return candidates


def _rank_candidates(candidates: list[dict], preferred_course_folder: str | None = None) -> list[dict]:
    return sorted(
        candidates,
        key=lambda item: (
            -item["score"],
            item["course_folder"] != preferred_course_folder if preferred_course_folder else False,
            item["path"],
        ),
    )


def _library_subject_matches(document_subject: str, selected_subject: str) -> bool:
    """Compare display subjects with legacy folder identifiers safely."""
    document = normalize_text(document_subject)
    selected = normalize_text(selected_subject)
    canonical = next(
        (
            subject for token, subject in (
                ("matematica", "matematica"),
                ("ciencias", "ciencias naturales"),
                ("historia", "historia"),
                ("lenguaje", "lenguaje"),
                ("tecnologia", "tecnologia"),
            )
            if token in selected
        ),
        selected,
    )
    return document == canonical


def _collect_library_candidates(keywords: list[str], selected_subject: str, profile_course: str) -> list[dict]:
    """Search every installed collection; profile course only affects ranking, never scope."""
    candidates = []
    preferred_number = _course_number(profile_course)
    selected_subject_normalized = normalize_text(selected_subject)
    _get_library_index()
    # Recupera títulos/editoriales en singular o plural (agujero/agujeros)
    # sin depender de una carpeta o documento con una forma exacta.
    search_keywords = list(keywords)
    for keyword in keywords:
        if len(keyword) < 4:
            continue
        search_keywords.append(keyword[:-1] if keyword.endswith("s") else f"{keyword}s")
    search_keywords = list(dict.fromkeys(search_keywords))
    is_water_cycle_query = {"ciclo", "agua"}.issubset(set(search_keywords))
    is_metaphor_query = "metafora" in search_keywords
    matching_documents = {
        id(document): document
        for keyword in search_keywords
        for document in _library_term_index.get(keyword, ())
    }
    # Sin una señal editorial no se recorre el cuerpo completo de la biblioteca.
    # Esto evita que una pregunta sin fuente tarde lo mismo que una coincidencia real.
    for document in matching_documents.values():
        if not _library_subject_matches(document["subject"], selected_subject_normalized):
            continue
        scored = _score_document(document, search_keywords)
        if scored["score"] <= 0:
            continue
        score = scored["score"]
        if is_water_cycle_query:
            exact_topic_fields = " ".join(
                document["fields"][field]
                for field in ("filename", "title", "topic", "headings", "explicit_keywords")
            )
            if "ciclo del agua" in exact_topic_fields:
                score += 100
            elif any(term in exact_topic_fields for term in ("reuso de aguas", "contaminacion del agua", "cuidado del agua")):
                score -= 40
        if is_metaphor_query:
            exact_topic_fields = " ".join(
                document["fields"][field]
                for field in ("filename", "title", "topic", "headings", "explicit_keywords")
            )
            if "lenguaje figurado" in exact_topic_fields or "metafora" in exact_topic_fields:
                # Las palabras de intención ("ejemplo", "pregunta") aparecen
                # en muchas guías. El concepto explícito debe conservar la fuente
                # de Lenguaje figurado por encima de esas coincidencias genéricas.
                score += 250
        if document.get("collection_category") == "Astronomía y espacio" and any(
            phrase in " ".join(search_keywords) for phrase in ASTRONOMY_PRIORITY_PHRASES
        ):
            score += 24
        if normalize_text(document["subject"]) == selected_subject_normalized:
            score += 6
        distance = 99
        if preferred_number is not None and document["course_number"] is not None:
            distance = abs(document["course_number"] - preferred_number)
            score += max(0, 4 - distance)
        metadata = document["metadata"]
        candidates.append({
            "title": scored["title"], "path": document["relative_path"], "score": score,
            # Creating excerpts normalizes and splits a full document. Defer it
            # until a candidate has actually won the ranking.
            "excerpt": "",
            "coherent": bool(scored["high_signal_matches"]),
            "matched_terms": sorted(scored["matched_terms"]), "is_exact_match": scored["is_exact_match"],
            "related_section": scored["related_section"], "course": document["course"],
            "course_folder": "", "subject": document["subject"], "course_distance": distance,
            "_document": document,
            "metadata": {
                "title": document["title"], "area": metadata.get("area", ""),
                "category": metadata.get("category", ""), "course_origin": document["course"],
                "display_category": metadata.get("display_category", ""),
                "origin_level": metadata.get("origin_level", ""), "suitable_from": metadata.get("suitable_from", ""),
                "keywords": metadata.get("keywords", []), "related_subjects": metadata.get("related_subjects", []),
                "content_type": metadata.get("content_type", ""),
                "requires_verified_source": metadata.get("requires_verified_source", ""),
            },
        })
    return sorted(candidates, key=lambda item: (-item["score"], item["course_distance"], item["path"]))


def _format_retrieval_result(
    base_result: dict,
    candidates: list[dict],
    possible_topic: str | None,
    topic_config: dict,
    effective_course: str,
    preferred_course_folder: str | None,
    selected_subject: str,
    limit: int,
    minimum_score: int,
) -> dict:
    candidates = _rank_candidates(candidates, preferred_course_folder)
    best_score = candidates[0]["score"] if candidates else 0
    searched_courses = list(dict.fromkeys(candidate["course"] for candidate in candidates))
    common_metadata = {
        "best_score": best_score,
        "effective_course": effective_course,
        "searched_courses": searched_courses,
    }

    verified = []
    seen_titles = set()
    for candidate in candidates:
        normalized_title = normalize_text(f"{candidate['course']} {candidate['title']}")
        if (
            not candidate["coherent"]
            or candidate["score"] < minimum_score
            or normalized_title in seen_titles
        ):
            continue
        seen_titles.add(normalized_title)
        verified.append({
            key: candidate[key]
            for key in ("title", "path", "score", "course", "subject", "matched_terms", "is_exact_match")
        })
        document = candidate.get("_document")
        verified[-1]["excerpt"] = (
            make_excerpt(document["content"], base_result["query_analysis"]["keywords"])
            if document else candidate.get("excerpt", "")
        )
        if candidate.get("metadata"):
            verified[-1]["metadata"] = candidate["metadata"]
        if len(verified) >= max(1, min(limit, MAX_RESULTS)):
            break

    if verified:
        source_course = verified[0]["course"]
        found_in_other_course = effective_course != "Todos los cursos" and effective_course != source_course
        return {
            **base_result,
            **common_metadata,
            "provenance_status": LOCAL_VERIFIED,
            "results": verified,
            "source_course": source_course,
            "source_subject": selected_subject,
            "found_in_other_course": found_in_other_course,
            "confidence": "high",
            "reason": "Coincidencia fuerte en título, tema, encabezados o palabras clave del contenido local.",
        }

    if candidates:
        # Solo si no hubo fuente principal se inspeccionan las secciones de las
        # mejores coincidencias para informar una relación secundaria.
        for candidate in candidates[:20]:
            if candidate["related_section"] is None:
                document = candidate.get("_document")
                if document:
                    candidate["related_section"] = find_related_section(
                        document["content"], base_result["query_analysis"]["keywords"],
                        sections=document["sections"],
                    )
        related_candidates = [
            {
                "title": candidate["title"],
                "path": candidate["path"],
                "score": candidate["score"],
                "section": candidate["related_section"]["section"],
                "summary": candidate["related_section"]["summary"],
                "excerpt": candidate["related_section"]["excerpt"],
                "course": candidate["course"],
                "subject": candidate["subject"],
                "matched_terms": candidate["matched_terms"],
                "is_exact_match": candidate["is_exact_match"],
            }
            for candidate in candidates
            if candidate["related_section"]
        ]
        if possible_topic and not topic_config.get("external") and related_candidates:
            source_course = related_candidates[0]["course"]
            found_in_other_course = effective_course != "Todos los cursos" and effective_course != source_course
            return {
                **base_result,
                **common_metadata,
                "provenance_status": LOCAL_RELATED,
                "related_results": related_candidates[: max(1, min(limit, MAX_RESULTS))],
                "source_course": source_course,
                "source_subject": selected_subject,
                "found_in_other_course": found_in_other_course,
                "confidence": "related",
                "reason": "El tema aparece como relación o mención secundaria, no como fuente principal.",
            }
        return {
            **base_result,
            **common_metadata,
            "provenance_status": LOCAL_LOW_CONFIDENCE,
            "confidence": "low",
            "reason": "Solo hubo coincidencias débiles; no se usan como fuente educativa principal.",
        }

    return {
        **base_result,
        "provenance_status": NO_LOCAL_CONTENT,
        "effective_course": effective_course,
        "source_subject": selected_subject,
    }


def retrieve_local_content(
    course: str,
    subject: str,
    question: str,
    mode: str | None = None,
    limit: int = MAX_RESULTS,
    minimum_score: int = MIN_RELEVANCE_SCORE,
) -> dict:
    analysis = normalize_question(question)
    course_folder = course_to_folder(course)
    selected_subject = subject_to_folder(subject)
    explorer_mode = is_explorer_mode(mode)
    global_search = is_all_courses(course)
    possible_topic = analysis["possible_topic"]
    topic_config = EDUCATIONAL_CONCEPTS.get(possible_topic or "", {})

    base_result = _make_base_result(analysis, minimum_score)
    effective_course = "Todos los cursos" if global_search else (folder_to_course_label(course_folder) if course_folder else course)

    if not selected_subject:
        return {
            **base_result,
            "provenance_status": NO_LOCAL_CONTENT,
            "effective_course": effective_course,
        }
    if not analysis["keywords"]:
        return {
            **base_result,
            "provenance_status": NO_LOCAL_CONTENT,
            "effective_course": effective_course,
        }

    # La biblioteca es transversal: nunca se filtra por el curso o materia del perfil.
    # Esos datos son señales suaves de ordenamiento y de adaptación de la respuesta.
    candidates = _collect_library_candidates(analysis["keywords"], selected_subject, course)
    return _format_retrieval_result(
        base_result,
        candidates,
        possible_topic,
        topic_config,
        effective_course,
        course_folder,
        selected_subject,
        limit,
        minimum_score,
    )


def search_local_content(
    course: str,
    subject: str,
    question: str,
    limit: int = MAX_RESULTS,
    mode: str | None = None,
) -> list[dict]:
    """Compatibilidad con el contrato anterior: solo retorna fuentes verificadas."""
    return retrieve_local_content(course, subject, question, mode=mode, limit=limit)["results"]
