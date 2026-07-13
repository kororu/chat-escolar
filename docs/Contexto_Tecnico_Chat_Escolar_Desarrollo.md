# Contexto técnico del proyecto Chat Escolar

Este archivo sirve para mantener ordenado el chat técnico del proyecto **Chat Escolar**.

Este chat debe enfocarse en instalación, configuración, desarrollo, backend, frontend, Git, GitHub, Codex, errores, comandos y preparación de una versión local gratuita.

---

## IA local opcional con Ollama

La integración local usa `backend/ollama_client.py` para consultar `GET /api/tags` y generar con `POST /api/generate` (`stream: false`). No usa OpenAI API ni servicios externos. El modelo por defecto es `qwen3.5:2b`; se puede cambiar con `OLLAMA_MODEL` y `qwen3.5:4b` queda disponible para una instalación manual futura.

`GET /ai/status` informa si Ollama y el modelo están disponibles sin devolver 500 cuando están apagados. `POST /ai/test` permite verificar una respuesta local. En el chat, `ollama_with_local_content` solo se usa cuando existe fuente Markdown `local_verified`; el prompt limita el contexto a tres fuentes y unos 3200 caracteres. `ollama_generated` solo puede usarse para una explicación general en Modo Explorador o Todos los cursos, siempre marcada como no basada en fuente local verificada. El modo escolar sin fuente mantiene una respuesta transparente de respaldo.

La interfaz muestra una burbuja temporal de procesamiento al enviar una pregunta. El botón Enviar se deshabilita para impedir duplicados y el aviso cambia a los 10 y 30 segundos para explicar que Ollama puede tardar en equipos modestos. Este mensaje no se persiste en historial y no expone razonamiento interno. Streaming, cancelación, progreso real por etapas y cola de solicitudes quedan pendientes para una versión futura.

Las respuestas de `POST /chat/demo` incluyen el metadato entero `processing_time_ms`, calculado con `time.perf_counter()` desde la recepción hasta antes de devolver la respuesta. React lo muestra de forma discreta bajo la respuesta final; si supera 30 segundos, agrega el aviso `respuesta lenta`. Esta duración incluye intentos de Ollama y fallback, no se inserta en el texto educativo ni expone razonamiento interno.

Si una búsqueda devuelve `local_verified`, el sistema prepara un fallback educativo desde el Markdown antes de intentar Ollama. Si la IA local falla o no está disponible, la respuesta final usa `local_content_fallback` y `provider: local_content`: conserva `used_local_content`, las fuentes y una explicación real basada en secciones como Respuesta breve, Explicación completa, Ejemplo explicado, Mini resumen y Preguntas de práctica. Se excluyen metadatos, OA, notas editoriales y referencias normativas. `demo_fallback` queda solo para casos sin fuente local útil.

La adaptación educativa se centraliza en `backend/educational_level.py`. Cada nivel define edad aproximada, nivel lector, estilo de oración, máximo de ideas, una pregunta de práctica y límite de palabras para Ollama. El fallback local simplifica expresiones técnicas frecuentes en 1° a 6° básico, conserva conceptos importantes con una explicación clara y toma solo la primera pregunta de práctica del Markdown. La interfaz conserva los bloques Explicación, Ejemplo, Mini resumen y Pregunta de práctica separados de fuente, estado y tiempo.

## 1. Ruta local del proyecto

El proyecto está ubicado en:

```text
C:\Users\Ariel\Documents\proyectos\chat-escolar
```

---

## 2. Repositorio GitHub

Repositorio conectado:

```text
https://github.com/kororu/chat-escolar.git
```

Rama principal:

```text
main
```

---

## 3. Stack técnico actual

### Frontend

- React;
- Vite;
- JavaScript;
- CSS simple;
- ejecuta en `http://localhost:5173`.

### Backend

- Python;
- FastAPI;
- Uvicorn;
- SQLite;
- ejecuta en `http://127.0.0.1:8000`.

### Base de datos local

- SQLite;
- archivo local en backend;
- no debe subirse a GitHub.

### Control de versiones

- Git;
- GitHub.

### Editor

- Visual Studio Code;
- Codex instalado en VS Code para ayudar con modificaciones.

---

## 4. Herramientas instaladas y verificadas

En el PC se verificó:

- Git 2.55.0.windows.2;
- Node.js v24.18.0;
- npm 11.16.0;
- Python 3.14.6;
- pip 26.1.2;
- VS Code 1.128.0.

---

## 5. Problema corregido con npm

