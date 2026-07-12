# Integración con FastAPI, Ollama y RAG

## Flujo

1. El frontend envía pregunta, curso y modo de respuesta.
2. FastAPI clasifica asignatura, tema e intención.
3. Se filtran documentos por `curso: sexto_basico` y asignatura.
4. El buscador combina coincidencia léxica y embeddings.
5. Se recuperan 3 a 6 fragmentos no duplicados.
6. Ollama responde usando solo contexto recuperado y conocimientos generales seguros.
7. Un validador comprueba curso, unidades, OA, seguridad y formato.
8. Se registra pregunta, archivos usados y retroalimentación.

## Directorios para primera indexación

- `lenguaje/`
- `matematica/`
- `ciencias_naturales/`
- `historia_geografia/`

Excluir:

- `compendios/`
- `00_documentacion/chunks_rag.jsonl` si se generan fragmentos directamente desde Markdown.

## Filtros mínimos

`curso`, `asignatura`, `eje`, `tema`, `oa_relacionados`, `tipo` y `version`.

## Seguridad

En salud, pubertad, drogas, violencia, derechos o normativa actual, el modelo debe reconocer límites, evitar diagnósticos y derivar a un adulto o fuente vigente cuando corresponda.
