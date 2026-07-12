try:
    from .text_utils import normalize_text
except ImportError:
    from text_utils import normalize_text


COURSE_ALIASES = {
    "primero_basico": ("1 basico", "1o basico", "primero basico", "primero_basico", "1° básico"),
    "segundo_basico": ("2 basico", "2o basico", "segundo basico", "segundo_basico", "2° básico"),
    "tercero_basico": ("3 basico", "3o basico", "tercero basico", "tercero_basico", "3° básico"),
    "cuarto_basico": ("4 basico", "4o basico", "cuarto basico", "cuarto_basico", "4° básico"),
    "quinto_basico": ("5 basico", "5o basico", "quinto basico", "quinto_basico", "5° básico"),
    "sexto_basico": ("6 basico", "6o basico", "sexto basico", "sexto_basico", "6° básico"),
    "septimo_basico": ("7 basico", "7o basico", "septimo basico", "septimo_basico", "7° básico"),
    "octavo_basico": ("8 basico", "8o basico", "octavo basico", "octavo_basico", "8° básico"),
}

COURSE_LABELS = {
    "primero_basico": "1° básico",
    "segundo_basico": "2° básico",
    "tercero_basico": "3° básico",
    "cuarto_basico": "4° básico",
    "quinto_basico": "5° básico",
    "sexto_basico": "6° básico",
    "septimo_basico": "7° básico",
    "octavo_basico": "8° básico",
}

COURSE_FOLDERS = {
    normalize_text(alias): folder
    for folder, aliases in COURSE_ALIASES.items()
    for alias in aliases
}

ALL_COURSES_LABEL = "Todos los cursos"
ALL_COURSES_ALIASES = {
    "all",
    "todos",
    "todos los cursos",
    "toda la base",
    "base completa",
}

PROFILE_COURSES = (
    "1° básico",
    "2° básico",
    "3° básico",
    "4° básico",
    "5° básico",
    "6° básico",
    "7° básico",
    "8° básico",
)

STUDY_COURSES = (*PROFILE_COURSES, ALL_COURSES_LABEL)

SUBJECT_ALIASES = {
    "lenguaje": ("lenguaje", "lenguaje y comunicacion"),
    "matematica": ("matematica", "matemática"),
    "ciencias_naturales": ("ciencias naturales", "ciencias_naturales"),
    "historia_geografia": (
        "historia",
        "historia geografia",
        "historia geografia y ciencias sociales",
        "historia, geografía y ciencias sociales",
        "historia_geografia",
    ),
    "modo_explorador": ("modo explorador", "explorador", "modo_explorador"),
}

SUBJECT_FOLDERS = {
    normalize_text(alias): folder
    for folder, aliases in SUBJECT_ALIASES.items()
    for alias in aliases
}


def course_to_folder(course: str) -> str | None:
    return COURSE_FOLDERS.get(normalize_text(course))


def folder_to_course_label(folder: str) -> str:
    return COURSE_LABELS.get(folder, folder.replace("_", " ").title())


def is_all_courses(course: str | None) -> bool:
    return normalize_text(course or "") in ALL_COURSES_ALIASES


def subject_to_folder(subject: str) -> str | None:
    return SUBJECT_FOLDERS.get(normalize_text(subject))


def is_explorer_mode(mode: str | None) -> bool:
    return "explor" in normalize_text(mode or "")
