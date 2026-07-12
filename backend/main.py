import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from unicodedata import normalize

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = Path(__file__).with_name("chat_escolar.db")

app = FastAPI(
    title="Chat Escolar API",
    description="Backend inicial para Chat Escolar",
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


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    role: str
    course: str


class HistoryStatusUpdate(BaseModel):
    status: str


class HistoryFavoriteUpdate(BaseModel):
    is_favorite: bool | None = None


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


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
        if "profile_id" not in history_columns:
            connection.execute(
                "ALTER TABLE chat_history ADD COLUMN profile_id INTEGER REFERENCES profiles(id)"
            )


def row_to_history_item(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["is_favorite"] = bool(item["is_favorite"])
    return item


def normalize_text(text: str) -> str:
    without_accents = normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return without_accents.lower()


def detect_topic(question: str) -> str:
    clean_question = normalize_text(question)

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


def save_history(payload: ChatDemoRequest, demo_answer: dict[str, str]) -> int:
    created_at = datetime.now(timezone.utc).isoformat()

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
                profile_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pendiente', 0, ?, ?)
            """,
            (
                payload.course,
                payload.mode,
                payload.subject,
                detect_topic(payload.question),
                payload.question,
                demo_answer["summary"],
                demo_answer["answer"],
                created_at,
                payload.profile_id,
            ),
        )
        return cursor.lastrowid


def get_history_item(history_id: int) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM chat_history WHERE id = ?",
            (history_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Historial no encontrado")

    return row_to_history_item(row)


def make_demo_answer(payload: ChatDemoRequest) -> dict[str, str]:
    question = normalize_text(payload.question)

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
        answer = (
            "Explicacion corta:\n"
            f"Esta es una respuesta demo para {payload.course}, en el modo {payload.mode}.\n\n"
            "Ejemplo:\n"
            f"Si estas estudiando {payload.subject}, podemos dividir el tema en partes pequenas.\n\n"
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

    return {
        "answer": f"{introduction}\n\n{answer}",
        "summary": summary,
        "status": "ok",
    }


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
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "chat-escolar-backend",
    }


@app.post("/profiles", status_code=201)
def create_profile(payload: ProfileCreate):
    valid_roles = {"Estudiante", "Apoderado", "Docente"}
    valid_courses = {"1° básico", "5° básico", "6° básico"}
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

    return {"status": "ok", "profile": get_profile_or_404(cursor.lastrowid)}


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


@app.post("/chat/demo")
def chat_demo(payload: ChatDemoRequest):
    if payload.profile_id is not None:
        profile = get_profile_or_404(payload.profile_id)
        payload.user_name = profile["name"]
        payload.user_role = profile["role"]
        payload.course = profile["course"]

    demo_answer = make_demo_answer(payload)
    history_id = save_history(payload, demo_answer)

    return {
        **demo_answer,
        "history_id": history_id,
    }


@app.get("/history")
def list_history(profile_id: int | None = None):
    with get_connection() as connection:
        if profile_id is None:
            rows = connection.execute(
                "SELECT * FROM chat_history ORDER BY created_at DESC, id DESC"
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT * FROM chat_history
                WHERE profile_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (profile_id,),
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
