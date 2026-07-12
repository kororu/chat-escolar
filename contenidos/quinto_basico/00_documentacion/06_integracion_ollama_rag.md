# Integración recomendada con Ollama y RAG

## Objetivo

Recuperar fragmentos pertinentes antes de pedir al modelo que redacte. Ollama genera; la base Markdown aporta contenido pedagógico controlado.

## Flujo

```text
React/Vite
  → POST /api/chat
FastAPI
  → valida curso, modo y pregunta
Clasificador
  → asignatura, tema, intención, dificultad
Recuperador
  → búsqueda híbrida por metadatos + texto/embeddings
Reranker opcional
  → selecciona fragmentos
Ollama
  → genera respuesta siguiendo prompt
Validador
  → controla curso, longitud, seguridad y fuentes
Historial local
  → guarda pregunta y rutas usadas
```

## Qué indexar

Indexar:
- capítulos `.md` de las cuatro asignaturas;
- apoyos inclusivos cuando la consulta solicite adaptación;
- bancos y evaluaciones en colecciones separadas.

No indexar en la misma colección:
- `compendios/` junto con capítulos;
- manifiestos, hashes o documentación técnica como si fueran materia;
- respuestas de evaluaciones cuando el modo sea evaluación sin retroalimentación.

## Fragmentación

- Cortar por encabezado `##`.
- Mantener entre 250 y 700 palabras por fragmento como punto inicial de prueba.
- Solapamiento de 40 a 80 palabras solo cuando una definición continúe.
- No separar pregunta de respuesta en bancos.
- Conservar metadatos: id, curso, asignatura, eje, tema, OA, sección, ruta y versión.

## Recuperación híbrida

1. Filtro obligatorio `curso=quinto_basico`.
2. Clasificación de asignatura.
3. Coincidencia léxica para términos exactos y OA.
4. Embeddings para preguntas en lenguaje natural.
5. Reranking por título, palabras clave y sección.
6. Top-k inicial sugerido: 8; entregar al modelo 3–5 fragmentos no redundantes.

## Modelos y memoria

La elección exacta depende del PC. Para equipos con memoria limitada conviene un modelo instruccional cuantizado y un modelo de embeddings pequeño. No se fija un nombre en esta base, porque disponibilidad y rendimiento cambian. Se debe medir calidad en español, RAM, latencia y obediencia al contexto.

## Prevención de alucinaciones

- Prompt: responder solo con fragmentos cuando la pregunta es curricular.
- Si falta contenido: indicar límite y sugerir categoría de búsqueda.
- No inventar OA, fechas, fuentes, resultados o reglas.
- Conservar rutas recuperadas para auditoría.
- Ejecutar pruebas de recuperación antes de evaluar redacción.

## Ejemplo de solicitud interna

```json
{
  "pregunta": "¿Por qué no se suman los denominadores?",
  "curso": "quinto_basico",
  "modo": "paso_a_paso",
  "perfil_apoyo": {
    "lectura_facil": true,
    "cantidad_ejercicios": 1
  }
}
```

## Respuesta interna sugerida

```json
{
  "respuesta": "...",
  "tema": "Adición y sustracción de fracciones",
  "archivos_fuente": ["5b_mat_09_adicion_y_sustraccion_de_fracciones"],
  "modo": "paso_a_paso",
  "requiere_revision": false
}
```
