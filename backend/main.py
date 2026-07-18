import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .ai_contract import build_educational_context
except ImportError:
    from ai_contract import build_educational_context

try:
    from .content_reader import (
        detect_subject_from_question,
        normalize_question,
        reload_local_content_index,
        retrieve_local_content,
    )
except ImportError:
    from content_reader import (
        detect_subject_from_question,
        normalize_question,
        reload_local_content_index,
        retrieve_local_content,
    )

try:
    from .conversation_context import build_conversation_context
except ImportError:
    from conversation_context import build_conversation_context

try:
    from .demo_tutor import (
        build_grounded_history_answer,
        build_grounded_math_answer,
        build_grounded_science_answer,
        build_contextual_followup,
        build_local_content_fallback,
        detect_topic,
        make_demo_answer,
    )
except ImportError:
    from demo_tutor import (
        build_grounded_history_answer,
        build_grounded_math_answer,
        build_grounded_science_answer,
        build_contextual_followup,
        build_local_content_fallback,
        detect_topic,
        make_demo_answer,
    )

try:
    from .educational_config import ALL_COURSES_LABEL, PROFILE_COURSES, is_all_courses
except ImportError:
    from educational_config import ALL_COURSES_LABEL, PROFILE_COURSES, is_all_courses

try:
    from .response_states import (
        CLARIFICATION_REQUIRED,
        DEMO_FALLBACK,
        GENERATION_BLOCKED_UNVERIFIED,
        LOCAL_CONTENT_FALLBACK,
        LOCAL_VERIFIED,
        OLLAMA_UNVERIFIED,
        OLLAMA_WITH_LOCAL_CONTENT,
        PROVIDER_OLLAMA,
        PROVIDER_OLLAMA_WITH_LOCAL_CONTENT,
        PROVIDER_LOCAL_CONTENT,
        PROVIDER_LOCAL_SAFE,
        uses_verified_local_content,
    )
except ImportError:
    from response_states import (
        CLARIFICATION_REQUIRED,
        DEMO_FALLBACK,
        GENERATION_BLOCKED_UNVERIFIED,
        LOCAL_CONTENT_FALLBACK,
        LOCAL_VERIFIED,
        OLLAMA_UNVERIFIED,
        OLLAMA_WITH_LOCAL_CONTENT,
        PROVIDER_OLLAMA,
        PROVIDER_OLLAMA_WITH_LOCAL_CONTENT,
        PROVIDER_LOCAL_CONTENT,
        PROVIDER_LOCAL_SAFE,
        uses_verified_local_content,
    )

try:
    from .ollama_client import (
        OllamaError,
        OllamaModelNotFoundError,
        OllamaTimeoutError,
        OllamaUnavailableError,
        generate as generate_with_ollama,
        get_status as get_ollama_status,
        start_managed_server,
        stop_managed_server,
        unload_model,
    )
    from .prompt_builder import (
        build_ollama_prompt,
        clean_ollama_response,
        is_source_insufficient_response,
    )
except ImportError:
    from ollama_client import (
        OllamaError,
        OllamaModelNotFoundError,
        OllamaTimeoutError,
        OllamaUnavailableError,
        generate as generate_with_ollama,
        get_status as get_ollama_status,
        start_managed_server,
        stop_managed_server,
        unload_model,
    )
    from prompt_builder import (
        build_ollama_prompt,
        clean_ollama_response,
        is_source_insufficient_response,
    )

try:
    from .text_utils import normalize_text
except ImportError:
    from text_utils import normalize_text

DB_PATH = Path(__file__).with_name("chat_escolar.db")
VIDEOS_PATH = Path(__file__).with_name("data") / "videos_curados.json"
SETTINGS_PATH = Path(__file__).with_name("data") / "settings.json"
AVATAR_DIRECTORY = Path(__file__).with_name("data") / "profile_avatars"
MAX_AVATAR_SIZE_BYTES = 2 * 1024 * 1024
AVATAR_CONTENT_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}
AVATAR_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_ollama_status_cache: dict | None = None
_ollama_status_checked_at: datetime | None = None
_ollama_last_test: dict = {
    "status": "not_tested",
    "model": None,
    "duration_ms": None,
    "error_code": None,
    "error_message": None,
}
_ollama_lifecycle: dict = {"status": "not_checked", "started_by_chat_escolar": False}
logger = logging.getLogger(__name__)
AI_MODES = {"basic", "automatic", "explore_only"}
AUTO_SUBJECT_VALUES = {"automatic", "automatica", "auto", ""}
CURRICULAR_SUBJECTS = ("Ciencias Naturales", "Matemática", "Lenguaje", "Historia")
DEFAULT_SETTINGS = {
    "ai_mode": "basic",
    "ollama_enabled": False,
    "ollama_model": "qwen3.5:2b",
    "ollama_timeout_seconds": 90,
}

app = FastAPI(
    title="Chat Escolar API",
    description="Backend local del proyecto educativo Chat Escolar",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatDemoRequest(BaseModel):
    course: str
    mode: str
    subject: str | None = "Automática"
    question: str
    profile_id: int | None = None
    user_name: str | None = None
    user_role: str | None = None
    conversation_id: str | None = Field(default=None, max_length=120)


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    role: str
    course: str


class AiTestRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=6000)


class QuickActionRequest(BaseModel):
    action: str
    course: str
    subject: str | None = "Automática"
    mode: str = "Estudiar para el colegio"
    last_user_question: str | None = None
    profile_id: int | None = None
    user_name: str | None = None
    user_role: str | None = None


class SettingsUpdate(BaseModel):
    ai_mode: str | None = None
    ollama_enabled: bool | None = None
    ollama_model: str | None = Field(default=None, max_length=80)
    ollama_timeout_seconds: int | None = None


class HistoryStatusUpdate(BaseModel):
    status: str


