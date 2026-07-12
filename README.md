# Chat Escolar

Aplicación educativa local con tutor demo, perfiles, historial y recursos curados.

## Base de conocimiento local

Chat Escolar puede leer archivos Markdown desde `contenidos/` y utilizarlos como apoyo para sus respuestas. La búsqueda funciona localmente, sin OpenAI API ni servicios pagados.

La base local reconoce carpetas curriculares Markdown de 1° a 8° básico. El backend centraliza los mapeos de cursos y materias para que el selector, la búsqueda y la futura capa de IA local usen la misma convención de carpetas.

La guía para organizar, agregar y probar estos materiales está en [docs/README_CONTENIDOS_LOCALES.md](docs/README_CONTENIDOS_LOCALES.md).

El buscador valida relevancia antes de mostrar una fuente: pondera títulos, temas, palabras clave y encabezados, evita índices o compendios como fuente principal cuando corresponde, y separa el contenido curricular del futuro Modo Explorador. Las coincidencias débiles o relacionadas no se presentan como respaldo verificado.

El curso asociado al perfil se usa como preferencia inicial, pero la búsqueda respeta siempre el curso activo que envía el frontend. Si el estudiante cambia de 5° a 6° básico en el selector, `/chat/demo` busca en 6° básico aunque el perfil siga asociado a 5°.

El selector incluye **Todos los cursos** para buscar en toda la base Markdown local. En Modo Escolar se busca primero en el curso activo; si no hay fuente local verificada, el backend puede revisar todos los cursos y marcar claramente `source_course` cuando la fuente viene de otro nivel. En Modo Explorador también se consulta la base local global antes de usar una respuesta demo de respaldo.

`POST /chat/demo` devuelve metadatos de procedencia como `effective_course`, `source_course`, `source_subject`, `used_local_content`, `content_sources` y `found_in_other_course`. El frontend muestra avisos simples para fuente verificada, tema relacionado, baja confianza, ausencia de contenido local y fuentes encontradas en otro curso.

Las preguntas de seguimiento usan una memoria local breve aislada por perfil y conversación. El historial conserva siempre el texto original del estudiante; las reconstrucciones se usan solo internamente para buscar contenido o pedir una aclaración segura.

El backend deja preparado un contrato `provider`/`ai_context` para una futura integración con Ollama, pero esta versión no llama Ollama ni OpenAI API.

## Perfiles locales

Los perfiles se pueden crear, cambiar y eliminar desde la pantalla de selección. Eliminar un perfil requiere confirmación y borra únicamente su historial, favoritos, pendientes y contexto conversacional local. Consulta [docs/README_PERFILES_LOCALES.md](docs/README_PERFILES_LOCALES.md).

## Autoría

Chat Escolar es un proyecto desarrollado por **Ariel Ponce**.

Versión actual: `0.1.0`
Año: `2026`

La marca de autoría no debe eliminarse de las versiones de prueba distribuidas por el autor.

Consulta [docs/AUTORIA_Y_VERSIONADO.md](docs/AUTORIA_Y_VERSIONADO.md) para conocer dónde se centraliza esta información y cómo actualizar la versión.
