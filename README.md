# Chat Escolar

Aplicación educativa local para enseñanza básica chilena. Ofrece un tutor de chat llamado Nexo, contenidos Markdown de 1.º a 8.º básico, perfiles e historial guardados en el equipo.

## Objetivo y público

Ayudar a estudiantes, apoderados y docentes a estudiar con explicaciones claras, lectura fácil y apoyo local. Está pensada para funcionar sin servicios pagados: Ollama es opcional y existe un modo básico sin IA local.

## Características principales

- Frontend React/Vite y backend FastAPI con SQLite local.
- Perfiles, avatar opcional, historial, favoritos y pendientes.
- Materia automática: Ciencias Naturales, Matemática, Lenguaje e Historia.
- Búsqueda y contenido curricular local de 1.º a 8.º básico.
- Respuestas pedagógicas adaptadas por curso, Nexo, preguntas sugeridas y perfil demo.
- Modo básico y control opcional de IA local con Ollama.

## Inicio rápido en Windows

Requisitos: Git, Node.js con npm y Python. Ollama es opcional.

1. Ejecuta `scripts\00_verificar_entorno.bat`.
2. En el primer uso, ejecuta `scripts\01_instalar_dependencias.bat`.
3. Ejecuta `iniciar_chat_escolar.bat` desde la raíz.
4. Si el navegador no se abre, visita `http://localhost:5173/`.

Para el uso diario, vuelve a ejecutar `iniciar_chat_escolar.bat`. El backend queda en `http://127.0.0.1:8000`; su estado se consulta en `/health` y su documentación interactiva está en `/docs`.

## Ejecución manual para desarrollo

En dos terminales, desde la raíz del proyecto:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm run dev -- --host localhost --port 5173 --strictPort
```

## Ollama: opcional

Sin Ollama, el modo **Básico** usa contenido local y respuestas de respaldo. Con Ollama, la tarjeta **IA local** permite usar el modelo configurado; el valor inicial es `qwen3.5:2b` y se puede instalar manualmente:

```powershell
ollama pull qwen3.5:2b
ollama list
```

La app conserva un fallback local si Ollama no está instalado, apagado o tarda demasiado.

## Estructura general

```text
backend/     API FastAPI, SQLite, búsqueda, respuestas y Ollama opcional
frontend/    interfaz React/Vite, Nexo y componentes de chat
contenidos/  base curricular local Markdown, 1.º a 8.º básico
scripts/     verificación, instalación e inicio para Windows
docs/        guías funcionales, técnicas, UX y planificación
```

## Estado y roadmap

La versión visible actual es `0.1.0`; el proyecto se estima en torno al 85 % hacia 1.0. Actualmente se ejecuta con scripts `.bat` o comandos de desarrollo. La meta 1.0 contempla, pero aún no incluye, el instalador Windows `ChatEscolar_Setup.exe`.

Consulta [PROJECT_STATUS.md](PROJECT_STATUS.md), [docs/ROADMAP_1_0.md](docs/ROADMAP_1_0.md) y la [guía de usuario](docs/GUIA_USUARIO_FINAL.md).

## Documentación

- [Arquitectura técnica](docs/ARQUITECTURA_TECNICA.md)
- [Guía para desarrolladores](docs/GUIA_DESARROLLADOR.md)
- [Mapa de código](docs/MAPA_CODIGO.md)
- [Guía UX/UI](docs/UX_UI_CHAT_ESCOLAR.md)
- [Plan del instalador 1.0](docs/INSTALADOR_WINDOWS_1_0.md)
- [Changelog del proyecto](docs/CHANGELOG_PROYECTO.md)

## Autoría y licencia

Autor: **Ariel Ponce**. Año: 2026. Licencia pendiente; la autoría no sustituye una licencia formal.
