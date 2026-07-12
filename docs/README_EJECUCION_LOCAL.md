# Ejecución local de Chat Escolar en Windows

## ¿Qué es Chat Escolar?

Chat Escolar es una aplicación educativa que funciona de manera local. Incluye un tutor demostrativo, perfiles, historial por usuario y videos educativos curados. La versión actual es gratuita y no usa la API de OpenAI.

Los perfiles y el historial se guardan en una base SQLite local dentro de `backend/chat_escolar.db`. Este archivo contiene datos locales y no debe subirse a GitHub.

## Programas necesarios

Antes de comenzar, instala:

- Git.
- Node.js, que también instala npm.
- Python.
- Visual Studio Code, opcional pero recomendado para editar el proyecto.

Durante la instalación de Python en Windows, activa la opción **Add Python to PATH**.

## 1. Verificar el entorno

Desde la carpeta raíz del proyecto, abre:

```bat
scripts\verificar_entorno.bat
```

El script mostrará las versiones disponibles de Git, Node.js, npm, Python, pip y VS Code. Si falta una herramienta, mostrará un mensaje claro.

## 2. Instalar las dependencias

Ejecuta:

```bat
scripts\instalar_dependencias.bat
```

Este proceso:

1. Instala las dependencias existentes de `frontend/package.json`.
2. Crea `backend/.venv` si todavía no existe.
3. Instala las dependencias existentes de `backend/requirements.txt`.

El script no borra ni reemplaza `backend/chat_escolar.db`.

## 3. Iniciar Chat Escolar

Ejecuta:

```bat
scripts\iniciar_chat_escolar.bat
```

Se abrirán dos ventanas: una para el backend y otra para el frontend. Después de unos segundos se abrirá el navegador.

También puedes iniciar cada parte por separado:

```bat
scripts\iniciar_backend.bat
scripts\iniciar_frontend.bat
```

## Direcciones locales

- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000
- Documentación de la API: http://127.0.0.1:8000/docs

## Cómo detener la aplicación

En las ventanas del backend y frontend, presiona `Ctrl + C`. También puedes detener la aplicación cerrando ambas ventanas.

Esto no borra los perfiles, el historial ni la base SQLite.

## Solución de problemas

### npm falla por la política de PowerShell

Abre PowerShell como tu usuario y ejecuta:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Confirma el cambio cuando PowerShell lo solicite. Como alternativa, ejecuta los archivos `.bat` desde el Explorador de archivos o usa `npm.cmd` desde PowerShell.

### Python no se reconoce

1. Instala Python desde su instalador oficial.
2. Activa **Add Python to PATH** durante la instalación.
3. Cierra y vuelve a abrir la terminal.
4. Ejecuta `python --version` para comprobarlo.

Si Python ya estaba instalado, vuelve a ejecutar el instalador y habilita su integración con `PATH`.

### Node.js o npm no se reconocen

1. Instala la versión estable de Node.js.
2. Cierra y vuelve a abrir la terminal.
3. Comprueba con `node --version` y `npm --version`.
4. Vuelve a ejecutar `scripts\instalar_dependencias.bat`.

### El backend no conecta

1. Confirma que la ventana **Backend Chat Escolar** sigue abierta.
2. Revisa que muestre `http://127.0.0.1:8000`.
3. Abre http://127.0.0.1:8000/health en el navegador.
4. Si falta `.venv`, ejecuta `scripts\instalar_dependencias.bat`.
5. Si el puerto 8000 está ocupado, cierra otra instancia del backend y vuelve a intentarlo.

### El frontend no abre

1. Confirma que la ventana **Frontend Chat Escolar** sigue abierta.
2. Abre manualmente http://localhost:5173.
3. Si falta `node_modules`, ejecuta `scripts\instalar_dependencias.bat`.
4. Si el puerto 5173 está ocupado, cierra otra instancia de Vite y vuelve a intentarlo.
5. Si la página aparece antes que el servidor, espera unos segundos y recárgala.

## Privacidad y funcionamiento local

Chat Escolar funciona localmente y de forma gratuita. Por ahora no se conecta a OpenAI API ni requiere servicios pagados. La información de perfiles e historial permanece en la base SQLite del equipo.

## Contenidos educativos locales

La aplicación también puede apoyar sus respuestas con archivos Markdown guardados en `contenidos/`. El backend busca automáticamente material relacionado con el curso, la materia y la pregunta, sin enviar información a servicios externos.

Consulta [README_CONTENIDOS_LOCALES.md](README_CONTENIDOS_LOCALES.md) para conocer la estructura, agregar nuevos contenidos y probar el buscador.