Al inicio `npm -v` fallaba por política de ejecución de PowerShell:

> No se puede cargar el archivo npm.ps1 porque la ejecución de scripts está deshabilitada.

Se solucionó cambiando la política para el usuario actual:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## 6. Estructura general actual del proyecto

```text
chat-escolar/
├── backend/
│   ├── .venv/
│   ├── ai_contract.py
│   ├── content_reader.py
│   ├── conversation_context.py
│   ├── demo_tutor.py
│   ├── educational_config.py
│   ├── main.py
│   ├── response_states.py
│   ├── requirements.txt
│   ├── text_utils.py
│   └── chat_escolar.db  // local, no subir
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── ...
├── docs/
│   ├── Chat_Escolar_Contexto_Proyecto.md
│   ├── Alcance_Version_1.md
│   ├── Guia_Preparacion_PC_Chat_Escolar.md
│   ├── Prompt_Chat_Escolar.md
│   ├── Diseno_UI_Chat_Escolar.md
│   ├── Contenidos_Iniciales_5to_Basico.md
│   ├── Modo_Explorador_Rutas.md
│   ├── Videos_Curados_Iniciales.md
│   ├── Historial_Chat_Escolar.md
│   ├── Proximos_Pasos_Chat_Escolar.md
│   ├── Guia_Config_Inicial_Cambio_PC_Chat_Escolar.md
│   └── Distribucion_Local_Gratuita_Chat_Escolar.md
├── contenidos/
├── prompts/
├── pruebas/
├── README.md
└── .gitignore
```

---

## 7. Commits importantes realizados

Historial reciente del proyecto:

```text
667fd26 Agrega historial local de preguntas
d1dbb2d Agrega tutor demo local sin IA
71521b2 Conecta frontend con estado del backend
66daaea Define distribucion local gratuita
98f12b8 Crea prototipo visual inicial de Chat Escolar
6b80567 Agrega guia de configuracion para cambio de PC
290de45 Agrega documentacion base de Chat Escolar
a6d4b3a Inicializa estructura base de Chat Escolar
```

---

## 8. Estado funcional actual

La app ya tiene:

1. Frontend React/Vite funcionando.
2. Backend FastAPI funcionando.
3. Conexión frontend-backend mediante endpoint `/health`.
4. Prototipo visual inicial de Chat Escolar.
5. Tutor demo local sin IA pagada.
6. Historial local de preguntas con SQLite.
7. Documentación base del proyecto.
8. Guía para cambio de PC.
9. Documento de distribución local gratuita.

---

## 9. Endpoints backend actuales

El backend tiene al menos:

### GET /

Devuelve mensaje de API funcionando.

### GET /health

Devuelve estado del backend.

### POST /chat/demo

Recibe pregunta y datos de curso/modo/materia.

Devuelve respuesta demo local sin usar OpenAI.

### GET /history

Lista historial de preguntas.

### PATCH /history/{id}/status

Permite cambiar estado entre leído y pendiente.

### PATCH /history/{id}/favorite

Permite marcar o desmarcar favorito.

### GET /history/continue

Devuelve última entrada pendiente o más reciente.

---

## 10. Comandos para levantar backend

Desde PowerShell:

```powershell
cd C:\Users\Ariel\Documents\proyectos\chat-escolar\backend
.venv\Scripts\activate
uvicorn main:app --reload
```

Backend disponible en:

```text
http://127.0.0.1:8000
```

Documentación FastAPI:

```text
http://127.0.0.1:8000/docs
```

---

## 11. Comandos para levantar frontend

Desde otra terminal:

```powershell
cd C:\Users\Ariel\Documents\proyectos\chat-escolar\frontend
npm run dev
```

Frontend disponible en:

```text
http://localhost:5173/
```

---

## 12. Flujo diario recomendado

1. Abrir VS Code en:

```text
C:\Users\Ariel\Documents\proyectos\chat-escolar
```

2. Abrir terminal backend:

```powershell
cd backend
.venv\Scripts\activate
uvicorn main:app --reload
```

3. Abrir terminal frontend:

```powershell
cd frontend
npm run dev
```

4. Abrir navegador:

```text
http://localhost:5173/
```

---

## 13. Comandos Git frecuentes

Revisar estado:

```powershell
git status
```

Agregar cambios:

```powershell
git add .
```

Crear commit:

```powershell
git commit -m "Mensaje del cambio"
```

Subir a GitHub:

```powershell
git push
```

Ver historial:

```powershell
git log --oneline -5
```

---

## 14. Decisiones técnicas importantes

