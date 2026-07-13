# Guía de ejecución en Windows

## Requisitos

Instala Git, Node.js (incluye npm) y Python con la opción **Add Python to PATH**. Ollama es opcional: Chat Escolar funciona en modo básico si no está instalado.

## Primer uso

1. Abre la carpeta del proyecto.
2. Ejecuta `scripts\00_verificar_entorno.bat`.
3. Ejecuta `scripts\01_instalar_dependencias.bat`.
4. Ejecuta `iniciar_chat_escolar.bat` desde la raíz.

El iniciador abre dos ventanas: backend en `http://127.0.0.1:8000` y frontend en `http://localhost:5173`. Después abre el navegador.

## Uso diario

Después de la primera instalación basta ejecutar `iniciar_chat_escolar.bat`. Para abrir una página ya iniciada también está `scripts\04_abrir_chat_escolar.bat`.

Para detener la aplicación, presiona `Ctrl + C` en las ventanas de Backend y Frontend o ciérralas. Esto no elimina perfiles, historial ni avatares locales.

## Problemas comunes

- Si falta `.venv` o `node_modules`, ejecuta `scripts\01_instalar_dependencias.bat`.
- Si el backend no responde, abre `http://127.0.0.1:8000/health` y comprueba que su ventana siga abierta.
- Si un puerto está ocupado, cierra otra instancia de Vite o Uvicorn y vuelve a iniciar.
- Si Ollama no está instalado, continúa en modo Básico; no es un error.

## Cambio de PC y actualización

Copia o clona la carpeta del proyecto, repite el **Primer uso** y conserva `backend/chat_escolar.db` si quieres llevar perfiles e historial. Para actualizar desde GitHub, usa `git pull` dentro de la carpeta y después ejecuta de nuevo `scripts\01_instalar_dependencias.bat` si cambió el proyecto.
