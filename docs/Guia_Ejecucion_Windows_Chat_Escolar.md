# Guía de ejecución en Windows

Esta guía sirve tanto para el equipo habitual como para preparar Chat Escolar en otro PC. Los scripts usan rutas relativas, por lo que la carpeta del proyecto se puede copiar o clonar en otra ubicación.

## Requisitos

- Windows 10 u 11.
- Git para clonar y actualizar el proyecto.
- Node.js `20.19` o superior compatible con Vite 8; Node incluye npm.
- Python 3 con la opción **Add Python to PATH** activada durante la instalación; también se admite el lanzador `py` de Windows.
- Conexión a Internet solo durante la primera instalación de dependencias o una actualización que agregue paquetes.
- Ollama es opcional. Chat Escolar funciona en modo Básico sin Ollama y sin servicios externos.

## Cómo iniciar Chat Escolar en Windows

### Primer uso

1. Abre la carpeta raíz de Chat Escolar.
2. Ejecuta `scripts\00_verificar_entorno.bat` y revisa que Git, Node, npm y Python indiquen `OK`.
3. Ejecuta `scripts\01_instalar_dependencias.bat`. Este paso crea `backend\.venv` e instala las dependencias del backend y frontend.
4. Ejecuta `iniciar_chat_escolar.bat` desde la raíz.
5. El iniciador abre el backend, el frontend y `http://localhost:5173/` en el navegador.

La primera instalación puede tardar varios minutos. No cierres la ventana mientras `pip install` o `npm install` estén trabajando.

### Uso diario

Después de la primera instalación, ejecuta únicamente `iniciar_chat_escolar.bat`. No es necesario reinstalar dependencias cada día.

Se abrirán dos ventanas:

- **Chat Escolar Backend**, disponible en `http://127.0.0.1:8000`.
- **Chat Escolar Frontend**, disponible en `http://localhost:5173/`.

Si el navegador no se abre, ejecuta `scripts\04_abrir_chat_escolar.bat` o escribe `http://localhost:5173/` manualmente.

## Scripts disponibles

| Script | Función |
| --- | --- |
| `scripts\00_verificar_entorno.bat` | Verifica programas, carpetas, archivos principales, entorno virtual y Ollama opcional. |
| `scripts\01_instalar_dependencias.bat` | Prepara `backend\.venv`, instala `backend\requirements.txt` y ejecuta `npm install`. |
| `scripts\02_iniciar_backend.bat` | Inicia FastAPI/Uvicorn en el puerto 8000. |
| `scripts\03_iniciar_frontend.bat` | Inicia React/Vite en el puerto 5173. |
| `scripts\04_abrir_chat_escolar.bat` | Abre Chat Escolar en el navegador predeterminado. |
| `iniciar_chat_escolar.bat` | Inicia todo para el uso diario. |

## Cómo comprobar que está funcionando

1. Abre `http://127.0.0.1:8000/health`. El backend debe responder sin error.
2. Abre `http://localhost:5173/`. Debe aparecer la pantalla de bienvenida o perfiles.
3. Entra a un perfil existente o usa **Usar demo rápida**.
4. Haz una pregunta sugerida o escribe una pregunta escolar.

## Inicio manual para desarrolladores

Abre una terminal PowerShell en la raíz y ejecuta el backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Abre otra terminal PowerShell en la raíz y ejecuta el frontend:

```powershell
cd frontend
npm run dev -- --host localhost --port 5173 --strictPort
```

## Cómo detener Chat Escolar

Presiona `Ctrl+C` en las ventanas del backend y frontend. También puedes cerrar ambas ventanas. Detener los procesos no elimina perfiles, historial, configuración ni avatares locales.

## Ejecutar en otro PC

1. Instala Git, Node.js y Python según la sección **Requisitos**.
2. Clona el repositorio o copia la carpeta completa del proyecto.
3. Si necesitas conservar los datos de otro equipo, copia también su base de datos local `backend\chat_escolar.db` con la aplicación detenida. Evita reemplazarla si quieres conservar los perfiles que ya existen en el PC nuevo.
4. Repite los pasos de **Primer uso**.
5. Para el uso diario, ejecuta `iniciar_chat_escolar.bat`.

No copies `backend\.venv` ni `frontend\node_modules` entre equipos: el instalador los crea para el PC actual.

## Actualizar desde GitHub

Con Chat Escolar detenido, abre PowerShell en la raíz del proyecto:

```powershell
git status
git pull
```

Si `git status` muestra cambios propios, guárdalos antes de actualizar para evitar conflictos. Después de `git pull`, ejecuta `scripts\01_instalar_dependencias.bat` si cambiaron `backend\requirements.txt`, `frontend\package.json` o `frontend\package-lock.json`.

## Ollama opcional y modo Básico

Ollama no es un requisito. Sin Ollama, selecciona **Básico** en la configuración de IA local: Chat Escolar responde con contenidos locales y su fallback educativo. Perfiles, historial, búsqueda local y Nexo siguen disponibles.

Si Ollama ya está instalado y configurado, `scripts\00_verificar_entorno.bat` lo mostrará como disponible. El instalador no descarga modelos ni cambia la configuración de Ollama.

## Problemas comunes

- **Node o npm no encontrado:** instala una versión compatible de Node.js, cierra las terminales abiertas y vuelve a ejecutar la verificación.
- **Python no encontrado:** reinstala Python con **Add Python to PATH** o habilita el lanzador `py`; luego abre una terminal nueva.
- **Falta `backend\.venv` o `frontend\node_modules`:** ejecuta `scripts\01_instalar_dependencias.bat`.
- **`pip install` o `npm install` falló:** revisa la conexión, el mensaje completo y el espacio disponible; vuelve a ejecutar el instalador.
- **Puerto 8000 ocupado:** cierra otra ventana de Uvicorn/Python que esté usando el backend y vuelve a iniciar.
- **Puerto 5173 ocupado:** cierra otra ventana de Vite/Node y vuelve a iniciar.
- **El navegador abrió antes que Vite:** espera unos segundos y actualiza la página.
- **El backend no responde:** comprueba `http://127.0.0.1:8000/health` y revisa el mensaje de la ventana Backend.
- **Ollama no detectado:** continúa en modo Básico; este aviso no impide usar la aplicación.
