# Chat Escolar - Proximos Pasos

## 1. Estado actual

Ya estan definidas las decisiones principales:

| Punto | Decision |
|---|---|
| Nombre | Chat Escolar |
| Plataforma inicial | Web/PWA |
| Cursos V1 | 1ro, 5to y 6to basico |
| Materias | Ciencias Naturales, Matematica, Lenguaje e Historia |
| Modo Escolar | Si |
| Modo Explorador | Si |
| Videos | Si, desde V1 |
| Historial | Si, desde V1 |
| Enfoque TEA / lectura facil | Si |
| Interfaz | Simple, moderna y no infantil |
| PC de desarrollo | Sera un PC distinto |

## 2. Archivos base del proyecto

Documentos creados o recomendados:

- `Chat_Escolar_Contexto_Proyecto.md`
- `Alcance_Version_1.md`
- `Guia_Preparacion_PC_Chat_Escolar.md`
- `Prompt_Chat_Escolar.md`
- `Diseno_UI_Chat_Escolar.md`
- `Contenidos_Iniciales_5to_Basico.md`
- `Modo_Explorador_Rutas.md`
- `Videos_Curados_Iniciales.md`
- `Historial_Chat_Escolar.md`
- `Proximos_Pasos_Chat_Escolar.md`

## 3. Lo que se puede avanzar desde el celular

Antes de usar el PC se puede avanzar:

1. Revisar documentos.
2. Ajustar alcance.
3. Agregar intereses del estudiante.
4. Definir mas contenidos.
5. Crear preguntas de practica.
6. Crear lista de videos sugeridos.
7. Refinar el prompt del tutor.
8. Definir el diseno de pantallas.

## 4. Lo que se hara en el PC nuevo

Cuando estes en el PC:

1. Instalar herramientas.
2. Crear carpeta del proyecto.
3. Crear repositorio GitHub.
4. Crear frontend React + Vite.
5. Crear backend FastAPI.
6. Crear base SQLite.
7. Crear pantallas.
8. Crear endpoints.
9. Conectar OpenAI API.
10. Agregar videos curados.
11. Agregar historial.
12. Probar con preguntas reales.

## 5. Orden tecnico recomendado

### Fase 1: Preparacion

- Instalar VS Code.
- Instalar Git.
- Instalar Node.js LTS.
- Instalar Python.
- Crear repositorio.

### Fase 2: Estructura

- Crear carpetas.
- Crear README.
- Crear `.gitignore`.
- Crear frontend.
- Crear backend.

### Fase 3: Prototipo sin IA

- Pantalla inicio.
- Perfil estudiante.
- Selector curso.
- Selector modo.
- Chat simulado.
- Historial simulado.
- Videos desde lista local.

### Fase 4: Backend

- API de chat.
- API de historial.
- API de contenidos.
- API de videos curados.

### Fase 5: IA

- Agregar `.env`.
- Conectar OpenAI API.
- Usar prompt interno.
- Probar respuestas por curso.

### Fase 6: Pruebas reales

Probar con:

- Que es un habitat?
- No entiendo fracciones.
- Que fue la Segunda Guerra Mundial?
- Que es un tanque Tiger?
- Que es un agujero negro?
- Hazme una pregunta de ecosistemas.

## 6. Prompt para iniciar desarrollo

Cuando estes listo en el PC, usar:

```text
Quiero iniciar el desarrollo de Chat Escolar.

Lee estos documentos:
- Chat_Escolar_Contexto_Proyecto.md
- Alcance_Version_1.md
- Guia_Preparacion_PC_Chat_Escolar.md
- Prompt_Chat_Escolar.md
- Diseno_UI_Chat_Escolar.md
- Historial_Chat_Escolar.md
- Modo_Explorador_Rutas.md
- Videos_Curados_Iniciales.md
- Contenidos_Iniciales_5to_Basico.md

Primero crea la estructura base del proyecto Web/PWA con React + Vite y backend FastAPI.

No conectes todavia la API de OpenAI hasta que el frontend, backend e historial simulado funcionen localmente.
```

## 7. Primera meta realista

La primera meta tecnica debe ser:

```text
Tener una app local que permita:
- Elegir perfil.
- Elegir curso.
- Elegir modo.
- Escribir una pregunta.
- Recibir una respuesta simulada.
- Guardar la pregunta en historial.
- Ver videos curados desde una lista local.
```

Despues de eso se conecta la IA real.