### 14.1. Gratuito por ahora

No se usará OpenAI API por ahora, porque tiene costo.

La versión actual debe funcionar gratis usando:

- tutor demo local;
- SQLite;
- frontend local;
- backend local;
- contenidos preparados;
- videos curados locales;
- IA local opcional a futuro.

### 14.2. Distribución local gratuita

Se decidió apuntar a una **Versión Local 2**:

- app local gratuita;
- scripts `.bat` para instalar dependencias;
- scripts `.bat` para iniciar backend y frontend;
- pensada para copiar/instalar en otro PC;
- no empaquetar todavía como `.exe`.

Más adelante se crearán scripts como:

- `instalar_dependencias.bat`;
- `iniciar_chat_escolar.bat`;
- `verificar_entorno.bat`.

### 14.3. IA local futura

Se planea agregar Ollama más adelante, no ahora.

La app debe tener en el futuro un selector de motor:

- Tutor demo local;
- IA local Ollama.

Si Ollama no está instalado, la app debe seguir funcionando con el tutor demo.

Para un PC con 12 GB RAM se recomienda probar después modelos pequeños:

- llama3.2:3b;
- qwen2.5:3b;
- gemma 3B/4B.

### 14.4. Base de conocimiento local

El backend reconoce mapeos de carpetas para 1° a 8° básico y materias principales. Estos mapeos están centralizados en `backend/educational_config.py`.

El lector Markdown y `GET /content/search` están funcionando. El tutor demo puede usar estos archivos como apoyo y señalar la fuente local en el frontend.

La búsqueda incluye normalización tolerante para conceptos educativos conocidos, puntuación ponderada, umbral mínimo y validación temática. Solo el estado `local_verified` permite mostrar una fuente. `local_related` puede informar una conexión secundaria sin tratarla como respaldo principal. Los temas externos no se mezclan con carpetas curriculares y las preguntas ambiguas devuelven `clarification_required`.

Estados actuales de procedencia:

- `local_verified`;
- `local_related`;
- `local_low_confidence`;
- `demo_fallback`;
- `clarification_required`;
- `no_local_content`.

`ollama_generated` queda reservado para una integración futura y no está implementado.

`POST /chat/demo` también devuelve `provider` y `ai_context`. Hoy los proveedores reales son `demo` y `local_content`; `ollama` queda reservado como `future_provider` con `ollama_enabled: false`. No hay cliente Ollama ni llamadas a `localhost:11434`.

El curso asociado al perfil no debe sobrescribir el curso activo del selector. El perfil funciona como preferencia inicial o respaldo si el frontend no envía curso; después, `payload.course` representa la decisión activa del usuario. Esto permite que un perfil de 5° básico consulte 6° básico sin que `/chat/demo` vuelva silenciosamente al curso del perfil.

El selector de estudio incorpora **Todos los cursos**. Cuando se usa esa opción, el buscador recorre la base Markdown curricular local por curso y materia, devuelve `effective_course: "Todos los cursos"` y marca el curso real de la fuente en `source_course`. Si en Modo Escolar no aparece una fuente verificada en el curso activo, el backend puede hacer una búsqueda global de respaldo y marcar `found_in_other_course` cuando la fuente pertenece a otro curso. En Modo Explorador se permite buscar globalmente en la base local antes de caer en una respuesta demo.

Los metadatos relevantes para una futura capa Ollama son: `active_course`, `profile_course`, `effective_course`, `source_course`, `source_subject`, `provenance_status`, `used_local_content`, `content_sources`, `related_sources` y `retrieval.searched_courses`. Ollama sigue apagado; cuando se integre, deberá consumir primero estas fuentes locales y no inventar procedencia.

### 14.5. Contexto conversacional por perfil

El tutor conserva una memoria local ligera por `profile_id` y `conversation_id`. Consulta como máximo seis interacciones de la misma conversación, con prioridad para el turno más reciente. Guarda por separado la pregunta original, la pregunta normalizada, la consulta contextual, el tema activo y la confianza de reconstrucción.

Las preguntas de seguimiento se reconstruyen solo cuando existe un tema activo confiable. Los cambios claros de tema descartan el contexto y las preguntas ambiguas sin antecedentes devuelven `clarification_required`. Esta memoria no mezcla perfiles y no reemplaza el texto visible del historial.

Ollama sigue reservado para una etapa futura. El orden previsto es: contenido local confiable, contenido exploratorio local, IA local mediante Ollama y respuesta segura de respaldo.

### 14.6. Eliminación segura de perfiles locales

