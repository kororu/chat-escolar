# Integración con Ollama y RAG

## Recuperación recomendada

1. Filtrar primero por curso.
2. Priorizar `curricular_directa` o `formacion_general`.
3. Recuperar 4 a 7 fragmentos por consulta.
4. Añadir un fragmento transversal solo cuando ayude a explicar una habilidad o concepto.
5. Usar bancos y evaluaciones en colecciones separadas.
6. Excluir compendios de la colección principal.

## Metadatos útiles

- `course_slug`
- `alignment`
- `period`
- `topic_key`
- `sensitive`
- `oa`

## Regla de respuesta

El modelo debe indicar cuando un contenido es puente o ampliación y nunca afirmar que forma una unidad obligatoria del curso si no lo es.
