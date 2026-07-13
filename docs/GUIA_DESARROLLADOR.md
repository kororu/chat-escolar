# Guía para desarrolladores

## Preparación y ejecución

Clona el repositorio, entra a su raíz y usa en Windows:

```powershell
scripts\00_verificar_entorno.bat
scripts\01_instalar_dependencias.bat
iniciar_chat_escolar.bat
```

Para desarrollo manual, usa los comandos del [README](../README.md#ejecución-manual-para-desarrollo). Verifica `http://127.0.0.1:8000/health` y abre `http://127.0.0.1:8000/docs` para probar la API.

Endpoints de uso frecuente: `POST /profiles`, `GET /profiles`, `POST /chat/demo`, `GET /history`, `GET /content/search`, `GET /ai/status` y `PATCH /settings`. Swagger muestra el contrato vigente.

## Mantenimiento seguro

- **Contenidos**: agrega Markdown bajo `contenidos/<curso>/<materia>/`, con título claro, nombre descriptivo y material original. Consulta [README_CONTENIDOS_LOCALES.md](README_CONTENIDOS_LOCALES.md).
- **Sugerencias**: edita `frontend/src/config/suggestedQuestions.js`. Mantén chips compactos y no actives sugerencias automáticamente para perfiles normales.
- **Nexo**: agrega PNG transparente en `frontend/src/assets/nexo/` y registra la variante en `nexoVariants.js`. Prueba el build después.
- **Materia y búsqueda**: `backend/content_reader.py` contiene normalización, detección, ranking y umbrales; `educational_config.py` contiene mapeos. Cambios requieren pruebas de procedencia.
- **Respuestas**: `demo_tutor.py` y `educational_level.py` controlan el fallback pedagógico; preserva claridad, nivel de curso y una sola pregunta de práctica.
- **Ollama**: revisa `/ai/status`, configura desde la interfaz o `PATCH /settings`, y usa `ollama list`. El modo básico debe seguir operativo.

## Calidad, commits y release

```powershell
cd frontend
npm run build
git status
git diff --check
```

Usa commits pequeños, por ejemplo `docs: actualizar guía de arquitectura` o `fix: ajustar búsqueda local`. Antes de release, prueba perfiles/demo/historial, Nexo, materia automática, modo básico y el fallback de Ollama. No subas secretos, base de datos personal ni avatares de usuarios.
