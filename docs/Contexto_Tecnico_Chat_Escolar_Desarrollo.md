# Contexto técnico del proyecto Chat Escolar

Este archivo sirve para mantener ordenado el chat técnico del proyecto **Chat Escolar**.

Este chat debe enfocarse en instalación, configuración, desarrollo, backend, frontend, Git, GitHub, Codex, errores, comandos y preparación de una versión local gratuita.

---

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
│   ├── main.py
│   ├── requirements.txt
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

Ya están integrados archivos Markdown locales para:

- 1° básico;
- 5° básico;
- 6° básico.

El lector Markdown y `GET /content/search` están funcionando. El tutor demo puede usar estos archivos como apoyo y señalar la fuente local en el frontend.

La búsqueda incluye normalización tolerante para conceptos educativos conocidos, puntuación ponderada, umbral mínimo y validación temática. Solo el estado `local_verified` permite mostrar una fuente. Los temas externos no se mezclan con carpetas curriculares y las preguntas ambiguas devuelven `clarification_required`.

Estados actuales de procedencia:

- `local_verified`;
- `local_low_confidence`;
- `demo_fallback`;
- `clarification_required`;
- `no_local_content`.

`ollama_generated` queda reservado para una integración futura y no está implementado.

### 14.5. Contexto conversacional por perfil

El tutor conserva una memoria local ligera por `profile_id` y `conversation_id`. Consulta como máximo seis interacciones de la misma conversación, con prioridad para el turno más reciente. Guarda por separado la pregunta original, la pregunta normalizada, la consulta contextual, el tema activo y la confianza de reconstrucción.

Las preguntas de seguimiento se reconstruyen solo cuando existe un tema activo confiable. Los cambios claros de tema descartan el contexto y las preguntas ambiguas sin antecedentes devuelven `clarification_required`. Esta memoria no mezcla perfiles y no reemplaza el texto visible del historial.

Ollama sigue reservado para una etapa futura. El orden previsto es: contenido local confiable, contenido exploratorio local, IA local mediante Ollama y respuesta segura de respaldo.

### 14.6. Eliminación segura de perfiles locales

`DELETE /profiles/{id}` elimina el perfil por su ID interno y borra en la misma transacción solo el historial asociado a ese `profile_id`. Como favoritos, pendientes y contexto conversacional están en `chat_history`, también se eliminan junto con esas filas. No existe una tabla separada de preferencias en esta versión.

La pantalla de selección solicita confirmación con el nombre exacto. Al eliminar el perfil activo, React limpia `localStorage` para el perfil activo y su conversación, borra el estado visual y vuelve al selector. Si no quedan perfiles, se muestra el formulario de creación.

Los cursos 2°, 3°, 4°, 7° y 8° básico están en preparación y no deben marcarse como disponibles hasta que sus contenidos se incorporen y verifiquen en el repositorio.

El Modo Escolar consulta exclusivamente contenido curricular del curso y materia. El Modo Explorador queda separado y, mientras no exista una colección local específica, informa que el contenido no está disponible y usa un respaldo demo transparente.

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

## 16. Prompt pendiente para Codex: perfiles locales

El usuario quiere agregar perfiles locales con nombre y tipo de usuario.

No debe ser login con contraseña todavía.

Debe pedir:

- nombre;
- tipo de usuario:
  - estudiante;
  - apoderado;
  - docente;
- curso asociado:
  - 1° básico;
  - 5° básico;
  - 6° básico.

Debe guardar perfil local y personalizar saludos/respuestas.

También se quiere preparar un espacio para una mascota futura, con placeholder y globo tipo cómic.

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
