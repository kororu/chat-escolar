from unicodedata import normalize

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


def normalize_text(text: str) -> str:
    without_accents = normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return without_accents.lower()


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

    return {
        "answer": answer,
        "summary": summary,
        "status": "ok",
    }


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


@app.post("/chat/demo")
def chat_demo(payload: ChatDemoRequest):
    return make_demo_answer(payload)