class HistoryFavoriteUpdate(BaseModel):
    is_favorite: bool | None = None


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    AVATAR_DIRECTORY.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding="utf-8")
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course TEXT NOT NULL,
                mode TEXT NOT NULL,
                subject TEXT,
                topic TEXT,
                question TEXT NOT NULL,
                answer_summary TEXT,
                answer_full TEXT,
                status TEXT NOT NULL DEFAULT 'pendiente',
                is_favorite INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                course TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_used_at TEXT NOT NULL
            )
            """
        )

        history_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(chat_history)").fetchall()
        }
        missing_columns = {
            "profile_id": "INTEGER REFERENCES profiles(id)",
            "conversation_id": "TEXT",
            "normalized_question": "TEXT",
            "contextual_question": "TEXT",
            "active_topic": "TEXT",
            "context_confidence": "REAL",
            "provider": "TEXT NOT NULL DEFAULT 'demo'",
            "provenance_status": "TEXT",
            "content_sources": "TEXT",
        }
        for column, definition in missing_columns.items():
            if column not in history_columns:
                connection.execute(f"ALTER TABLE chat_history ADD COLUMN {column} {definition}")

        profile_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(profiles)").fetchall()
        }
        if "avatar_filename" not in profile_columns:
            connection.execute("ALTER TABLE profiles ADD COLUMN avatar_filename TEXT")


def row_to_history_item(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["is_favorite"] = bool(item["is_favorite"])
    return item


def load_curated_videos() -> list[dict]:
    try:
        with VIDEOS_PATH.open(encoding="utf-8") as videos_file:
            videos = json.load(videos_file)
    except (OSError, json.JSONDecodeError, UnicodeError):
        return []

    return videos if isinstance(videos, list) else []


def validate_settings(candidate: dict) -> dict:
    settings = {**DEFAULT_SETTINGS, **candidate}
    if settings["ai_mode"] not in AI_MODES:
        raise HTTPException(status_code=400, detail="Modo de IA local inválido")
    if not isinstance(settings["ollama_enabled"], bool):
        raise HTTPException(status_code=400, detail="ollama_enabled debe ser verdadero o falso")
    if not isinstance(settings["ollama_model"], str) or not settings["ollama_model"].strip():
        raise HTTPException(status_code=400, detail="El modelo de Ollama es obligatorio")
    if not isinstance(settings["ollama_timeout_seconds"], int) or not 5 <= settings["ollama_timeout_seconds"] <= 120:
        raise HTTPException(status_code=400, detail="El timeout debe estar entre 5 y 120 segundos")
    settings["ollama_model"] = settings["ollama_model"].strip()
    return settings


def load_settings() -> dict:
    try:
        with SETTINGS_PATH.open(encoding="utf-8") as settings_file:
            saved_settings = json.load(settings_file)
        if not isinstance(saved_settings, dict):
            raise ValueError("La configuración no es un objeto")
        return validate_settings(saved_settings)
    except (OSError, ValueError, json.JSONDecodeError, HTTPException):
        # A corrupt local preference must not prevent the educational fallback.
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> dict:
    validated = validate_settings(settings)
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = SETTINGS_PATH.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(validated, indent=2), encoding="utf-8")
    temporary_path.replace(SETTINGS_PATH)
    return validated


def get_cached_ollama_status(settings: dict | None = None) -> dict:
    global _ollama_status_cache, _ollama_status_checked_at
    now = datetime.now(timezone.utc)
    if _ollama_status_cache is not None and _ollama_status_checked_at is not None:
        if (now - _ollama_status_checked_at).total_seconds() < 10:
            return _ollama_status_cache
    settings = settings or load_settings()
    _ollama_status_cache = get_ollama_status(
        model=settings["ollama_model"],
        enabled=settings["ollama_enabled"],
        timeout_seconds=settings["ollama_timeout_seconds"],
    )
    _ollama_status_checked_at = now
    return _ollama_status_cache


def ollama_error_code(error: OllamaError) -> str:
    if isinstance(error, OllamaTimeoutError):
        return "ollama_timeout"
    if isinstance(error, OllamaModelNotFoundError):
        return "model_not_installed"
    if isinstance(error, OllamaUnavailableError):
        return "ollama_unreachable"
    return "generation_error"


def add_ollama_fallback_notice(
    demo_answer: dict,
    *,
    error_code: str,
    subject: str | None,
    has_verified_source: bool,
    model: str,
) -> dict:
    messages = []
    if not has_verified_source:
        if subject:
            messages.append(f"Detecté que tu pregunta es de {subject}.")
        messages.append("No encontré una fuente curricular local exacta.")

    if error_code == "ollama_timeout":
        messages.append(
            "La IA local excedió el tiempo máximo configurado. Se utilizó el modo básico."
        )
    elif error_code == "model_not_installed":
        messages.append(
            f"El modelo local {model} no está instalado. Se utilizó el modo básico."
        )
    elif error_code == "ollama_unreachable":
        messages.append(
            "El servidor local de Ollama está inaccesible. Se utilizó el modo básico."
        )
    else:
        messages.append(
            "La IA local no pudo completar la generación. Se utilizó el modo básico."
        )

    return {
        **demo_answer,
        "answer": f"{' '.join(messages)}\n\n{demo_answer['answer']}",
    }


def build_unverified_source_blocked_answer(subject: str | None) -> dict:
    detected = subject or "un tema escolar"
    answer = (
        f"Detecté que tu pregunta es de {detected}, pero todavía no tengo una "
        "fuente curricular local verificada sobre este tema. Para evitar darte "
        "información incorrecta, no generaré una explicación como si estuviera confirmada.\n\n"
        "Puedes consultar este tema en Modo Explorar o incorporarlo a los contenidos locales."
    )
    return {
        "answer": answer,
        "summary": "La generación factual se bloqueó porque no existe una fuente local verificada.",
        "status": "ok",
    }


def add_insufficient_source_notice(demo_answer: dict) -> dict:
    return {
        **demo_answer,
        "answer": (
            "No tengo suficiente información local verificada para explicar este tema con "
            "seguridad. Se muestra únicamente el contenido local disponible.\n\n"
            f"{demo_answer['answer']}"
        ),
    }


IQUIQUE_TOPIC_MARKERS = (
    "combate naval de iquique",
    "combate naval",
    "arturo prat",
    "21 de mayo",
    "esmeralda",
    "huascar",
    "miguel grau",
)


@app.on_event("startup")
def start_local_ai() -> None:
    """Prepare the local index before serving requests, then manage local AI."""
    global _ollama_lifecycle
    index_started_at = perf_counter()
    try:
        indexed_documents = reload_local_content_index()
        logger.info(
            "Índice local preparado: %s documentos en %d ms.",
            indexed_documents,
            round((perf_counter() - index_started_at) * 1000),
        )
    except Exception:
        # El índice también conserva carga diferida; no bloquear el backend si un
        # archivo local tiene un problema inesperado.
        logger.exception("No se pudo precalentar el índice de contenido local.")
    settings = load_settings()
    if settings["ollama_enabled"]:
        _ollama_lifecycle = start_managed_server()
    else:
        _ollama_lifecycle = {"status": "ollama_disabled", "started_by_chat_escolar": False}


@app.on_event("shutdown")
def stop_local_ai() -> None:
    settings = load_settings()
    unloaded = unload_model(model=settings["ollama_model"])
    stopped = stop_managed_server()
    _ollama_lifecycle.update({"model_unloaded": unloaded, "server_stopped": stopped})
IQUIQUE_HALLUCINATION_TERMS = (
    "juan manuel balmaceda",
    "monarca",
    "invasion de chile",
    "invadir chile",
    "bandera de victoria",
    "espanoles",
    "segunda guerra mundial",
    "alemania",
    "italia",
    "japon",
    "piratas",
    "oro",
    "misiles",
    "1942",
    "siglo xviii",
    "convoy",
    "barcos italianos",
    "navieros britanicos",
    "murieron ambos comandantes",
    "ambos comandantes murieron",
    "corbeta chilena arturo prat",
    "arturo prat se vencio",
    "bernardo ohiggins",
    "bernardo o higgins",
    "barco chilena",
    "los chilenos fueron derrotados",
    "murio por los golpes",
    "destruyeron y hundir al navio enemigo",
    "el capitan peruano murio",
)


def has_iquique_historical_hallucination(question: str, answer: str) -> bool:
    normalized_question = normalize_text(question)
    if not any(marker in normalized_question for marker in IQUIQUE_TOPIC_MARKERS):
        return False
    answer_terms = f" {normalize_text(answer).replace(chr(39), '')} "
    return any(f" {term} " in answer_terms for term in IQUIQUE_HALLUCINATION_TERMS)


def is_grounded_iquique_source(local_content: dict | None) -> bool:
    return bool(
        local_content
        and "combate naval de iquique" in normalize_text(local_content.get("title", ""))
    )


def is_history_subject(subject: str | None) -> bool:
    """Identifica Historia, incluso cuando el contenido usa su nombre curricular largo."""
    normalized = normalize_text(subject or "")
    return normalized == "historia" or normalized.startswith("historia geografia")


def should_use_grounded_history_answer(
    *,
    grounding_required: bool,
    has_verified_source: bool,
    subject_used: str | None,
    local_content: dict | None,
) -> bool:
    """En Escolar, Historia verificada se responde solo desde la fuente local."""
    return bool(
        grounding_required
        and has_verified_source
        and (
            is_history_subject(subject_used)
            or is_history_subject((local_content or {}).get("subject"))
        )
    )


def should_use_grounded_math_answer(
    *, grounding_required: bool, has_verified_source: bool, subject_used: str | None,
    local_content: dict | None,
) -> bool:
    subject = normalize_text(subject_used or (local_content or {}).get("subject", ""))
    return grounding_required and has_verified_source and "matematica" in subject


def should_use_grounded_science_answer(
    *, grounding_required: bool, has_verified_source: bool, subject_used: str | None,
    local_content: dict | None,
) -> bool:
    """Ciencias verificadas se presentan desde la fuente, sin redacción libre de IA."""
    subject = normalize_text(subject_used or (local_content or {}).get("subject", ""))
    return grounding_required and has_verified_source and any(
        term in subject for term in ("ciencias", "fisica", "quimica", "biologia", "astronomia")
    )


def add_grounding_validation_notice(demo_answer: dict) -> dict:
    return {
        **demo_answer,
        "answer": (
            "La respuesta de IA no se mostró porque incluía información ajena a la fuente "
            "local. Se muestra únicamente el contenido local verificado.\n\n"
            f"{demo_answer['answer']}"
        ),
    }


def status_with_ai_test(status: dict, settings: dict) -> dict:
    last_test = _ollama_last_test.copy()
    ready = bool(
        status.get("server_reachable", status.get("available"))
        and status.get("model_installed")
        and last_test.get("status") == "ollama_success"
        and last_test.get("model") == settings["ollama_model"]
    )
    return {
        **status,
        "server_reachable": status.get("server_reachable", status.get("available", False)),
        "configured_model": settings["ollama_model"],
        "ready": ready,
        "last_test_status": last_test["status"],
        "last_test_duration_ms": last_test["duration_ms"],
        "last_error_code": last_test["error_code"],
        "last_error_message": last_test["error_message"],
    }


def is_automatic_subject(subject: str | None) -> bool:
    return normalize_text(subject or "") in AUTO_SUBJECT_VALUES


def select_best_retrieval(retrievals: list[tuple[str, dict]]) -> tuple[str, dict]:
    priority = {
        LOCAL_VERIFIED: 4,
        "local_related": 3,
        "local_low_confidence": 2,
        "no_local_content": 1,
        CLARIFICATION_REQUIRED: 0,
    }
    return max(
        retrievals,
        key=lambda item: (priority.get(item[1]["provenance_status"], 0), item[1].get("best_score", 0)),
    )


def retrieve_automatic_subject(course: str, question: str, mode: str, detected_subject: str | None) -> tuple[str | None, dict, bool]:
    """Preserve a detected subject even when its local collection has no match."""
    candidates: list[tuple[str, dict]] = []
    if detected_subject:
        initial = retrieve_local_content(course, detected_subject, question, mode=mode)
        return detected_subject, initial, False

    for subject in CURRICULAR_SUBJECTS:
        if subject == detected_subject:
            continue
        candidates.append((subject, retrieve_local_content(course, subject, question, mode=mode)))
    subject_used, selected = select_best_retrieval(candidates)
    return subject_used, selected, subject_used != detected_subject


def save_history(
    payload: ChatDemoRequest,
    demo_answer: dict[str, str],
    conversation_context: dict | None = None,
    provider: str = "demo",
    provenance_status: str | None = None,
    content_sources: list[dict] | None = None,
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    conversation_context = conversation_context or {}

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO chat_history (
                course,
                mode,
                subject,
                topic,
                question,
                answer_summary,
                answer_full,
                status,
                is_favorite,
                created_at,
                profile_id,
                conversation_id,
                normalized_question,
                contextual_question,
                active_topic,
                context_confidence,
                provider,
                provenance_status,
                content_sources
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pendiente', 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.course,
                payload.mode,
                payload.subject,
                conversation_context.get("active_topic") or detect_topic(payload.question),
                payload.question,
                demo_answer["summary"],
                demo_answer["answer"],
                created_at,
                payload.profile_id,
                payload.conversation_id,
                conversation_context.get("normalized_question"),
                conversation_context.get("contextual_question"),
                conversation_context.get("active_topic"),
                conversation_context.get("confidence"),
                provider,
                provenance_status,
                json.dumps(content_sources or [], ensure_ascii=False),
            ),
        )
        return cursor.lastrowid


def get_recent_conversation_items(profile_id: int | None, conversation_id: str | None) -> list[dict]:
    if profile_id is None or not conversation_id:
        return []

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT question, subject, normalized_question, contextual_question, active_topic,
                   context_confidence, created_at
            FROM chat_history
            WHERE profile_id = ? AND conversation_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 6
            """,
            (profile_id, conversation_id),
        ).fetchall()

    return [dict(row) for row in rows]


