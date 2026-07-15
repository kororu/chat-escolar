# Arquitectura técnica

## Visión general

Chat Escolar funciona en el equipo local. React/Vite presenta el chat; FastAPI procesa solicitudes, SQLite persiste perfiles e historial y `contenidos/` entrega apoyo curricular. Ollama es opcional, nunca el único camino de respuesta.

```text
Usuario pregunta → Frontend envía mensaje → Backend detecta materia
→ Busca contenido local → Evalúa confianza → Genera respuesta pedagógica
→ Opcionalmente usa Ollama según configuración → Guarda historial
→ Frontend muestra respuesta con Nexo
```

## Capas

- **Frontend (`frontend/`)**: `App.jsx` coordina perfiles, chat, configuración e historial; `ChatBubbles`, `NexoAvatar` y `UserAvatar` presentan la conversación. `suggestedQuestions.js` define las sugerencias.
- **API (`backend/main.py`)**: expone perfiles, chat, historial, búsqueda, videos, estado y configuración de IA. CORS permite el Vite local.
- **Persistencia**: `backend/chat_escolar.db` guarda perfiles, historial y contexto. `backend/data/settings.json` conserva la preferencia de IA; los avatares se guardan bajo `backend/data/profile_avatars/`.
- **Contenidos**: `content_reader.py` indexa Markdown por curso/materia, normaliza preguntas, puntúa documentos y devuelve procedencia verificable.

## Flujo educativo

`educational_config.py` traduce etiquetas visibles a carpetas. `content_reader.py` detecta materia automática, prioriza frases históricas específicas y busca fuentes; `conversation_context.py` reconstruye seguimientos prudentes. `demo_tutor.py` crea el fallback pedagógico por curso usando `educational_level.py`. Los estados de procedencia están centralizados en `response_states.py`.

En Modo Escolar, `prompt_builder.py` permite usar Ollama solo sobre una fuente local verificada y le prohíbe completar hechos desde su memoria. Sin fuente verificada, `main.py` bloquea la generación factual. En Modo Explorar puede haber generación sin fuente cuando la configuración lo permite, siempre con procedencia y advertencia de respuesta no verificada.

## Experiencia visual y operaciones

Los PNG y el mapa de variantes de Nexo están en `frontend/src/assets/nexo/`. El perfil demo ofrece chips; un perfil normal mantiene una bienvenida limpia sin chips automáticos. Los scripts en `scripts/` verifican entorno, instalan dependencias e inician ambos servicios.

La futura distribución prevista es `ChatEscolar_Setup.exe`; no existe todavía. Ver [INSTALADOR_WINDOWS_1_0.md](INSTALADOR_WINDOWS_1_0.md).
