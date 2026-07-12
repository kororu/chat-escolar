# Integración con FastAPI, Ollama y RAG — 1° básico

## Flujo sugerido

1. El frontend envía pregunta, curso y modo de apoyo.
2. FastAPI normaliza texto y conserva la pregunta original.
3. Un clasificador identifica asignatura, eje, tema y tipo de respuesta.
4. Se filtran documentos por `curso: primero_basico`.
5. Se recuperan de 2 a 4 fragmentos principales. En primero básico conviene usar menos contexto que en cursos superiores.
6. Ollama responde con una idea central, un ejemplo y una práctica.
7. Un validador revisa longitud, lenguaje, seguridad, números y coherencia.
8. El historial registra archivos usados y apoyo solicitado.

## Directorios iniciales de indexación

- `lenguaje/`
- `matematica/`
- `ciencias_naturales/`
- `historia_geografia/`

## Índices opcionales

- `evaluaciones/`: solo para modo diagnóstico.
- `bancos/`: solo para práctica adicional.
- `apoyo_inclusivo/`: como reglas de estilo y adaptación.

## Excluir

- `compendios/`
- índices Markdown cuando solo duplican títulos;
- `chunks_rag.jsonl` cuando los fragmentos se generan directamente desde Markdown.

## Recuperación pedagógica

- Dar mayor peso al tema exacto y a prerrequisitos.
- Preferir fragmentos con “Respuesta breve”, “Ejemplo explicado” y “Cómo explicarlo”.
- Evitar combinar demasiados ejes en una respuesta.
- En lectoescritura, distinguir sonido, letra, sílaba, palabra, oración y comprensión.
- En matemática, preferir concreto y pictórico antes de símbolo.
- En identidad, familia y seguridad, aplicar privacidad y ejemplos ficticios.

## Registro mínimo

```json
{
  "curso": "primero_basico",
  "pregunta": "¿Cómo formo una decena?",
  "modo": "paso_a_paso",
  "fuentes": ["1b_mat_13_unidades_y_decenas_hasta_20"],
  "apoyos": ["lectura_facil", "ejemplo_concreto"]
}
```
