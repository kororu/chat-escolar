# Chat Escolar

Aplicación educativa local con tutor demo, perfiles, historial y recursos curados.

## Base de conocimiento local

Chat Escolar puede leer archivos Markdown desde `contenidos/` y utilizarlos como apoyo para sus respuestas. La búsqueda funciona localmente, sin OpenAI API ni servicios pagados.

Actualmente la base puede consultar contenidos curriculares Markdown de 1°, 5° y 6° básico. Los cursos 2°, 3°, 4°, 7° y 8° básico están en preparación y todavía no deben considerarse disponibles.

La guía para organizar, agregar y probar estos materiales está en [docs/README_CONTENIDOS_LOCALES.md](docs/README_CONTENIDOS_LOCALES.md).

El buscador valida relevancia antes de mostrar una fuente: pondera títulos, temas, palabras clave y encabezados, y separa el contenido curricular del futuro Modo Explorador. Las coincidencias débiles no se presentan como respaldo verificado.

Las preguntas de seguimiento usan una memoria local breve aislada por perfil y conversación. El historial conserva siempre el texto original del estudiante; las reconstrucciones se usan solo internamente para buscar contenido o pedir una aclaración segura.

## Perfiles locales

Los perfiles se pueden crear, cambiar y eliminar desde la pantalla de selección. Eliminar un perfil requiere confirmación y borra únicamente su historial, favoritos, pendientes y contexto conversacional local. Consulta [docs/README_PERFILES_LOCALES.md](docs/README_PERFILES_LOCALES.md).

## Autoría

Chat Escolar es un proyecto desarrollado por **Ariel Ponce**.

Versión actual: `0.1.0`
Año: `2026`

La marca de autoría no debe eliminarse de las versiones de prueba distribuidas por el autor.

Consulta [docs/AUTORIA_Y_VERSIONADO.md](docs/AUTORIA_Y_VERSIONADO.md) para conocer dónde se centraliza esta información y cómo actualizar la versión.