def get_history_item(history_id: int) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM chat_history WHERE id = ?",
            (history_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Historial no encontrado")

    return row_to_history_item(row)


init_db()


def get_profile_or_404(profile_id: int) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    return profile_to_response(row)


def profile_to_response(row: sqlite3.Row | dict) -> dict:
    profile = dict(row)
    avatar_filename = profile.pop("avatar_filename", None)
    profile["avatar_url"] = f"/profiles/{profile['id']}/avatar" if avatar_filename else None
    return profile


def avatar_path(avatar_filename: str | None) -> Path | None:
    if not avatar_filename:
        return None
    filename = Path(avatar_filename).name
    if filename != avatar_filename or Path(filename).suffix.lower() not in AVATAR_EXTENSIONS:
        return None
    return AVATAR_DIRECTORY / filename


def delete_avatar_file(avatar_filename: str | None) -> None:
    path = avatar_path(avatar_filename)
    if path is not None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            logger.warning("No se pudo eliminar el avatar local %s", path.name)


def has_expected_avatar_signature(content: bytes, content_type: str) -> bool:
    signatures = {
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/webp": len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP",
    }
    return signatures.get(content_type, False)


@app.get("/")
def home():
    return {
        "message": "Chat Escolar API funcionando",
        "project": "Chat Escolar",
        "author": "Ariel Ponce",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "chat-escolar-backend",
    }


@app.get("/ai/status")
def ai_status():
    settings = load_settings()
    status = get_cached_ollama_status(settings)
    return {
        **status_with_ai_test(status, settings),
        "ai_mode": settings["ai_mode"],
        "ollama_enabled": settings["ollama_enabled"],
        "ollama_timeout_seconds": settings["ollama_timeout_seconds"],
        "lifecycle": _ollama_lifecycle,
    }


@app.post("/ai/shutdown")
def ai_shutdown():
    """Clean shutdown for launch scripts and the application window."""
    settings = load_settings()
    unloaded = unload_model(model=settings["ollama_model"])
    stopped = stop_managed_server()
    _ollama_lifecycle.update({
        "status": "model_unloaded" if unloaded else _ollama_lifecycle.get("status", "not_checked"),
        "model_unloaded": unloaded,
        "server_stopped": stopped,
    })
    return {"status": "ok", "model_unloaded": unloaded, "server_stopped": stopped,
            "started_by_chat_escolar": _ollama_lifecycle.get("started_by_chat_escolar", False)}


@app.get("/settings")
def get_settings():
    return {"status": "ok", "settings": load_settings()}


@app.patch("/settings")
def update_settings(payload: SettingsUpdate):
    global _ollama_status_cache, _ollama_status_checked_at
    updates = (
        payload.model_dump(exclude_none=True)
        if hasattr(payload, "model_dump")
        else payload.dict(exclude_none=True)
    )
    settings = save_settings({**load_settings(), **updates})
    _ollama_status_cache = None
    _ollama_status_checked_at = None
    return {"status": "ok", "settings": settings}


def run_ai_test(prompt: str = "Responde únicamente: OK") -> dict:
    global _ollama_last_test
    settings = load_settings()
    if settings["ai_mode"] == "basic" or not settings["ollama_enabled"]:
        message = "Activa la IA local para probar Ollama."
        _ollama_last_test = {"status": "ollama_disabled", "model": settings["ollama_model"], "duration_ms": None, "error_code": "ollama_disabled", "error_message": message}
        return {"status": "ollama_disabled", "provider": "demo", "message": message, "answer": None}

    status = get_cached_ollama_status(settings)
    if not status["available"] or not status["model_installed"]:
        code = status.get("status")
        if code not in {
            "ollama_timeout",
            "ollama_unreachable",
            "model_not_installed",
            "generation_error",
        }:
            code = "model_not_installed" if status.get("available") else "ollama_unreachable"
        message = (
            "La comprobación de Ollama excedió el tiempo máximo configurado."
            if code == "ollama_timeout"
            else f"El modelo {settings['ollama_model']} no está instalado."
            if code == "model_not_installed"
            else "La IA local no pudo completar la prueba."
            if code == "generation_error"
            else "No se pudo conectar con Ollama."
        )
        _ollama_last_test = {
            "status": code,
            "model": settings["ollama_model"],
            "duration_ms": None,
            "error_code": code,
            "error_message": message,
        }
        return {"status": code, "provider": "demo", "message": message, "answer": None}

    started_at = perf_counter()
    try:
        answer = clean_ollama_response(generate_with_ollama(
            prompt,
            model=settings["ollama_model"],
            enabled=settings["ollama_enabled"],
            timeout_seconds=settings["ollama_timeout_seconds"],
        ))
    except OllamaError as error:
        code = ollama_error_code(error)
        message = (
            f"La IA local excedió el tiempo máximo de {settings['ollama_timeout_seconds']} s."
            if code == "ollama_timeout"
            else f"El modelo {settings['ollama_model']} no está instalado."
            if code == "model_not_installed"
            else "No se pudo conectar con Ollama."
            if code == "ollama_unreachable"
            else "La IA local no pudo completar la prueba."
        )
        duration_ms = round((perf_counter() - started_at) * 1000)
        _ollama_last_test = {"status": code, "model": settings["ollama_model"], "duration_ms": duration_ms, "error_code": code, "error_message": message}
        return {"status": code, "provider": "demo", "message": message, "answer": None, "duration_ms": duration_ms}

    duration_ms = round((perf_counter() - started_at) * 1000)
    _ollama_last_test = {"status": "ollama_success", "model": settings["ollama_model"], "duration_ms": duration_ms, "error_code": None, "error_message": None}
    return {"status": "ollama_success", "provider": PROVIDER_OLLAMA, "answer": answer, "duration_ms": duration_ms}


@app.post("/ai/test")
def ai_test(payload: AiTestRequest):
    return run_ai_test(payload.prompt)


@app.post("/chat/quick-action")
def chat_quick_action(payload: QuickActionRequest):
    action_map = {"No entendí": "explain_again", "Explícalo más fácil": "simplify", "Dame un ejemplo": "give_example", "Hazme una pregunta": "ask_question"}
    question = (payload.last_user_question or "").strip()
    if payload.profile_id is not None:
        profile = get_profile_or_404(payload.profile_id)
        payload.user_name, payload.user_role = profile["name"], profile["role"]
    if not question:
        response = build_contextual_followup(payload, "explain_again", None)
        return {
            **response, "subject_used": "General", "category": "Sin categoría",
            "source_title": "Sin fuente local", "source_course": "Sin curso específico declarado",
            "content_sources": [], "related_sources": [], "provenance_status": "safe_fallback",
            "used_local_content": False, "used_ollama": False, "metadata": {}, "provider": "demo",
        }
    subject = payload.subject
    if is_automatic_subject(subject):
        subject, _ = detect_subject_from_question(question)
        subject = subject or "Ciencias Naturales"
    payload.subject = subject
    retrieval = retrieve_local_content(payload.course, subject, question, mode=payload.mode)
    source = retrieval["results"][0] if retrieval.get("results") else None
    response = build_contextual_followup(payload, action_map.get(payload.action, "explain_again"), source)
    source = source or {}
    return {
        **response,
        "subject_used": subject or "General",
        "category": (
            source.get("metadata", {}).get("display_category")
            or source.get("metadata", {}).get("category")
            or "Sin categoría"
        ),
        "source_title": source.get("title") or "Sin fuente local",
        "source_course": source.get("course") or "Sin curso específico declarado",
        "content_sources": [{"title": source.get("title") or "Fuente local", "path": source.get("path"), "course": source.get("course"), "subject": source.get("subject")} ] if source else [],
        "related_sources": [],
        "provenance_status": LOCAL_CONTENT_FALLBACK if source else "safe_fallback",
        "used_local_content": bool(source),
        "used_ollama": False,
        "metadata": source.get("metadata", {}),
        "provider": PROVIDER_LOCAL_CONTENT if source else "demo",
    }


@app.get("/videos")
def list_videos(
    topic: str | None = None,
    mode: str | None = None,
    subject: str | None = None,
):
    videos = load_curated_videos()
    filters = {"topic": topic, "mode": mode, "subject": subject}

    for field, value in filters.items():
        if value:
            normalized_value = normalize_text(value.strip())
            videos = [
                video
                for video in videos
                if normalized_value in normalize_text(str(video.get(field, "")))
            ]

    return videos


@app.get("/content/search")
def search_content(
    course: str,
    q: str,
    subject: str = "Automática",
    mode: str = "Estudiar para el colegio",
):
    detected_subject, subject_confidence = detect_subject_from_question(q)
    if is_automatic_subject(subject):
        subject_used, result, fallback_used = retrieve_automatic_subject(
            course, q, mode, detected_subject
        )
        subject_mode = "automatic"
    else:
        subject_used = subject
        fallback_used = False
        result = retrieve_local_content(course, subject, q, mode=mode)
        subject_mode = "manual"
    return {
        "status": "ok",
        **result,
        "detected_subject": detected_subject,
        "subject_used": subject_used,
        "subject_mode": subject_mode,
        "subject_confidence": subject_confidence,
        "subject_fallback_used": fallback_used,
    }


@app.post("/profiles", status_code=201)
def create_profile(payload: ProfileCreate):
    valid_roles = {"Estudiante", "Apoderado", "Docente"}
    valid_courses = set(PROFILE_COURSES)
    name = payload.name.strip()

    if not name:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    if payload.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Tipo de usuario inválido")
    if payload.course not in valid_courses:
        raise HTTPException(status_code=400, detail="Curso inválido")

    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO profiles (name, role, course, created_at, last_used_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, payload.role, payload.course, now, now),
        )
        profile_id = cursor.lastrowid

    return {"status": "ok", "profile": get_profile_or_404(profile_id)}


