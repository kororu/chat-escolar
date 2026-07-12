import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .ai_contract import build_educational_context
except ImportError:
    from ai_contract import build_educational_context

try:
    from .content_reader import normalize_question, retrieve_local_content
except ImportError:
    from content_reader import normalize_question, retrieve_local_content

try:
    from .conversation_context import build_conversation_context
except ImportError:
    from conversation_context import build_conversation_context

try:
    from .demo_tutor import detect_topic, make_demo_answer
except ImportError:
    from demo_tutor import detect_topic, make_demo_answer

try:
    from .educational_config import PROFILE_COURSES
except ImportError:
    from educational_config import PROFILE_COURSES

try:
    from .response_states import (
        CLARIFICATION_REQUIRED,
        uses_verified_local_content,
    )
except ImportError:
    from response_states import (
        CLARIFICATION_REQUIRED,
        uses_verified_local_content,
    )

try:
    from .text_utils import normalize_text
except ImportError:
    from text_utils import normalize_text

DB_PATH = Path(__file__).with_name("chat_escolar.db")
VIDEOS_PATH = Path(__file__).with_name("data") / "videos_curados.json"

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
    subject: str
    question: str
    profile_id: int | None = None
    user_name: str | None = None
    user_role: str | None = None
    conversation_id: str | None = Field(default=None, max_length=120)


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    role: str
    course: str


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
        }
        for column, definition in missing_columns.items():
            if column not in history_columns:
                connection.execute(f"ALTER TABLE chat_history ADD COLUMN {column} {definition}")


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


def save_history(
    payload: ChatDemoRequest,
    demo_answer: dict[str, str],
    conversation_context: dict | None = None,
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
                context_confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pendiente', 0, ?, ?, ?, ?, ?, ?, ?)
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
            ),
        )
        return cursor.lastrowid


def get_recent_conversation_items(profile_id: int | None, conversation_id: str | None) -> list[dict]:
    if profile_id is None or not conversation_id:
        return []

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT question, normalized_question, contextual_question, active_topic,
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

    return dict(row)


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
    subject: str,
    q: str,
    mode: str = "Estudiar para el colegio",
):
    result = retrieve_local_content(course, subject, q, mode=mode)
    return {"status": "ok", **result}


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

    return {"status": "ok", "items": [dict(row) for row in rows]}


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


@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int):
    with get_connection() as connection:
        profile = connection.execute(
            "SELECT id, name FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()
        if profile is None:
            raise HTTPException(status_code=404, detail="Perfil no encontrado")

        deleted_history = connection.execute(
            "DELETE FROM chat_history WHERE profile_id = ?", (profile_id,)
        ).rowcount
        connection.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))

    return {
        "status": "ok",
        "deleted_profile": {"id": profile["id"], "name": profile["name"]},
        "deleted_history_count": deleted_history,
    }


@app.post("/chat/demo")
def chat_demo(payload: ChatDemoRequest):
    if payload.profile_id is not None:
        profile = get_profile_or_404(payload.profile_id)
        payload.user_name = profile["name"]
        payload.user_role = profile["role"]
        payload.course = profile["course"]

    if payload.profile_id is not None and not payload.conversation_id:
        payload.conversation_id = f"profile-{payload.profile_id}-default"

    recent_items = get_recent_conversation_items(
        payload.profile_id,
        payload.conversation_id,
    )
    conversation_context = build_conversation_context(payload.question, recent_items)

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
        retrieval = retrieve_local_content(
            payload.course,
            payload.subject,
            conversation_context["contextual_question"],
            mode=payload.mode,
        )

    local_results = retrieval["results"]
    related_results = retrieval.get("related_results", [])
    educational_context = build_educational_context(
        payload,
        retrieval,
        conversation_context,
    )
    demo_answer = make_demo_answer(
        payload,
        local_content=local_results[0] if local_results else None,
        related_content=related_results[0] if related_results else None,
        query_analysis=retrieval["query_analysis"],
        provenance_status=retrieval["provenance_status"],
    )
    history_id = save_history(payload, demo_answer, conversation_context)

    return {
        **demo_answer,
        "history_id": history_id,
        "provenance_status": retrieval["provenance_status"],
        "provider": educational_context["provider"],
        "used_local_content": uses_verified_local_content(retrieval["provenance_status"]),
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
        "content_sources": [
            {"title": local_results[0]["title"], "path": local_results[0]["path"]}
        ] if local_results else [],
        "related_sources": [
            {
                "title": item["title"],
                "path": item["path"],
                "section": item["section"],
                "summary": item["summary"],
            }
            for item in related_results
        ],
        "retrieval": {
            "minimum_score": retrieval["minimum_score"],
            "best_score": retrieval["best_score"],
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
