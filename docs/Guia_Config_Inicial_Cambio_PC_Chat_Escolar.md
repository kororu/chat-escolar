# Chat Escolar - Guia de Configuracion Inicial para Cambiar de PC

## 1. Objetivo

Esta guia sirve para preparar un PC nuevo y continuar el proyecto **Chat Escolar** desde cero.

Incluye los pasos realizados durante la configuracion inicial:

- Instalar herramientas.
- Verificar Git, Node, npm, Python, pip y VS Code.
- Corregir bloqueo de npm en PowerShell.
- Crear carpeta del proyecto.
- Inicializar Git.
- Crear frontend React + Vite.
- Crear backend FastAPI.
- Conectar con GitHub.
- Agregar documentacion base.
- Ejecutar frontend y backend localmente.

Esta guia esta pensada para Windows y PowerShell.

## 2. Herramientas necesarias

Instalar:

| Herramienta | Uso |
|---|---|
| Visual Studio Code | Editor de codigo |
| Git for Windows | Control de versiones y GitHub |
| Node.js LTS | Frontend React + Vite |
| npm | Gestor de paquetes de Node |
| Python | Backend FastAPI |
| pip | Gestor de paquetes de Python |
| Codex en VS Code | Ayuda para desarrollo paso a paso |

Links oficiales:

- Visual Studio Code: https://code.visualstudio.com/
- Git: https://git-scm.com/download/win
- Node.js: https://nodejs.org/
- Python: https://www.python.org/downloads/

## 3. Verificar instalaciones

Abrir PowerShell y ejecutar:

```powershell
git --version
node -v
npm -v
python --version
pip --version
code --version
```

Resultado esperado:

- Git debe mostrar version.
- Node debe mostrar version.
- npm debe mostrar version.
- Python debe mostrar version.
- pip debe mostrar version.
- code debe mostrar version de VS Code.

## 4. Problema comun: npm bloqueado en PowerShell

Si al ejecutar:

```powershell
npm -v
```

aparece un error parecido a:

```text
No se puede cargar el archivo C:\Program Files\nodejs\npm.ps1 porque la ejecucion de scripts esta deshabilitada en este sistema.
```

Ejecutar:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Cuando pregunte confirmacion, escribir:

```text
S
```

Cerrar PowerShell, abrirlo de nuevo y probar:

```powershell
npm -v
```

Alternativa temporal:

```powershell
npm.cmd -v
```

## 5. Configurar Git local

Revisar configuracion:

```powershell
git config --global --list
```

Si no aparece nombre y correo, configurar:

```powershell
git config --global user.name "Ariel Ponce"
git config --global user.email "arielignacio.ponce@gmail.com"
```

Verificar:

```powershell
git config --global user.name
git config --global user.email
```

Nota:

Esto firma los commits localmente. No significa necesariamente que el proyecto ya este subido a GitHub.

## 6. Crear carpeta del proyecto

Ejecutar:

```powershell
cd $env:USERPROFILE\Documents
mkdir proyectos
cd proyectos
mkdir chat-escolar
cd chat-escolar
```

Verificar ruta:

```powershell
pwd
```

Ruta esperada:

```text
C:\Users\Ariel\Documents\proyectos\chat-escolar
```

Abrir VS Code:

```powershell
code .
```

## 7. Inicializar Git

Desde la raiz del proyecto:

```powershell
git init
git branch -M main
```

Crear README:

```powershell
echo "# Chat Escolar" > README.md
```

Crear `.gitignore`:

```powershell
notepad .gitignore
```

Pegar:

```gitignore
node_modules/
dist/
.venv/
__pycache__/
*.pyc
.env
.env.local
.DS_Store
```

Guardar y cerrar.

Revisar:

```powershell
git status
```

## 8. Crear frontend React + Vite

Desde la raiz:

```powershell
npm create vite@latest frontend -- --template react
```

Si pregunta:

```text
Which linter to use?
```

Elegir:

```text
ESLint
```

Entrar al frontend:

```powershell
cd frontend
npm install
```

Ejecutar:

```powershell
npm run dev
```

URL esperada:

```text
http://localhost:5173/
```

Para detener:

```text
Ctrl + C
```

## 9. Crear backend FastAPI

Abrir otra terminal y volver a la raiz:

```powershell
cd C:\Users\Ariel\Documents\proyectos\chat-escolar
```

Crear backend:

```powershell
mkdir backend
cd backend
python -m venv .venv
```

Activar entorno virtual:

```powershell
.venv\Scripts\activate
```

Debe aparecer algo como:

```text
(.venv) PS C:\Users\Ariel\Documents\proyectos\chat-escolar\backend>
```

Instalar dependencias:

```powershell
pip install fastapi uvicorn python-dotenv openai
```

Guardar dependencias:

```powershell
pip freeze > requirements.txt
```

## 10. Crear backend inicial

Desde:

```text
C:\Users\Ariel\Documents\proyectos\chat-escolar\backend
```

Crear archivo:

```powershell
notepad main.py
```

Pegar:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Chat Escolar API",
    description="Backend inicial para Chat Escolar",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Chat Escolar API funcionando",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "chat-escolar-backend",
    }
