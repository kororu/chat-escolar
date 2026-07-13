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
    from .content_reader import detect_subject_from_question, normalize_question, retrieve_local_content
except ImportError:
    from content_reader import detect_subject_from_question, normalize_question, retrieve_local_content

try:
    from .conversation_context import build_conversation_context
except ImportError:
    from conversation_context import build_conversation_context

try:
    from .demo_tutor import build_local_content_fallback, detect_topic, make_demo_answer
except ImportError:
    from demo_tutor import build_local_content_fallback, detect_topic, make_demo_answer

try:
    from .educational_config import ALL_COURSES_LABEL, PROFILE_COURSES, is_all_courses
except ImportError:
    from educational_config import ALL_COURSES_LABEL, PROFILE_COURSES, is_all_courses

try:
    from .response_states import (
        CLARIFICATION_REQUIRED,
        DEMO_FALLBACK,
        LOCAL_CONTENT_FALLBACK,
        LOCAL_VERIFIED,
        OLLAMA_GENERATED,
        OLLAMA_UNAVAILABLE,
        OLLAMA_WITH_LOCAL_CONTENT,
        PROVIDER_OLLAMA,
        PROVIDER_OLLAMA_WITH_LOCAL_CONTENT,
        PROVIDER_LOCAL_CONTENT,
        uses_verified_local_content,
    )
except ImportError:
    from response_states import (
        CLARIFICATION_REQUIRED,
        DEMO_FALLBACK,
        LOCAL_CONTENT_FALLBACK,
        LOCAL_VERIFIED,
        OLLAMA_GENERATED,
        OLLAMA_UNAVAILABLE,
        OLLAMA_WITH_LOCAL_CONTENT,
        PROVIDER_OLLAMA,
        PROVIDER_OLLAMA_WITH_LOCAL_CONTENT,
        PROVIDER_LOCAL_CONTENT,
        uses_verified_local_content,
    )

try:
    from .ollama_client import OllamaError, generate as generate_with_ollama, get_status as get_ollama_status
    from .prompt_builder import build_ollama_prompt, clean_ollama_response
except ImportError:
    from ollama_client import OllamaError, generate as generate_with_ollama, get_status as get_ollama_status
    from prompt_builder import build_ollama_prompt, clean_ollama_response

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
logger = logging.getLogger(__name__)
AI_MODES = {"basic", "automatic", "explore_only"}
AUTO_SUBJECT_VALUES = {"automatic", "automatica", "auto", ""}
CURRICULAR_SUBJECTS = ("Ciencias Naturales", "Matemática", "Lenguaje", "Historia")
DEFAULT_SETTINGS = {
    "ai_mode": "basic",
    "ollama_enabled": False,
    "ollama_model": "qwen3.5:2b",
    "ollama_timeout_seconds": 25,
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
    if not isinstance(settings["ollama_timeout_seconds"], int) or not 5 <= settings["ollama_timeout_seconds"] <= 60:
        raise HTTPException(status_code=400, detail="El timeout debe estar entre 5 y 60 segundos")
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
    """Prefer a detected subject, expanding only when it has no verified source."""
    candidates: list[tuple[str, dict]] = []
    if detected_subject:
        initial = retrieve_local_content(course, detected_subject, question, mode=mode)
        candidates.append((detected_subject, initial))
        if initial["provenance_status"] == LOCAL_VERIFIED:
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
        **status,
        "ai_mode": settings["ai_mode"],
        "ollama_enabled": settings["ollama_enabled"],
        "ollama_timeout_seconds": settings["ollama_timeout_seconds"],
    }


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


@app.post("/ai/test")
def ai_test(payload: AiTestRequest):
    settings = load_settings()
    if settings["ai_mode"] == "basic" or not settings["ollama_enabled"]:
        return {
            "status": "disabled",
            "provider": "demo",
            "message": "Activa IA local automática o Solo Explorar para probar Ollama.",
            "answer": None,
        }
    status = get_cached_ollama_status(settings)
    if not status["available"] or not status["model_installed"]:
        return {
            "status": "unavailable",
            "provider": "demo",
            "message": status["message"],
            "answer": None,
        }
    try:
        answer = clean_ollama_response(generate_with_ollama(
            payload.prompt,
            model=settings["ollama_model"],
            enabled=settings["ollama_enabled"],
            timeout_seconds=settings["ollama_timeout_seconds"],
        ))
    except OllamaError as error:
        return {"status": "unavailable", "provider": "demo", "message": str(error), "answer": None}
    return {"status": "ok", "provider": PROVIDER_OLLAMA, "answer": answer}


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
    settings = load_settings()
    ai_mode = settings["ai_mode"]
    is_exploration = "explor" in normalize_text(payload.mode or "") or is_all_courses(payload.course)
    ollama_allowed_for_request = (
        ai_mode == "automatic"
        or (ai_mode == "explore_only" and is_exploration)
    )
    ollama_attempted = False
    ollama_timeout = False
    if settings["ollama_enabled"] and ollama_allowed_for_request:
        ollama_status = get_cached_ollama_status(settings)
    else:
        ollama_status = {
            "enabled": False,
            "available": False,
            "model": settings["ollama_model"],
            "model_installed": False,
            "message": "La IA local no se usa con la configuración actual.",
        }
    educational_context["ollama_enabled"] = (
        ollama_status["enabled"]
        and ollama_status["available"]
        and ollama_status["model_installed"]
    )
    educational_context["ollama_available"] = ollama_status["available"]
    has_verified_source = retrieval["provenance_status"] == LOCAL_VERIFIED and bool(local_results)
    can_use_general_ollama = (
        not has_verified_source
        and is_exploration
    )

    if has_verified_source:
        demo_answer = build_local_content_fallback(payload, local_results[0])
        response_provenance = LOCAL_CONTENT_FALLBACK
        provider = PROVIDER_LOCAL_CONTENT

    if ollama_allowed_for_request and (has_verified_source or can_use_general_ollama):
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
                demo_answer = {
                    "answer": answer,
                    "summary": "Explicación generada con IA local" + (" usando contenido local verificado." if has_verified_source else " sin fuente local verificada."),
                    "status": "ok",
                }
                response_provenance = OLLAMA_WITH_LOCAL_CONTENT if has_verified_source else OLLAMA_GENERATED
                provider = PROVIDER_OLLAMA_WITH_LOCAL_CONTENT if has_verified_source else PROVIDER_OLLAMA
            except OllamaError as error:
                logger.warning("Ollama falló; se usará el fallback local: %s", error)
                ollama_timeout = "timeout" in str(error).lower()
                response_provenance = LOCAL_CONTENT_FALLBACK if has_verified_source else DEMO_FALLBACK
                provider = PROVIDER_LOCAL_CONTENT if has_verified_source else "demo"
        else:
            provider = educational_context["provider"]

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
        "ai_mode_used": ai_mode,
        "ollama_attempted": ollama_attempted,
        "ollama_timeout": ollama_timeout,
        "used_local_content": has_verified_source,
        "ollama": {
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
