# Mapa de código

## Backend

| Archivo | Responsabilidad y cuidado |
| --- | --- |
| `backend/main.py` | API FastAPI, SQLite, perfiles, avatares, historial, chat, configuración y videos. Cambiar contratos afecta el frontend. |
| `backend/content_reader.py` | Índice, normalización, detección de materia, scoring y recuperación local. Ajustar umbrales exige pruebas de procedencia. |
| `backend/demo_tutor.py` | Fallback pedagógico desde contenido local o demo. No perder la adaptación por curso. |
| `backend/educational_level.py` | Reglas de extensión y complejidad por nivel escolar. |
| `backend/educational_config.py` | Mapeos de cursos, materias y carpetas. |
| `backend/conversation_context.py` | Seguimientos y tema activo por conversación. |
| `backend/ollama_client.py` y `prompt_builder.py` | Cliente local y preparación/limpieza de prompts; preservar timeout y fallback. |
| `backend/response_states.py` y `ai_contract.py` | Estados de procedencia y contrato de contexto para proveedores. |
| `backend/tests/` | Pruebas de búsqueda, contexto, perfiles, procedencia y Ollama. |

Mejora futura: separar rutas FastAPI por dominio y añadir pruebas end-to-end, sin cambiar el contrato actual sin migración.

## Frontend

| Archivo | Responsabilidad y cuidado |
| --- | --- |
| `frontend/src/App.jsx` | Contenedor principal: perfiles, solicitudes API, historial, chat y estados. Probar normal/demo/historial ante cambios. |
| `frontend/src/App.css` | Layout global, globos, paneles y responsive. Preservar legibilidad y posición de Nexo. |
| `components/ChatBubbles.jsx` | Burbujas de estudiante y Nexo, fuentes y metadatos. |
| `components/NexoAvatar.jsx` | Render seguro de assets y fallback visual. |
| `components/UserAvatar.jsx` | Avatar local o inicial del perfil. |
| `assets/nexo/nexoVariants.js` | Mapa de imágenes y variantes por materia; no importar assets inexistentes. |
| `config/suggestedQuestions.js` | Catálogo de sugerencias. |
| `config/appInfo.js` | Nombre, autor, año y versión visibles. |

## Recursos y operaciones

- `contenidos/`: Markdown curricular organizado por curso y materia; no mezclar con fuentes no revisadas.
- `backend/data/`: configuración y videos curados; los datos de usuario son locales.
- `scripts/00_*` a `04_*`: verificación, instalación, backend, frontend y navegador. Los nombres alternativos sin prefijo mantienen compatibilidad.
- `iniciar_chat_escolar.bat`: inicio conjunto desde la raíz.
- `docs/`: documentación; `pruebas/` contiene material de pruebas previas.