`DELETE /profiles/{id}` elimina el perfil por su ID interno y borra en la misma transacción solo el historial asociado a ese `profile_id`. Como favoritos, pendientes y contexto conversacional están en `chat_history`, también se eliminan junto con esas filas. No existe una tabla separada de preferencias en esta versión.

La pantalla de selección solicita confirmación con el nombre exacto. Al eliminar el perfil activo, React limpia `localStorage` para el perfil activo y su conversación, borra el estado visual y vuelve al selector. Si no quedan perfiles, se muestra el formulario de creación.

Los cursos sin contenidos verificados no deben presentarse como cubiertos para todos los temas. Si el selector activo no tiene fuente directa, la app puede mostrar una fuente verificada de otro curso, pero debe marcarla como tal.

El Modo Escolar consulta primero contenido curricular del curso y materia activos. El Modo Explorador usa la base local global antes de informar que no hay contenido local y entregar un respaldo demo transparente.

---

## 15. Próximo paso técnico pendiente

El próximo paso que estaba en curso era agregar:

## Videos curados locales

Objetivo:

- crear `backend/data/videos_curados.json`;
- agregar endpoint `GET /videos`;
- mostrar tarjetas de video en frontend;
- no usar YouTube Data API todavía;
- usar videos curados o enlaces de ejemplo;
- mantener todo gratis y local.

Después de videos curados, los siguientes pasos recomendados son:

1. Agregar perfiles locales personalizados.
2. Asociar historial al perfil.
3. Mejorar historial completo.
4. Crear scripts `.bat`.
5. Crear README de instalación local.
6. Probar instalación en otro PC.
7. Crear primer ZIP local de prueba.
8. Más adelante, integrar Ollama.
9. Ampliar la base Markdown a otros cursos cuando sus contenidos estén incorporados y verificados.

---

## 16. Perfiles locales

La app ya permite crear, seleccionar y eliminar perfiles locales con nombre, tipo de usuario y curso asociado.

No debe ser login con contraseña todavía.

El perfil pide:

- nombre;
- tipo de usuario:
  - estudiante;
  - apoderado;
  - docente;
- curso asociado de 1° a 8° básico.

El perfil se guarda localmente y personaliza saludos/respuestas. La eliminación segura usa `DELETE /profiles/{id}` y no borra datos de otros perfiles.

También se quiere preparar un espacio para una mascota futura, con placeholder y globo tipo cómic.

---

## 16.1 Control local de Ollama

La IA local es opcional y su preferencia persistente se guarda en `backend/data/settings.json`. Los modos disponibles son `basic`, `automatic` y `explore_only`. El valor inicial recomendado para equipos modestos es `basic`, con Ollama desactivado y timeout de 25 segundos.

- `basic`: no consulta Ollama; responde con contenido local o fallback educativo.
- `automatic`: puede usar Ollama y vuelve al fallback si falla o supera el timeout.
- `explore_only`: permite Ollama solo en Modo Explorador o Todos los cursos; el modo escolar conserva prioridad local.

Los endpoints `GET /settings`, `PATCH /settings` y `GET /ai/status` permiten ver y ajustar esta configuración sin salir del equipo. La respuesta del chat conserva `provider`, procedencia, tiempo total, `ai_mode_used`, `ollama_attempted` y `ollama_timeout`, sin mostrar razonamiento interno al estudiante.

---

## 17. Prompt pendiente para Codex: videos curados

Crear videos curados locales sin YouTube API.

Temas iniciales:

- hábitat;
- ecosistemas;
- fracciones;
- comprensión lectora;
- Segunda Guerra Mundial;
- tanques;
- agujeros negros;
- naves espaciales.

Crear endpoint:

```text
GET /videos
```

Filtros:

- topic;
- mode;
- subject.

Frontend debe mostrar tarjetas con:

- título;
- tema;
- canal;
- duración;
- revisado;
- botón Abrir video.

---

## 18. Recordatorio importante

Este chat debe mantenerse enfocado en:

- comandos;
- instalación;
- errores técnicos;
- implementación;
- backend;
- frontend;
- Git;
- Codex;
- scripts;
- pruebas locales.

---

## 19. Autoría y versión

Se incorporó autoría centralizada y versión `0.1.0`. La configuración visible del frontend se mantiene en `frontend/src/config/appInfo.js`; los criterios de actualización están documentados en `docs/AUTORIA_Y_VERSIONADO.md`.

Las ideas generales, mejoras, contenidos educativos y preguntas estratégicas se manejarán en otro chat.