```

Ejecutar:

```powershell
uvicorn main:app --reload
```

URLs esperadas:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

La primera debe mostrar JSON:

```json
{
  "message": "Chat Escolar API funcionando",
  "version": "0.1.0"
}
```

La segunda debe mostrar la documentacion automatica de FastAPI.

## 11. Primer commit base

Desde la raiz:

```powershell
cd C:\Users\Ariel\Documents\proyectos\chat-escolar
git status
git add .
git commit -m "Inicializa estructura base de Chat Escolar"
```

Revisar:

```powershell
git status
```

Debe mostrar:

```text
nothing to commit, working tree clean
```

## 12. Conectar con GitHub

Crear un repositorio en GitHub llamado:

```text
chat-escolar
```

Recomendacion inicial:

- Privado.
- No crear README.
- No crear `.gitignore`.
- No agregar licencia.

Configurar remoto:

```powershell
git remote add origin https://github.com/kororu/chat-escolar.git
```

Si por error quedo como `TU_USUARIO`, corregir:

```powershell
git remote set-url origin https://github.com/kororu/chat-escolar.git
```

Verificar:

```powershell
git remote -v
```

Debe mostrar:

```text
origin  https://github.com/kororu/chat-escolar.git (fetch)
origin  https://github.com/kororu/chat-escolar.git (push)
```

Subir:

```powershell
git push -u origin main
```

## 13. Crear estructura documental

Desde la raiz:

```powershell
mkdir docs
mkdir prompts
mkdir contenidos
mkdir contenidos\primero_basico
mkdir contenidos\quinto_basico
mkdir contenidos\sexto_basico
mkdir contenidos\modo_explorador
mkdir pruebas
```

Estructura esperada:

```text
chat-escolar/
├── backend/
├── frontend/
├── docs/
├── prompts/
├── contenidos/
│   ├── primero_basico/
│   ├── quinto_basico/
│   ├── sexto_basico/
│   └── modo_explorador/
├── pruebas/
├── README.md
└── .gitignore
```

## 14. Agregar documentos base

Copiar los siguientes archivos dentro de:

```text
C:\Users\Ariel\Documents\proyectos\chat-escolar\docs
```

Archivos:

```text
Alcance_Version_1.md
Chat_Escolar_Contexto_Proyecto.md
Contenidos_Iniciales_5to_Basico.md
Diseno_UI_Chat_Escolar.md
Guia_Preparacion_PC_Chat_Escolar.md
Historial_Chat_Escolar.md
Modo_Explorador_Rutas.md
Prompt_Chat_Escolar.md
Proximos_Pasos_Chat_Escolar.md
Videos_Curados_Iniciales.md
```

Verificar:

```powershell
dir docs
git status
```

Commit:

```powershell
git add docs
git commit -m "Agrega documentacion base de Chat Escolar"
git push
```

Verificar historial:

```powershell
git log --oneline -5
```

Debe mostrar algo parecido a:

```text
Agrega documentacion base de Chat Escolar
Inicializa estructura base de Chat Escolar
```

## 15. Como retomar el proyecto en otro PC si ya existe en GitHub

Si el repositorio ya esta subido a GitHub, en un PC nuevo se recomienda clonar en vez de crear todo manualmente.

Ir a la carpeta de proyectos:

```powershell
cd $env:USERPROFILE\Documents
mkdir proyectos
cd proyectos
```

Clonar:

```powershell
git clone https://github.com/kororu/chat-escolar.git
cd chat-escolar
```

Instalar frontend:

```powershell
cd frontend
npm install
```

Ejecutar frontend:

```powershell
npm run dev
```

En otra terminal, instalar backend:

```powershell
cd C:\Users\Ariel\Documents\proyectos\chat-escolar\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 16. Variables de entorno futuras

Cuando se conecte OpenAI API, crear:

```text
backend\.env
```

Ejemplo:

```env
OPENAI_API_KEY=tu_api_key_aqui
YOUTUBE_API_KEY=tu_youtube_api_key_aqui
APP_ENV=development
```

Importante:

El archivo `.env` no debe subirse a GitHub.

Ya esta protegido por `.gitignore`.

## 17. Comandos rapidos de uso diario

### Levantar frontend

```powershell
cd C:\Users\Ariel\Documents\proyectos\chat-escolar\frontend
npm run dev
```

### Levantar backend

```powershell
cd C:\Users\Ariel\Documents\proyectos\chat-escolar\backend
.venv\Scripts\activate
uvicorn main:app --reload
```

### Ver estado Git

```powershell
cd C:\Users\Ariel\Documents\proyectos\chat-escolar
git status
```

### Guardar cambios

```powershell
git add .
git commit -m "Mensaje del cambio"
git push
```

## 18. Validacion final del entorno

El PC esta listo si:

- `git --version` funciona.
- `node -v` funciona.
- `npm -v` funciona.
- `python --version` funciona.
- `pip --version` funciona.
- `code --version` funciona.
- `npm run dev` abre `http://localhost:5173/`.
- `uvicorn main:app --reload` abre `http://127.0.0.1:8000`.
- `git status` queda limpio despues de commits.
- `git push` sube cambios a GitHub.

## 19. Prompt para usar esta guia en otro chat

```text
Estoy cambiando de PC y quiero continuar el proyecto Chat Escolar.

Lee el archivo Guia_Config_Inicial_Cambio_PC_Chat_Escolar.md y guiame paso a paso.

No avances al siguiente paso hasta que confirme el resultado del paso actual.

El proyecto usa:
- React + Vite en frontend.
- Python + FastAPI en backend.
- GitHub como repositorio.
- Documentacion en carpeta docs.

Quiero dejar el entorno funcionando igual que antes.
```

