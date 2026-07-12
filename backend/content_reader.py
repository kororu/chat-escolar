import re
from pathlib import Path
from unicodedata import normalize

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "contenidos"

COURSE_FOLDERS = {
    "1 basico": "primero_basico",
    "1o basico": "primero_basico",
    "primero basico": "primero_basico",
    "5 basico": "quinto_basico",
    "5o basico": "quinto_basico",
    "quinto basico": "quinto_basico",
    "6 basico": "sexto_basico",
    "6o basico": "sexto_basico",
    "sexto basico": "sexto_basico",
}

SUBJECT_FOLDERS = {
    "lenguaje": "lenguaje",
    "lenguaje y comunicacion": "lenguaje",
    "matematica": "matematica",
    "ciencias naturales": "ciencias_naturales",
    "historia": "historia_geografia",
    "historia geografia y ciencias sociales": "historia_geografia",
    "modo explorador": "modo_explorador",
    "explorador": "modo_explorador",
}

STOP_WORDS = {
    "al", "algo", "como", "con", "cual", "cuando", "de", "del", "desde",
    "donde", "el", "ella", "en", "es", "esta", "este", "esto", "hay", "la",
    "las", "lo", "los", "mas", "me", "mi", "para", "por", "que", "se", "sin",
    "son", "su", "sus", "un", "una", "unas", "unos", "y",
}


def normalize_text(value: str) -> str:
    without_accents = normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    clean_value = re.sub(r"[^a-z0-9]+", " ", without_accents.lower())
    return " ".join(clean_value.split())


def course_to_folder(course: str) -> str | None:
    normalized_course = normalize_text(course).replace("°", "")
    return COURSE_FOLDERS.get(normalized_course)


def subject_to_folder(subject: str) -> str | None:
    return SUBJECT_FOLDERS.get(normalize_text(subject))


def question_keywords(question: str) -> list[str]:
    keywords = []
    for word in normalize_text(question).split():
        if len(word) < 3 or word in STOP_WORDS:
            continue
        keywords.append(word)
        if word.startswith("sum"):
            keywords.append("adicion")
        elif word.startswith("rest"):
            keywords.append("sustraccion")

    return list(dict.fromkeys(keywords))


def strip_front_matter(content: str) -> str:
    if not content.startswith("---"):
        return content

    parts = content.split("---", 2)
    return parts[2].lstrip() if len(parts) == 3 else content


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            return re.sub(r"^Tema:\s*", "", title, flags=re.IGNORECASE)
    return fallback.replace("_", " ").strip().title()


def clean_excerpt(value: str) -> str:
    value = re.sub(r"(?m)^#{1,6}\s*", "", value)
    value = re.sub(r"(?m)^[-*>]+\s*", "", value)
    value = value.replace("`", "")
    return " ".join(value.split())


def make_excerpt(content: str, keywords: list[str], max_length: int = 800) -> str:
    normalized_content = normalize_text(content)
    match_positions = [
        normalized_content.find(keyword)
        for keyword in keywords
        if normalized_content.find(keyword) >= 0
    ]
    normalized_position = min(match_positions) if match_positions else 0

    if normalized_position == 0:
        fragment = content[: max_length + 200]
    else:
        ratio = normalized_position / max(len(normalized_content), 1)
        source_position = int(ratio * len(content))
        start = max(0, source_position - 160)
        fragment = content[start : start + max_length + 200]

    excerpt = clean_excerpt(fragment)
    if len(excerpt) <= max_length:
        return excerpt

    shortened = excerpt[:max_length].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{shortened}…"


def score_content(file_path: Path, content: str, title: str, keywords: list[str]) -> int:
    normalized_name = normalize_text(file_path.stem)
    normalized_title = normalize_text(title)
    normalized_content = normalize_text(content)
    score = 0

    for keyword in keywords:
        if keyword in normalized_name:
            score += 8
        if keyword in normalized_title:
            score += 6
        score += min(normalized_content.count(keyword), 5)

    if keywords and all(keyword in f"{normalized_name} {normalized_title}" for keyword in keywords):
        score += 6

    return score


def search_local_content(
    course: str,
    subject: str,
    question: str,
    limit: int = 3,
) -> list[dict]:
    course_folder = course_to_folder(course)
    subject_folder = subject_to_folder(subject)
    keywords = question_keywords(question)

    if not course_folder or not subject_folder or not keywords:
        return []

    search_folder = CONTENT_ROOT / course_folder / subject_folder
    if not search_folder.is_dir():
        return []

    results = []
    for file_path in sorted(search_folder.rglob("*.md")):
        try:
            raw_content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue

        content = strip_front_matter(raw_content)
        title = extract_title(content, file_path.stem)
        score = score_content(file_path, content, title, keywords)
        if score <= 0:
            continue

        try:
            relative_path = file_path.relative_to(CONTENT_ROOT).as_posix()
        except ValueError:
            continue

        results.append(
            {
                "title": title,
                "path": relative_path,
                "score": score,
                "excerpt": make_excerpt(content, keywords),
            }
        )

    results.sort(key=lambda item: (-item["score"], item["path"]))
    return results[: max(0, min(limit, 3))]
