# Plan de continuidad curricular de 1° a 8° básico — Chat Escolar

## Recomendación

Mantener los ocho cursos es recomendable porque permite:

- recuperar prerrequisitos;
- detectar progresión entre cursos;
- adaptar profundidad y vocabulario;
- evitar mezclar niveles;
- construir rutas de refuerzo y avance;
- ofrecer respuestas fuera de nivel con una advertencia clara.

## Estructura común

Cada curso mantiene:

- capítulos modulares por asignatura;
- índices y mapa de cobertura;
- rutas de aprendizaje;
- evaluación diagnóstica y repasos;
- bancos de preguntas, glosarios y tarjetas;
- apoyo TEA y lectura fácil;
- compendios para lectura humana;
- catálogo y fragmentos JSONL para RAG.

## Cambios curriculares importantes

- De 1° a 6° se usa **Lenguaje y Comunicación**.
- En 7° y 8° se usa **Lengua y Literatura**.
- En 7° y 8° Lengua y Literatura incorpora un eje explícito de **Investigación**.
- Matemática de 7° y 8° reorganiza sus ejes respecto de 1° a 6°.
- Ciencias Naturales de 7° y 8° se desarrolla mediante Biología, Física, Química y habilidades científicas.
- La profundidad histórica y ciudadana aumenta y exige análisis de fuentes, perspectivas y procesos.

## Política de recuperación

1. Filtrar siempre por curso.
2. Buscar primero el tema exacto.
3. Si falta comprensión, recuperar un prerrequisito del curso anterior.
4. Si el estudiante domina el tema, ofrecer conexión con el curso siguiente.
5. Señalar claramente cuando la explicación sale del nivel seleccionado.
6. No usar evaluaciones como fuente principal de explicación.
7. No indexar compendios junto con capítulos.

## Próximos pasos técnicos

- Crear un indexador único para `contenidos/`.
- Añadir filtros por curso, asignatura, eje, tipo y dificultad.
- Mantener una colección curricular y colecciones separadas de práctica y evaluación.
- Ejecutar pruebas cruzadas entre cursos.
- Registrar la fuente recuperada en el historial interno.
