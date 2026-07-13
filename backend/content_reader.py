import re
from difflib import SequenceMatcher
from pathlib import Path

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
        "aliases": {"habitat", "habitats"},
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
    "Matemática": ("suma", "resta", "multiplicacion", "division", "fraccion", "fracciones", "decimal", "porcentaje", "numero", "ecuacion", "geometria", "angulo", "area", "perimetro", "volumen", "grafico", "tabla", "probabilidad", "medida"),
    "Ciencias Naturales": ("fotosintesis", "planta", "celula", "cuerpo humano", "sistema respiratorio", "sistema digestivo", "sistema circulatorio", "ecosistema", "habitat", "animales", "energia", "fuerza", "materia", "agua", "planeta", "sistema solar", "universo", "volcan", "terremoto", "alimentacion", "nutrientes", "saludable"),
    "Historia": ("historia", "pasado", "chile", "independencia", "colonia", "pueblos originarios", "mapuche", "incas", "mayas", "aztecas", "guerra", "segunda guerra mundial", "arturo prat", "bernardo ohiggins", "civilizacion", "democracia", "derechos", "constitucion", "region", "geografia", "mapa", "territorio"),
    "Lenguaje": ("sustantivo", "verbo", "adjetivo", "oracion", "texto", "cuento", "poema", "fabula", "leyenda", "mito", "resumen", "comprension lectora", "lectura", "escritura", "sinonimo", "antonimo", "narrador", "personaje", "parrafo", "acento", "tilde", "puntuacion"),
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
}


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

    if best_alias and best_ratio >= 0.72:
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
    normalized = normalize_question(question)["normalized_text"]
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
    topic_match = re.search(r'(?m)^tema:\s*["\']?([^"\'\n]+)', metadata)
    subject_match = re.search(r'(?m)^asignatura:\s*["\']?([^"\'\n]+)', metadata)
    keyword_block = re.search(r"(?ms)^palabras_clave:\s*\n((?:\s+-[^\n]*\n?)*)", metadata)
    keywords = []
    if keyword_block:
        keywords = [
            item.strip().strip('"\'')
            for item in re.findall(r"(?m)^\s+-\s*(.+)$", keyword_block.group(1))
        ]
    return {
        "topic": topic_match.group(1).strip() if topic_match else "",
        "subject": subject_match.group(1).strip() if subject_match else "",
        "keywords": keywords,
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


def find_related_section(content: str, keywords: list[str]) -> dict | None:
    matches = []
    for section in extract_sections(content):
        normalized_heading = normalize_text(section["heading"])
        normalized_text = normalize_text(section["text"])
        if not any(keyword in normalized_text or keyword in normalized_heading for keyword in keywords):
            continue
        heading_match = any(keyword in normalized_heading for keyword in keywords)
        matches.append(
            {
                "heading": section["heading"],
                "text": section["text"],
                "heading_match": heading_match,
                "explicit_related_section": _is_related_section(section["heading"]),
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


def _score_document(file_path: Path, raw_content: str, keywords: list[str]) -> dict:
    content = strip_front_matter(raw_content)
    metadata = parse_front_matter(raw_content)
    title = extract_title(content, file_path.stem)
    headings = extract_headings(content)
    direct_headings = [
        heading for heading in headings if not _is_related_section(heading)
    ]
    fields = {
        "filename": normalize_text(file_path.stem),
        "title": normalize_text(title),
        "topic": normalize_text(metadata["topic"]),
        "headings": normalize_text(" ".join(direct_headings)),
        "explicit_keywords": normalize_text(" ".join(metadata["keywords"])),
        "body": normalize_text(content),
    }
    weights = {
        "filename": 14,
        "title": 14,
        "topic": 12,
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

    return {
        "title": title,
        "content": content,
        "score": score,
        "high_signal_matches": high_signal_matches,
        "matched_terms": matched_terms,
        "is_exact_match": any(
            keyword in fields["title"] or keyword in fields["topic"]
            for keyword in keywords
        ),
        "related_section": find_related_section(content, keywords),
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


def _candidate_from_file(
    file_path: Path,
    course_folder: str,
    subject_folder: str,
    keywords: list[str],
) -> dict | None:
    if not is_primary_content_file(file_path.relative_to(CONTENT_ROOT)):
        return None
    try:
        raw_content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None

    scored = _score_document(file_path, raw_content, keywords)
    if scored["score"] <= 0:
        return None
    try:
        relative_path = file_path.relative_to(CONTENT_ROOT).as_posix()
    except ValueError:
        return None

    return {
        "title": scored["title"],
        "path": relative_path,
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
    for course_folder, subject_folder in search_scopes:
        search_folder = CONTENT_ROOT / course_folder / subject_folder
        if not search_folder.is_dir():
            continue
        for file_path in sorted(search_folder.rglob("*.md")):
            candidate = _candidate_from_file(file_path, course_folder, subject_folder, keywords)
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
            for key in ("title", "path", "score", "excerpt", "course", "subject", "matched_terms", "is_exact_match")
        })
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
    effective_course = "Todos los cursos" if global_search else folder_to_course_label(course_folder or "")

    if (not course_folder and not global_search) or not selected_subject:
        return {
            **base_result,
            "provenance_status": NO_LOCAL_CONTENT,
            "effective_course": effective_course,
        }
    if not analysis["keywords"]:
        return {
            **base_result,
            "provenance_status": CLARIFICATION_REQUIRED,
            "effective_course": effective_course,
        }

    if topic_config.get("external"):
        return {
            **base_result,
            "provenance_status": NO_LOCAL_CONTENT,
            "effective_course": effective_course,
        }

    possible_subject = analysis["possible_subject"]
    if possible_subject and possible_subject != selected_subject:
        return {
            **base_result,
            "provenance_status": CLARIFICATION_REQUIRED,
            "effective_course": effective_course,
        }

    if global_search or explorer_mode:
        search_scopes = [
            (course_name, selected_subject)
            for course_name in COURSE_LABELS
        ]
    else:
        search_scopes = [(course_folder, selected_subject)]

    candidates = _collect_candidates(search_scopes, analysis["keywords"])
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