@app.get("/profiles")
def list_profiles():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM profiles ORDER BY last_used_at DESC, id DESC"
        ).fetchall()

    return {"status": "ok", "items": [profile_to_response(row) for row in rows]}


@app.get("/profiles/{profile_id}")
def get_profile(profile_id: int):
    return {"status": "ok", "profile": get_profile_or_404(profile_id)}


@app.patch("/profiles/{profile_id}/last-used")
def update_profile_last_used(profile_id: int):
    get_profile_or_404(profile_id)
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        connection.execute(
            "UPDATE profiles SET last_used_at = ? WHERE id = ?", (now, profile_id)
        )

    return {"status": "ok", "profile": get_profile_or_404(profile_id)}


@app.post("/profiles/{profile_id}/avatar")
async def upload_profile_avatar(profile_id: int, request: Request):
    """Store an avatar received as a raw local image body.

    Raw bytes are intentionally used instead of multipart so the project remains
    dependency-free when python-multipart is not installed.
    """
    get_profile_or_404(profile_id)
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    filename = request.headers.get("x-avatar-filename", "")
    extension = Path(filename).suffix.lower()

    if content_type not in AVATAR_CONTENT_TYPES or extension not in AVATAR_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="El avatar debe ser una imagen PNG, JPG, JPEG o WEBP",
        )

    content = await request.body()
    if not content:
        raise HTTPException(status_code=400, detail="Selecciona una imagen para el avatar")
    if len(content) > MAX_AVATAR_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="El avatar no puede superar los 2 MB")
    if not has_expected_avatar_signature(content, content_type):
        raise HTTPException(status_code=415, detail="El archivo no coincide con el formato de imagen indicado")

    # The generated name is based only on the stable internal id, never on a
    # browser-provided path or filename.
    safe_extension = AVATAR_CONTENT_TYPES[content_type]
    avatar_filename = f"profile_{profile_id}{safe_extension}"
    destination = AVATAR_DIRECTORY / avatar_filename
    temporary_destination = AVATAR_DIRECTORY / f".{avatar_filename}.tmp"
    AVATAR_DIRECTORY.mkdir(parents=True, exist_ok=True)
    try:
        temporary_destination.write_bytes(content)
        temporary_destination.replace(destination)
    except OSError as error:
        temporary_destination.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="No pude guardar el avatar local") from error

    with get_connection() as connection:
        existing_avatar = connection.execute(
            "SELECT avatar_filename FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()
        connection.execute(
            "UPDATE profiles SET avatar_filename = ? WHERE id = ?",
            (avatar_filename, profile_id),
        )
    old_avatar_filename = existing_avatar["avatar_filename"] if existing_avatar else None
    if old_avatar_filename and old_avatar_filename != avatar_filename:
        delete_avatar_file(old_avatar_filename)

    return {"status": "ok", "profile": get_profile_or_404(profile_id)}


@app.get("/profiles/{profile_id}/avatar")
def get_profile_avatar(profile_id: int):
    get_profile_or_404(profile_id)
    # Read the internal filename directly, since the public profile response
    # deliberately exposes only a relative endpoint URL.
    with get_connection() as connection:
        row = connection.execute(
            "SELECT avatar_filename FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()
    avatar_file = avatar_path(row["avatar_filename"] if row else None)
    if avatar_file is None or not avatar_file.is_file():
        raise HTTPException(status_code=404, detail="Este perfil no tiene avatar")

    suffix = avatar_file.suffix.lower()
    media_type = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}[suffix]
    return Response(
        content=avatar_file.read_bytes(),
        media_type=media_type,
        headers={"Cache-Control": "no-store"},
    )


@app.delete("/profiles/{profile_id}/avatar")
def delete_profile_avatar(profile_id: int):
    get_profile_or_404(profile_id)
    with get_connection() as connection:
        row = connection.execute(
            "SELECT avatar_filename FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()
        if not row or not row["avatar_filename"]:
            raise HTTPException(status_code=404, detail="Este perfil no tiene avatar")
        avatar_filename = row["avatar_filename"]
        connection.execute(
            "UPDATE profiles SET avatar_filename = NULL WHERE id = ?", (profile_id,)
        )
    delete_avatar_file(avatar_filename)
    return {"status": "ok", "profile": get_profile_or_404(profile_id)}


@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int):
    with get_connection() as connection:
        profile = connection.execute(
            "SELECT id, name, avatar_filename FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()
        if profile is None:
            raise HTTPException(status_code=404, detail="Perfil no encontrado")

        deleted_history = connection.execute(
            "DELETE FROM chat_history WHERE profile_id = ?", (profile_id,)
        ).rowcount
        connection.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))

    delete_avatar_file(profile["avatar_filename"])

    return {
        "status": "ok",
        "deleted_profile": {"id": profile["id"], "name": profile["name"]},
        "deleted_history_count": deleted_history,
    }


