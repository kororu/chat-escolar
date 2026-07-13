# Nexo en la interfaz

Nexo es la identidad visual de Chat Escolar. Sus respuestas se muestran en una burbuja propia junto a un avatar; las preguntas del perfil activo usan una burbuja diferente.

## Variantes

El selector central está en `frontend/src/assets/nexo/nexoVariants.js`. La prioridad es: pensando, felicitación, pregunta, materia, respuesta y reposo.

Los assets reales se importan desde `frontend/src/assets/nexo/` con estos nombres:

- `nexo_reposo.png`
- `nexo_respuesta.png`
- `nexo_pensando.png`
- `nexo_pregunta.png`
- `nexo_felicitacion.png`
- `nexo_matematica_01.png` y `nexo_matematica_02.png`
- `nexo_ciencias_01.png` y `nexo_ciencias_02.png`
- `nexo_historia_01.png` y `nexo_historia_02.png`
- `nexo_lenguaje_01.png` y `nexo_lenguaje_02.png`
- `nexo_bienvenida.png`

El mapa central importa únicamente los archivos existentes desde `frontend/src/assets/nexo/nexoVariants.js`. Si una imagen no carga en el navegador, el avatar muestra el placeholder CSS con la letra `N`; para un archivo ausente antes del build, debe retirarse su importación o apuntarse su clave a `nexo_respuesta.png`. Las clases por variante permiten agregar transiciones o animaciones ligeras en una fase posterior.

Las respuestas nuevas guardan `nexoVariant` al crearse. Por eso una variante de materia se elige al azar una sola vez y no cambia con un re-renderizado, badge o actualización de tiempo. Para añadir más variantes, agrega la clave y el archivo al array de `NEXO_SUBJECT_VARIANTS` en `frontend/src/assets/nexo/nexoVariants.js`.

## Imagen de bienvenida

La pantalla de selección de perfiles usa `nexo_bienvenida.png` como hero de bienvenida. Coloca el archivo final en `frontend/src/assets/nexo/nexo_bienvenida.png`; el mapeo de variantes se mantiene en `frontend/src/assets/nexo/nexoVariants.js`. Mientras el archivo no exista, se muestra un placeholder grande de Nexo sin bloquear la selección de perfil.

## Globos y avatar del usuario

Nexo se muestra como PNG transparente grande a la izquierda de su globo, sin marco circular. El usuario usa un globo a la derecha y un avatar circular pequeño creado con la primera letra de su nombre; funciona con tildes y eñes. `UserAvatar` ya acepta `imageUrl`, `avatarImage` y `avatarColor` para una futura imagen personalizada, pero esta versión no incluye carga ni almacenamiento de imágenes de perfil.
