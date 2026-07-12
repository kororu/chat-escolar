# Integración con FastAPI, Ollama y RAG

## Flujo

1. Recibir pregunta, curso y modo.
2. Filtrar `curso=septimo_basico`.
3. Clasificar asignatura y eje.
4. Buscar fragmentos semánticos y por palabras clave.
5. Recuperar entre 3 y 6 fragmentos.
6. Generar respuesta usando solo evidencia suficiente.
7. Registrar archivos y fragmentos usados.

## Reglas de recuperación

- Priorizar capítulos principales.
- Aplicar filtro estricto de curso.
- Usar bancos solo en modo práctica.
- Usar evaluaciones solo en modo diagnóstico o repaso.
- Excluir compendios.
- Ante baja confianza, indicar que falta información y no inventar.

## Metadatos sugeridos

`id`, `curso`, `asignatura`, `eje`, `tema`, `tipo`, `ruta`, `seccion`, `fecha_verificacion`.