@app.post("/chat/demo")
def chat_demo(payload: ChatDemoRequest):
    started_at = perf_counter()
    profile_course = None
    if payload.profile_id is not None:
        profile = get_profile_or_404(payload.profile_id)
        payload.user_name = profile["name"]
        payload.user_role = profile["role"]
        profile_course = profile["course"]
        if not (payload.course or "").strip():
            payload.course = profile_course

    if payload.profile_id is not None and not payload.conversation_id:
        payload.conversation_id = f"profile-{payload.profile_id}-default"

    recent_items = get_recent_conversation_items(
        payload.profile_id,
        payload.conversation_id,
    )
    conversation_context = build_conversation_context(payload.question, recent_items)
    subject_mode = "automatic" if is_automatic_subject(payload.subject) else "manual"
    detected_subject, subject_confidence = detect_subject_from_question(
        conversation_context["contextual_question"]
    )
    if subject_mode == "automatic" and detected_subject is None and recent_items:
        previous_subject = recent_items[0].get("subject")
        if previous_subject in CURRICULAR_SUBJECTS:
            detected_subject, subject_confidence = previous_subject, 0.55
    subject_used = payload.subject
    subject_fallback_used = False

    if conversation_context["requires_clarification"]:
        retrieval = {
            "provenance_status": CLARIFICATION_REQUIRED,
            "results": [],
            "related_results": [],
            "query_analysis": conversation_context["query_analysis"],
            "minimum_score": None,
            "best_score": 0,
        }
    else:
        if subject_mode == "automatic":
            subject_used, retrieval, subject_fallback_used = retrieve_automatic_subject(
                payload.course,
                conversation_context["contextual_question"],
                payload.mode,
                detected_subject,
            )
            if subject_used:
                payload.subject = subject_used
        else:
            retrieval = retrieve_local_content(
                payload.course,
                payload.subject,
                conversation_context["contextual_question"],
                mode=payload.mode,
            )
        if (
            retrieval["provenance_status"] != LOCAL_VERIFIED
            and not is_all_courses(payload.course)
            and "explor" not in normalize_text(payload.mode or "")
        ):
            if subject_mode == "automatic":
                global_subject, global_retrieval, global_fallback = retrieve_automatic_subject(
                    ALL_COURSES_LABEL,
                    conversation_context["contextual_question"],
                    payload.mode,
                    detected_subject,
                )
            else:
                global_subject = payload.subject
                global_fallback = False
                global_retrieval = retrieve_local_content(
                    ALL_COURSES_LABEL,
                    payload.subject,
                    conversation_context["contextual_question"],
                    mode=payload.mode,
                )
            if global_retrieval["provenance_status"] == LOCAL_VERIFIED:
                if subject_mode == "automatic" and global_subject:
                    subject_used = global_subject
                    payload.subject = global_subject
                    subject_fallback_used = subject_fallback_used or global_fallback
                retrieval = {
                    **global_retrieval,
                    "effective_course": payload.course,
                    "global_fallback": True,
                    "found_in_other_course": global_retrieval.get("source_course") != payload.course,
                }

    retrieval.setdefault("active_course", payload.course)
    retrieval.setdefault("profile_course", profile_course)

    local_results = retrieval["results"]
    related_results = retrieval.get("related_results", [])
    educational_context = build_educational_context(
        payload,
        retrieval,
        conversation_context,
        profile_course=profile_course,
    )
    demo_answer = make_demo_answer(
        payload,
        local_content=local_results[0] if local_results else None,
        related_content=related_results[0] if related_results else None,
        query_analysis=retrieval["query_analysis"],
        provenance_status=retrieval["provenance_status"],
        source_course=retrieval.get("source_course"),
        found_in_other_course=retrieval.get("found_in_other_course", False),
    )
    content_sources = [
        {
            "title": local_results[0]["title"],
            "path": local_results[0]["path"],
            "course": local_results[0].get("course"),
            "subject": local_results[0].get("subject"),
        }
    ] if local_results else []
    response_provenance = retrieval["provenance_status"]
    provider = educational_context["provider"]
    has_verified_source = retrieval["provenance_status"] == LOCAL_VERIFIED and bool(local_results)
    settings = load_settings()
    ai_mode = settings["ai_mode"]
    is_exploration = "explor" in normalize_text(payload.mode or "")
    grounding_required = not is_exploration
    grounded_history_policy = should_use_grounded_history_answer(
        grounding_required=grounding_required,
        has_verified_source=has_verified_source,
        subject_used=subject_used,
        local_content=local_results[0] if local_results else None,
    )
    grounded_math_policy = should_use_grounded_math_answer(
        grounding_required=grounding_required,
        has_verified_source=has_verified_source,
        subject_used=subject_used,
        local_content=local_results[0] if local_results else None,
    )
    grounded_science_policy = should_use_grounded_science_answer(
        grounding_required=grounding_required,
        has_verified_source=has_verified_source,
        subject_used=subject_used,
        local_content=local_results[0] if local_results else None,
    )
    grounded_source_available = has_verified_source
    answer_grounded = has_verified_source
    source_confidence = "verified" if has_verified_source else retrieval.get("confidence", "none")
    generation_blocked_reason = None
    local_fallback_reason = None
    answer_warning = None
    ai_mode_allows_ollama = (
        ai_mode == "automatic"
        or (ai_mode == "explore_only" and is_exploration)
    )
    ollama_allowed_for_request = (
        not conversation_context["requires_clarification"]
        and ai_mode_allows_ollama
        and (has_verified_source or not grounding_required)
        and not grounded_history_policy
        # En Modo Escolar la fuente local verificada es la respuesta preferida;
        # IA libre solo puede operar sin fuente en Modo Explorar.
        and not (grounding_required and has_verified_source)
    )
    ollama_attempted = False
    ollama_timeout = False

    if (
        grounding_required
        and not has_verified_source
        and not conversation_context["requires_clarification"]
    ):
        demo_answer = build_unverified_source_blocked_answer(
            subject_used or detected_subject
        )
        response_provenance = GENERATION_BLOCKED_UNVERIFIED
        provider = "demo"
        generation_blocked_reason = "no_verified_local_source"

    if settings["ollama_enabled"] and ollama_allowed_for_request:
        ollama_status = get_cached_ollama_status(settings)
    else:
        blocked_status = "generation_blocked" if generation_blocked_reason else None
        ollama_status = {
            "status": blocked_status or (
                "ollama_disabled" if not settings["ollama_enabled"] else "not_attempted"
            ),
            "enabled": False,
            "available": False,
            "model": settings["ollama_model"],
            "model_installed": False,
            "message": (
                "La generación se bloqueó porque no existe una fuente local verificada."
                if generation_blocked_reason
                else "La IA local no se usa con la configuración actual."
            ),
        }
    ollama_result_status = ollama_status.get(
        "status",
        "ready_for_generation"
        if ollama_status["available"] and ollama_status["model_installed"]
        else "ollama_unreachable",
    )
    educational_context["ollama_enabled"] = (
        ollama_status["enabled"]
        and ollama_status["available"]
        and ollama_status["model_installed"]
    )
    educational_context["ollama_available"] = ollama_status["available"]

    if grounded_history_policy:
        # Esta ruta se resuelve antes de toda llamada o comprobacion de Ollama.
        # No aplica el aviso de fuente insuficiente: la fuente ya fue verificada.
        demo_answer = build_grounded_history_answer(payload, local_results[0])
        response_provenance = LOCAL_VERIFIED
        provider = PROVIDER_LOCAL_SAFE
        ollama_result_status = "grounded_local_policy"
        local_fallback_reason = "grounded_history_policy"
    elif grounded_math_policy:
        demo_answer = build_grounded_math_answer(payload, local_results[0])
        response_provenance = LOCAL_VERIFIED
        provider = PROVIDER_LOCAL_SAFE
        ollama_result_status = "grounded_local_policy"
        local_fallback_reason = "grounded_math_policy"
    elif grounded_science_policy:
        demo_answer = build_grounded_science_answer(payload, local_results[0])
        response_provenance = LOCAL_VERIFIED
        provider = PROVIDER_LOCAL_SAFE
        ollama_result_status = "grounded_local_policy"
        local_fallback_reason = "grounded_science_policy"
    elif has_verified_source:
        demo_answer = build_local_content_fallback(payload, local_results[0])
        response_provenance = LOCAL_CONTENT_FALLBACK
        provider = PROVIDER_LOCAL_CONTENT

    if ollama_allowed_for_request:
        if ollama_status["available"] and ollama_status["model_installed"]:
            try:
                ollama_attempted = True
                prompt = build_ollama_prompt(
                    payload,
                    educational_context,
                    use_local_source=has_verified_source,
                )
                answer = clean_ollama_response(generate_with_ollama(
                    prompt,
                    model=settings["ollama_model"],
                    enabled=settings["ollama_enabled"],
                    timeout_seconds=settings["ollama_timeout_seconds"],
                ))
                if not answer:
                    raise OllamaError("Ollama devolvió una respuesta vacía después de la limpieza.")
                if has_verified_source and is_source_insufficient_response(answer):
                    demo_answer = add_insufficient_source_notice(
                        build_local_content_fallback(payload, local_results[0])
                    )
                    response_provenance = LOCAL_CONTENT_FALLBACK
                    provider = PROVIDER_LOCAL_CONTENT
                    ollama_result_status = "source_insufficient"
                    generation_blocked_reason = "verified_source_insufficient"
                    local_fallback_reason = "verified_source_insufficient"
                    answer_grounded = True
                elif has_verified_source and has_iquique_historical_hallucination(
                    conversation_context["contextual_question"], answer
                ):
                    demo_answer = add_grounding_validation_notice(
                        build_local_content_fallback(payload, local_results[0])
                    )
                    response_provenance = LOCAL_CONTENT_FALLBACK
                    provider = PROVIDER_LOCAL_CONTENT
                    ollama_result_status = "grounding_validation_failed"
                    generation_blocked_reason = "historical_hallucination_detected"
                    local_fallback_reason = "historical_hallucination_detected"
                    answer_grounded = True
                else:
                    demo_answer = {
                        "answer": answer,
                        "summary": "Explicación generada con IA local" + (
                            " usando contenido local verificado."
                            if has_verified_source
                            else " en modo exploratorio sin fuente verificada."
                        ),
                        "status": "ok",
                    }
                    if has_verified_source:
                        response_provenance = OLLAMA_WITH_LOCAL_CONTENT
                        provider = PROVIDER_OLLAMA_WITH_LOCAL_CONTENT
                        answer_grounded = True
                    else:
                        response_provenance = OLLAMA_UNVERIFIED
                        provider = PROVIDER_OLLAMA
                        answer_grounded = False
                        answer_warning = (
                            "Respuesta generada con IA local sin fuente verificada. "
                            "Puede contener errores."
                        )
                    ollama_result_status = "ollama_success"
            except OllamaError as error:
                logger.warning("Ollama falló; se usará el fallback local: %s", error)
                ollama_result_status = ollama_error_code(error)
                ollama_timeout = ollama_result_status == "ollama_timeout"
                demo_answer = add_ollama_fallback_notice(
                    demo_answer,
                    error_code=ollama_result_status,
                    subject=subject_used or detected_subject,
                    has_verified_source=has_verified_source,
                    model=settings["ollama_model"],
                )
                response_provenance = LOCAL_CONTENT_FALLBACK if has_verified_source else retrieval["provenance_status"]
                provider = PROVIDER_LOCAL_CONTENT if has_verified_source else "demo"
                if has_verified_source:
                    local_fallback_reason = "ollama_failure"
        else:
            ollama_result_status = (
                "model_not_installed"
                if ollama_status["available"] and not ollama_status["model_installed"]
                else ollama_status.get("status", "ollama_unreachable")
            )
            demo_answer = add_ollama_fallback_notice(
                demo_answer,
                error_code=ollama_result_status,
                subject=subject_used or detected_subject,
                has_verified_source=has_verified_source,
                model=settings["ollama_model"],
            )
            provider = educational_context["provider"]
            if has_verified_source:
                local_fallback_reason = "ollama_unavailable"

    educational_context.update({
        "grounding_required": grounding_required,
        "grounded_source_available": grounded_source_available,
        "answer_grounded": answer_grounded,
        "source_confidence": source_confidence,
        "generation_blocked_reason": generation_blocked_reason,
        "local_fallback_reason": local_fallback_reason,
    })

    history_id = save_history(
        payload,
        demo_answer,
        conversation_context,
        provider=provider,
        provenance_status=response_provenance,
        content_sources=content_sources,
    )
    processing_time_ms = round((perf_counter() - started_at) * 1000)

    return {
        **demo_answer,
        "history_id": history_id,
        "provenance_status": response_provenance,
        "retrieval_provenance_status": retrieval["provenance_status"],
        "provider": provider,
        "processing_time_ms": processing_time_ms,
        "detected_subject": detected_subject,
        "subject_mode": subject_mode,
        "subject_used": subject_used,
        "subject_confidence": subject_confidence,
        "subject_fallback_used": subject_fallback_used,
        "category": (
            local_results[0].get("metadata", {}).get("display_category")
            or local_results[0].get("metadata", {}).get("category")
            if local_results else "Sin categoría"
        ) or "Sin categoría",
        "source_title": local_results[0]["title"] if local_results else None,
        "ai_mode_used": ai_mode,
        "ollama_attempted": ollama_attempted,
        "used_ollama": ollama_attempted,
        "ollama_timeout": ollama_timeout,
        "ollama_status": ollama_result_status,
        "used_local_content": has_verified_source,
        "local_content_found": has_verified_source,
        "grounding_required": grounding_required,
        "grounded_source_available": grounded_source_available,
        "answer_grounded": answer_grounded,
        "source_confidence": source_confidence,
        "generation_blocked_reason": generation_blocked_reason,
        "answer_warning": answer_warning,
        "local_fallback_reason": local_fallback_reason,
        "ollama": {
            "status": ollama_result_status,
            "error_code": ollama_result_status if ollama_result_status in {
                "ollama_unreachable",
                "model_not_installed",
                "ollama_timeout",
                "generation_error",
            } else None,
            "enabled": ollama_status["enabled"],
            "available": ollama_status["available"],
            "model": ollama_status["model"],
            "model_installed": ollama_status["model_installed"],
            "timeout_seconds": settings["ollama_timeout_seconds"],
        },
        "active_course": payload.course,
        "profile_course": profile_course,
        "effective_course": retrieval.get("effective_course"),
        "source_course": retrieval.get("source_course"),
        "source_subject": retrieval.get("source_subject"),
        "found_in_other_course": retrieval.get("found_in_other_course", False),
        "query_analysis": conversation_context["query_analysis"],
        "retrieval_query_analysis": retrieval["query_analysis"],
        "conversation_context": {
            "conversation_id": payload.conversation_id,
            "normalized_question": conversation_context["normalized_question"],
            "contextual_question": conversation_context["contextual_question"],
            "active_topic": conversation_context["active_topic"],
            "confidence": conversation_context["confidence"],
            "used_context": conversation_context["used_context"],
        },
        "content_sources": content_sources,
        "related_sources": [
            {
                "title": item["title"],
                "path": item["path"],
                "section": item["section"],
                "summary": item["summary"],
                "course": item.get("course"),
                "subject": item.get("subject"),
            }
            for item in related_results
        ],
        "retrieval": {
            "minimum_score": retrieval["minimum_score"],
            "best_score": retrieval["best_score"],
            "searched_courses": retrieval.get("searched_courses", []),
            "global_fallback": retrieval.get("global_fallback", False),
        },
        "ai_context": educational_context,
    }


