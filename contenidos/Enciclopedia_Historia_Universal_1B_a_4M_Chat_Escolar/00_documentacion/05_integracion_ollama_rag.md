# Integración con FastAPI, Ollama y RAG

## Flujo

1. Recibir pregunta, curso y modo de respuesta.
2. Clasificar colección: curricular general, Historia Universal o Historia de Chile.
3. Filtrar por curso y tipo de alineación.
4. Recuperar entre 3 y 6 fragmentos.
5. Priorizar respuesta breve, explicación, ejemplo y práctica.
6. Validar nivel, sensibilidad y respaldo documental.
7. Registrar ids de archivos utilizados.

## Metadatos útiles

- `coleccion`
- `curso`
- `tipo_alineacion`
- `periodo`
- `tema`
- `tema_sensible`
- `palabras_clave`

## Reglas

- No enviar toda la enciclopedia al modelo.
- No mezclar compendios con capítulos modulares.
- No presentar ampliaciones como OA obligatorio.
- No inventar fechas, citas ni consensos.
- En temas sensibles, recuperar también la guía de tratamiento inclusivo.
