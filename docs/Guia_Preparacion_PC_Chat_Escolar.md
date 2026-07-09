# Chat Escolar - Guia de Preparacion del PC de Desarrollo

## 1. Objetivo de esta guia

Esta guia explica todo lo necesario para preparar un PC nuevo para desarrollar **Chat Escolar**.

El proyecto se realizara en un computador distinto al usado para la aplicacion de YouTube, por lo que conviene instalar y verificar todo desde cero.

Esta guia esta pensada para Windows.

## 2. Que se va a instalar

Herramientas principales:

| Herramienta | Para que sirve |
|---|---|
| Visual Studio Code | Editor de codigo |
| Git | Control de versiones |
| GitHub Desktop opcional | Manejo visual de repositorios |
| Node.js LTS | Frontend con React + Vite |
| Python | Backend con FastAPI |
| Postman opcional | Probar la API |
| Windows Terminal opcional | Consola mas comoda |
| Cuenta GitHub | Guardar el proyecto |
| OpenAI API | Conectar el chatbot con IA |
| Google Cloud / YouTube API | Videos educativos, cuando corresponda |

## 3. Orden recomendado

No instalar todo al azar. Seguir este orden:

1. Crear carpeta de proyectos.
2. Instalar Visual Studio Code.
3. Instalar Git.
4. Instalar Node.js LTS.
5. Instalar Python.
6. Verificar instalaciones.
7. Crear cuenta o revisar GitHub.
8. Crear repositorio.
9. Instalar extensiones de VS Code.
10. Preparar llaves API.
11. Crear estructura inicial del proyecto.

## 4. Crear carpeta de proyectos

En Windows, crear una carpeta principal:

```text
C:\Users\Ariel\Documents\proyectos
```

Dentro de esa carpeta, el proyecto podria quedar asi:

```text
C:\Users\Ariel\Documents\proyectos\chat-escolar
```

Recomendacion:

Usar nombres sin espacios para evitar problemas con comandos.

## 5. Instalar Visual Studio Code

Descargar e instalar:

```text
https://code.visualstudio.com/
```

Durante instalacion, si aparecen opciones, marcar:

- Add to PATH.
- Open with Code.
- Register Code as editor.

Extensiones recomendadas:

- Spanish Language Pack for Visual Studio Code.
- Python.
- Pylance.
- ESLint.
- Prettier.
- GitLens opcional.
- Thunder Client opcional.

## 6. Instalar Git

Descargar:

```text
https://git-scm.com/downloads
```

Durante instalacion, se puede dejar casi todo por defecto.

Recomendado:

- Editor por defecto: Visual Studio Code.
- Terminal: Git Bash o Windows Terminal.

Verificar instalacion:

```bash
git --version
```

Configurar nombre y correo:

```bash
git config --global user.name "Ariel Ponce"
git config --global user.email "TU_CORREO_DE_GITHUB"
```

Verificar configuracion:

```bash
git config --global --list
```

## 7. Instalar Node.js LTS

Descargar la version LTS:

```text
https://nodejs.org/
```

Node.js se usara para:

- React.
- Vite.
- Dependencias del frontend.
- Construir la PWA.

Verificar:

```bash
node -v
npm -v
```

## 8. Instalar Python

Descargar:

```text
https://www.python.org/downloads/
```

Importante durante instalacion:

- Marcar "Add Python to PATH".

Verificar:

```bash
python --version
pip --version
```

Si `python` no funciona, probar:

```bash
py --version
py -m pip --version
```

## 9. Instalar herramientas opcionales utiles

### Postman

Sirve para probar el backend.

```text
https://www.postman.com/downloads/
```

Alternativa simple:

- Thunder Client dentro de VS Code.

### Windows Terminal

Disponible desde Microsoft Store.

No es obligatorio, pero ayuda a trabajar mas comodo.

### GitHub Desktop

Opcional si se quiere manejar Git de forma visual.

```text
https://desktop.github.com/
```

## 10. Crear o preparar cuenta GitHub

Necesario para guardar el codigo.

Pasos:

1. Entrar a GitHub.
2. Crear repositorio nuevo.
3. Nombre recomendado:

```text
chat-escolar
```

4. Elegir privado o publico.

Recomendacion inicial:

- Privado mientras se desarrolla.

## 11. Preparar cuenta OpenAI API

Chat Escolar usara OpenAI API para generar respuestas del tutor.

La documentacion actual de OpenAI recomienda usar la **Responses API** como interfaz principal para generar respuestas y usar herramientas. Tambien existen SDKs oficiales para trabajar desde Python o JavaScript/TypeScript.

Pasos generales:

1. Entrar a la plataforma de OpenAI.
2. Crear o revisar cuenta de desarrollador.
3. Crear una API key.
4. Guardarla de forma segura.
5. No subir la API key a GitHub.

La API key se guardara en un archivo local:

```text
.env
```

Ejemplo:

```env
OPENAI_API_KEY=tu_api_key_aqui
```

Importante:

El archivo `.env` debe estar en `.gitignore`.

## 12. Preparar YouTube Data API

Para videos educativos hay dos caminos:

### Camino recomendado al inicio

Usar una lista curada manual:

```text
contenidos/videos/videos_curados.json
```

Ventaja:

