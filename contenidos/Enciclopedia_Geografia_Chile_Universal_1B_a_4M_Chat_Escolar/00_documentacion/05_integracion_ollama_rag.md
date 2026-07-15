# Integración con Ollama y RAG

## Objetivo

Permitir que Chat Escolar recupere fragmentos geográficos locales y genere respuestas adaptadas.

## Flujo

```text
Pregunta → curso activo → detección de tema → recuperación de fragmentos → respuesta adaptada → validación
```

## Reglas

- Si el estudiante pregunta algo de curso superior, responder adaptando el lenguaje.
- Si faltan fuentes para datos recientes, decirlo.
- No inventar cifras de población, migración, clima reciente o desastres.
- En riesgos, entregar prevención sin alarmismo.
- En conflictos socioambientales, explicar actores, causas y consecuencias.

## Campos útiles

- curso_origen
- apto_desde
- categoria
- palabras_clave
- requiere_fuente_verificada
- alineacion_curricular
