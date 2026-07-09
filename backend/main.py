from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Chat Escolar API",
    description="Backend inicial para Chat Escolar",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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