@app.get("/history")
def list_history(
    profile_id: int | None = None,
    status: str | None = None,
    favorite: bool | None = None,
    limit: int | None = Query(default=None, ge=1, le=100),
):
    if status is not None and status not in {"leido", "pendiente"}:
        raise HTTPException(status_code=400, detail="Estado invalido")

    conditions = []
    parameters: list[object] = []

    if profile_id is not None:
        conditions.append("profile_id = ?")
        parameters.append(profile_id)
    if status is not None:
        conditions.append("status = ?")
        parameters.append(status)
    if favorite is not None:
        conditions.append("is_favorite = ?")
        parameters.append(1 if favorite else 0)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    limit_clause = "LIMIT ?" if limit is not None else ""
    if limit is not None:
        parameters.append(limit)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT * FROM chat_history
            {where_clause}
            ORDER BY created_at DESC, id DESC
            {limit_clause}
            """,
            parameters,
        ).fetchall()

    return {
        "status": "ok",
        "items": [row_to_history_item(row) for row in rows],
    }


@app.get("/history/continue")
def continue_history(profile_id: int | None = None):
    with get_connection() as connection:
        profile_filter = "AND profile_id = ?" if profile_id is not None else ""
        params = (profile_id,) if profile_id is not None else ()
        row = connection.execute(
            f"""
            SELECT * FROM chat_history
            WHERE status = 'pendiente'
            {profile_filter}
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            params,
        ).fetchone()

        if row is None:
            row = connection.execute(
                f"""
                SELECT * FROM chat_history
                {"WHERE profile_id = ?" if profile_id is not None else ""}
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                """,
                params,
            ).fetchone()

    return {
        "status": "ok",
        "item": row_to_history_item(row) if row else None,
    }


@app.patch("/history/{history_id}/status")
def update_history_status(history_id: int, payload: HistoryStatusUpdate):
    if payload.status not in {"leido", "pendiente"}:
        raise HTTPException(status_code=400, detail="Estado invalido")

    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE chat_history SET status = ? WHERE id = ?",
            (payload.status, history_id),
        )

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Historial no encontrado")

    return {
        "status": "ok",
        "item": get_history_item(history_id),
    }


@app.patch("/history/{history_id}/favorite")
def update_history_favorite(history_id: int, payload: HistoryFavoriteUpdate):
    current_item = get_history_item(history_id)
    next_favorite = (
        not current_item["is_favorite"]
        if payload.is_favorite is None
        else payload.is_favorite
    )

    with get_connection() as connection:
        connection.execute(
            "UPDATE chat_history SET is_favorite = ? WHERE id = ?",
            (1 if next_favorite else 0, history_id),
        )

    return {
        "status": "ok",
        "item": get_history_item(history_id),
    }
