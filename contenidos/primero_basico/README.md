# Enciclopedia de 1° básico — Chat Escolar

Base de conocimiento original, modular e inclusiva para una aplicación local con React, FastAPI y futura IA mediante Ollama.

## Contenido

- **112 capítulos curriculares principales**.
- 38 capítulos de Lenguaje y Comunicación.
- 30 capítulos de Matemática.
- 21 capítulos de Ciencias Naturales.
- 23 capítulos de Historia, Geografía y Ciencias Sociales.
- Bancos de preguntas, glosarios y tarjetas de repaso.
- Diagnósticos y cuatro repasos por asignatura con respuestas.
- Apoyos TEA, lectura fácil, alfabetización inicial y matemática concreta.
- Compendios para lectura humana.
- Catálogo y 2252 fragmentos JSONL para RAG.

## Instalación

Copiar el contenido de esta carpeta en:

```text
chat-escolar/contenidos/primero_basico/
```

La estructura del proyecto debería quedar:

```text
chat-escolar/
├── backend/
├── frontend/
├── docs/
└── contenidos/
    ├── primero_basico/
    ├── quinto_basico/
    └── sexto_basico/
```

## Primera indexación recomendada

Incluir:

- `lenguaje/`
- `matematica/`
- `ciencias_naturales/`
- `historia_geografia/`

Excluir:

- `compendios/`
- `evaluaciones/`
- `bancos/`
- archivos `00_indice_*.md`

Después se pueden construir índices separados para práctica y evaluación.

## Características pedagógicas

- Edad referencial: 6 a 7 años.
- Lenguaje directo y una instrucción principal por vez.
- Alfabetización desde oralidad, sonido, sílaba, palabra, oración y texto.
- Matemática desde concreto, pictórico y simbólico.
- Actividades cortas y materiales cotidianos seguros.
- Privacidad en identidad y familia.
- Respuestas alternativas: selección, dibujo, objetos, oralidad y escritura.
- Adaptación TEA sin infantilización ni reducción automática de expectativas.

## Estado curricular

La alineación fue revisada en el portal oficial Currículum Nacional/MINEDUC el **2026-07-12**. Se cubren los 26 OA de Lenguaje, 20 de Matemática, 12 de Ciencias Naturales y 15 de Historia, Geografía y Ciencias Sociales publicados en las páginas oficiales consultadas.

## Estado del paquete

Versión 1.0 lista para revisión pedagógica humana, integración y pruebas de recuperación.

## Inicio recomendado

Abrir [el índice maestro](00_documentacion/00_indice_maestro.md).