- Mas seguro.
- Mas controlado.
- Menos configuracion inicial.

### Camino posterior

Usar YouTube Data API.

Pasos generales:

1. Crear cuenta en Google Cloud.
2. Crear proyecto.
3. Activar YouTube Data API v3.
4. Crear API key.
5. Restringir la API key.
6. Guardarla en `.env`.

Ejemplo:

```env
YOUTUBE_API_KEY=tu_youtube_api_key_aqui
```

## 13. Crear proyecto frontend

Cuando el PC este listo, se podra crear el frontend con Vite.

Comandos:

```bash
cd C:\Users\Ariel\Documents\proyectos
npm create vite@latest chat-escolar -- --template react
cd chat-escolar
npm install
npm run dev
```

Esto levantara una direccion local similar a:

```text
http://localhost:5173
```

## 14. Crear proyecto backend

Dentro de la carpeta del proyecto:

```bash
mkdir backend
cd backend
python -m venv .venv
```

Activar entorno virtual en Windows:

```bash
.venv\Scripts\activate
```

Instalar dependencias iniciales:

```bash
pip install fastapi uvicorn python-dotenv openai
```

Guardar dependencias:

```bash
pip freeze > requirements.txt
```

Ejecutar backend cuando exista `main.py`:

```bash
uvicorn main:app --reload
```

Direccion local esperada:

```text
http://localhost:8000
```

Documentacion automatica de FastAPI:

```text
http://localhost:8000/docs
```

## 15. Estructura recomendada del proyecto

```text
chat-escolar/
├── README.md
├── docs/
│   ├── contexto_proyecto.md
│   ├── alcance_version_1.md
│   ├── guia_preparacion_pc.md
│   ├── prompt_tutor.md
│   └── roadmap.md
├── frontend/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── contenidos/
│   ├── primero_basico/
│   ├── quinto_basico/
│   ├── sexto_basico/
│   └── modo_explorador/
├── prompts/
│   └── chat_escolar_tutor.md
└── pruebas/
    └── conversaciones_ejemplo.md
```

## 16. Archivo .gitignore recomendado

Crear archivo:

```text
.gitignore
```

Contenido inicial:

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

## 17. Variables de entorno

Archivo local:

```text
backend/.env
```

Contenido esperado:

```env
OPENAI_API_KEY=tu_api_key_aqui
YOUTUBE_API_KEY=tu_youtube_api_key_aqui
APP_ENV=development
```

No subir este archivo a GitHub.

## 18. Verificaciones antes de desarrollar

Ejecutar estos comandos:

```bash
git --version
node -v
npm -v
python --version
pip --version
```

Todo debe responder con una version instalada.

Luego verificar:

```bash
code --version
```

Si `code` no funciona, abrir VS Code y activar el comando desde la paleta:

```text
Shell Command: Install 'code' command in PATH
```

## 19. Extensiones utiles de VS Code

Instalar:

- Spanish Language Pack.
- Python.
- Pylance.
- ESLint.
- Prettier.
- GitLens.
- Thunder Client.

## 20. Preparacion antes de pedir desarrollo en Codex/ChatGPT

Cuando estes en el PC nuevo, tener listo:

1. Carpeta creada.
2. Git instalado.
3. Node instalado.
4. Python instalado.
5. VS Code instalado.
6. Repositorio GitHub creado.
7. API key de OpenAI disponible.
8. Este archivo cargado o disponible.
9. Documento de contexto del proyecto.
10. Documento de alcance Version 1.

## 21. Prompt para iniciar desarrollo en otro chat

Cuando quieras comenzar el desarrollo, puedes usar este mensaje:

```text
Quiero iniciar el desarrollo de Chat Escolar.

Lee estos documentos:
- Chat_Escolar_Contexto_Proyecto.md
- Alcance_Version_1.md
- Guia_Preparacion_PC_Chat_Escolar.md

El proyecto debe ser una Web/PWA con frontend React + Vite y backend Python + FastAPI.

Cursos iniciales:
- 1ro basico
- 5to basico
- 6to basico

Materias:
- Ciencias Naturales
- Matematica
- Lenguaje
- Historia

Debe incluir desde la Version 1:
- Modo Escolar
- Modo Explorador
- Videos educativos
- Tutor paciente
- Lectura facil
- Apoyo para estudiantes con dificultades o TEA
- Interfaz simple, moderna y no infantil

Primero revisa el estado del repositorio y crea la estructura inicial del proyecto.
No avances a conectar la API de OpenAI hasta que la estructura base este funcionando.
```

## 22. Primeros pasos que se pueden avanzar desde el celular

Aunque todavia no estes en el PC, se puede avanzar:

- Definir alcance.
- Definir pantallas.
- Crear prompt interno del tutor.
- Crear contenidos iniciales.
- Crear lista de videos curados.
- Crear roadmap.
- Crear textos de prueba.
- Crear ejemplos de conversaciones.
- Definir estructura del repositorio.

## 23. Proximos archivos recomendados

Despues de esta guia, conviene crear:

1. `Prompt_Chat_Escolar.md`
2. `Diseno_UI_Chat_Escolar.md`
3. `Contenidos_Iniciales_5to_Basico.md`
4. `Modo_Explorador_Rutas.md`
5. `Videos_Curados_Iniciales.md`

