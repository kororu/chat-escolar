"""Cliente pequeño y opcional para el servidor local de Ollama."""

import json
import os
import socket
import subprocess
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:2b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "90"))
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}
# El chequeo visual no debe demorar una conversación cuando Ollama está apagado.
STATUS_TIMEOUT_SECONDS = min(1.0, OLLAMA_TIMEOUT_SECONDS)
RUNTIME_DIRECTORY = Path(__file__).resolve().parent.parent / ".runtime"
OLLAMA_PID_PATH = RUNTIME_DIRECTORY / "ollama.pid"
_managed_process: subprocess.Popen | None = None


class OllamaError(RuntimeError):
    """Error controlado: el tutor puede volver al modo demo."""


class OllamaUnavailableError(OllamaError):
    pass


class OllamaModelNotFoundError(OllamaError):
    pass


class OllamaTimeoutError(OllamaError):
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
    except (TimeoutError, socket.timeout) as error:
        raise OllamaTimeoutError("La IA local excedió el tiempo máximo configurado.") from error
    except URLError as error:
        if isinstance(error.reason, (TimeoutError, socket.timeout)) or "timed out" in str(error.reason).lower():
            raise OllamaTimeoutError("La IA local excedió el tiempo máximo configurado.") from error
        raise OllamaUnavailableError("Ollama no está disponible.") from error
    except OSError as error:
        raise OllamaUnavailableError("Ollama no está disponible.") from error
    except json.JSONDecodeError as error:
        raise OllamaError("Ollama devolvió una respuesta inválida.") from error


def list_models(*, timeout: float = STATUS_TIMEOUT_SECONDS) -> list[str]:
    data = _request("/api/tags", timeout=timeout)
    return [model["name"] for model in data.get("models", []) if isinstance(model, dict) and model.get("name")]


def get_status(
    *,
    model: str = OLLAMA_MODEL,
    enabled: bool = OLLAMA_ENABLED,
    timeout_seconds: float = OLLAMA_TIMEOUT_SECONDS,
) -> dict:
    if not enabled:
        return {
            "status": "ollama_disabled",
            "enabled": False,
            "available": False,
            "server_reachable": False,
            "base_url": OLLAMA_BASE_URL,
            "model": model,
            "configured_model": model,
            "model_installed": False,
            "models": [],
            "message": "La IA local está desactivada. Chat Escolar seguirá en modo básico.",
        }
    try:
        models = list_models(timeout=min(1.0, timeout_seconds))
    except OllamaTimeoutError:
        return {
            "status": "ollama_timeout",
            "enabled": True,
            "available": False,
            "server_reachable": False,
            "base_url": OLLAMA_BASE_URL,
            "model": model,
            "configured_model": model,
            "model_installed": False,
            "models": [],
            "message": "La comprobación de Ollama excedió el tiempo máximo configurado.",
        }
    except OllamaUnavailableError:
        return {
            "status": "ollama_unreachable",
            "enabled": True,
            "available": False,
            "server_reachable": False,
            "base_url": OLLAMA_BASE_URL,
            "model": model,
            "configured_model": model,
            "model_installed": False,
            "models": [],
            "message": "Ollama no está disponible. Chat Escolar seguirá en modo básico.",
        }
    except OllamaError as error:
        return {
            "status": "generation_error",
            "enabled": True,
            "available": False,
            "server_reachable": False,
            "base_url": OLLAMA_BASE_URL,
            "model": model,
            "configured_model": model,
            "model_installed": False,
            "models": [],
            "message": str(error),
        }
    installed = model in models
    return {
        "status": "ready_for_generation" if installed else "model_not_installed",
        "enabled": True,
        "available": True,
        "server_reachable": True,
        "base_url": OLLAMA_BASE_URL,
        "model": model,
        "configured_model": model,
        "model_installed": installed,
        "models": models,
        "message": "Ollama conectado, modelo pendiente de prueba." if installed else "Ollama conectado, pero falta el modelo configurado.",
    }


def generate(
    prompt: str,
    *,
    model: str = OLLAMA_MODEL,
    enabled: bool = OLLAMA_ENABLED,
    timeout_seconds: float = OLLAMA_TIMEOUT_SECONDS,
) -> str:
    if not enabled:
        raise OllamaUnavailableError("La IA local está desactivada.")
    data = _request(
        "/api/generate",
        payload={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "keep_alive": "10m",
        },
        timeout=timeout_seconds,
    )
    answer = data.get("response")
    if not isinstance(answer, str) or not answer.strip():
        raise OllamaError("Ollama no devolvió una respuesta de texto.")
    return answer.strip()


def unload_model(*, model: str = OLLAMA_MODEL, timeout: float = 5.0) -> bool:
    """Ask Ollama to unload only the configured model; server ownership is untouched."""
    try:
        _request("/api/generate", payload={"model": model, "prompt": "", "stream": False, "keep_alive": 0}, timeout=timeout)
        return True
    except OllamaError:
        return False


def start_managed_server(*, wait_seconds: float = 5.0) -> dict:
    """Start `ollama serve` only when the local API was not already reachable."""
    global _managed_process
    try:
        _request("/api/version", timeout=STATUS_TIMEOUT_SECONDS)
        return {"status": "already_running", "started_by_chat_escolar": False}
    except OllamaError:
        pass
    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        _managed_process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
    except OSError as error:
        return {"status": "not_installed", "started_by_chat_escolar": False, "message": str(error)}
    RUNTIME_DIRECTORY.mkdir(parents=True, exist_ok=True)
    OLLAMA_PID_PATH.write_text(str(_managed_process.pid), encoding="utf-8")
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        try:
            _request("/api/version", timeout=STATUS_TIMEOUT_SECONDS)
            return {"status": "started_by_chat_escolar", "started_by_chat_escolar": True, "pid": _managed_process.pid}
        except OllamaError:
            time.sleep(0.15)
    return {"status": "starting", "started_by_chat_escolar": True, "pid": _managed_process.pid}


def stop_managed_server() -> bool:
    """Terminate only the Popen instance created by this backend, never global ollama.exe."""
    global _managed_process
    if _managed_process is None:
        return False
    if _managed_process.poll() is None:
        _managed_process.terminate()
        try:
            _managed_process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            _managed_process.kill()
    _managed_process = None
    try:
        OLLAMA_PID_PATH.unlink(missing_ok=True)
    except OSError:
        pass
    return True
