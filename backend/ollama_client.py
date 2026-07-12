"""Cliente pequeño y opcional para el servidor local de Ollama."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:2b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}
# El chequeo visual no debe demorar una conversación cuando Ollama está apagado.
STATUS_TIMEOUT_SECONDS = min(1.0, OLLAMA_TIMEOUT_SECONDS)


class OllamaError(RuntimeError):
    """Error controlado: el tutor puede volver al modo demo."""


class OllamaUnavailableError(OllamaError):
    pass


class OllamaModelNotFoundError(OllamaError):
    pass


def _request(path: str, *, payload: dict | None = None, timeout: float = OLLAMA_TIMEOUT_SECONDS) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        f"{OLLAMA_BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310: URL local configurable
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 404:
            raise OllamaModelNotFoundError("El modelo configurado no está instalado en Ollama.") from error
        raise OllamaError(f"Ollama respondió con error {error.code}.") from error
    except (URLError, TimeoutError, OSError) as error:
        raise OllamaUnavailableError("Ollama no está disponible.") from error
    except json.JSONDecodeError as error:
        raise OllamaError("Ollama devolvió una respuesta inválida.") from error


def list_models() -> list[str]:
    data = _request("/api/tags", timeout=STATUS_TIMEOUT_SECONDS)
    return [model["name"] for model in data.get("models", []) if isinstance(model, dict) and model.get("name")]


def get_status() -> dict:
    if not OLLAMA_ENABLED:
        return {
            "enabled": False,
            "available": False,
            "base_url": OLLAMA_BASE_URL,
            "model": OLLAMA_MODEL,
            "model_installed": False,
            "models": [],
            "message": "La IA local está desactivada. Chat Escolar seguirá en modo básico.",
        }
    try:
        models = list_models()
    except OllamaUnavailableError:
        return {
            "enabled": True,
            "available": False,
            "base_url": OLLAMA_BASE_URL,
            "model": OLLAMA_MODEL,
            "model_installed": False,
            "models": [],
            "message": "Ollama no está disponible. Chat Escolar seguirá en modo básico.",
        }
    except OllamaError as error:
        return {
            "enabled": True,
            "available": False,
            "base_url": OLLAMA_BASE_URL,
            "model": OLLAMA_MODEL,
            "model_installed": False,
            "models": [],
            "message": str(error),
        }
    installed = OLLAMA_MODEL in models
    return {
        "enabled": True,
        "available": True,
        "base_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL,
        "model_installed": installed,
        "models": models,
        "message": "Ollama conectado" if installed else "Ollama conectado, pero falta el modelo configurado.",
    }


def generate(prompt: str) -> str:
    if not OLLAMA_ENABLED:
        raise OllamaUnavailableError("La IA local está desactivada.")
    data = _request(
        "/api/generate",
        payload={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
    )
    answer = data.get("response")
    if not isinstance(answer, str) or not answer.strip():
        raise OllamaError("Ollama no devolvió una respuesta de texto.")
    return answer.strip()
