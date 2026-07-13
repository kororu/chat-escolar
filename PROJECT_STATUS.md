# Estado del proyecto: Chat Escolar

Actualizado: 13 de julio de 2026. Versión aproximada: `0.1.0`. Avance estimado hacia 1.0: **85 %**.

## Completado

- Base React/Vite, FastAPI, SQLite y scripts de Windows.
- Perfiles, avatares locales, historial, favoritos y pendientes.
- Contenidos locales para cursos de 1.º a 8.º básico y búsqueda con relevancia.
- Detección automática de materia, contexto conversacional y adaptación pedagógica por curso.
- Nexo, globos, modo demo, preguntas sugeridas y estado inicial diferenciado entre demo y perfil normal.
- Modo básico, configuración de IA local y uso opcional de Ollama con fallback local.
- Documentación principal, técnica, UX y de distribución inicial.

## En desarrollo o pendiente

- Validación visual/manual en equipos y resoluciones variadas.
- Pack portable, instalador Windows y pruebas en PC limpio.
- Revisión final de textos, contenidos y rendimiento con modelos locales.
- Tag `v1.0.0`, manual de distribución y definición de licencia.

## Decisiones técnicas y riesgos

- Datos y contenidos se mantienen locales; no se requiere OpenAI API.
- SQLite está en `backend/chat_escolar.db`; la configuración IA en `backend/data/settings.json`.
- El modo básico es el fallback seguro; Ollama no es requisito.
- Riesgos: modelos Ollama, rendimiento, puertos 8000/5173 y cobertura de contenidos.

## Próximos pasos hacia 1.0

1. Ejecutar pruebas funcionales y UX en PC limpio.
2. Preparar pack portable e instalador con fallback básico.
3. Revisar licencias de dependencias y modelos locales.
4. Corregir hallazgos, documentar release y crear el tag `v1.0.0`.
