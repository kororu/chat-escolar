# Contenidos locales de Chat Escolar

## ¿Qué son?

Los contenidos locales son archivos Markdown educativos que Chat Escolar puede consultar sin conectarse a una inteligencia artificial ni a un servicio externo. Sirven como una base de conocimiento gratuita para apoyar las respuestas del tutor demo.

Los archivos se guardan en la carpeta `contenidos/` de la raíz del proyecto.

## Estructura de carpetas

```text
contenidos/
├── primero_basico/
├── segundo_basico/
├── tercero_basico/
├── cuarto_basico/
├── quinto_basico/
├── sexto_basico/
├── septimo_basico/
└── octavo_basico/
```

Cada curso sigue la convención de materias `lenguaje/`, `matematica/`, `ciencias_naturales/` e `historia_geografia/` cuando la colección está disponible.

## Cursos disponibles

El backend reconoce mapeos para 1° a 8° básico, incluyendo variantes sin tilde y nombres de carpeta como `quinto_basico`.

Los mapeos se centralizan en `backend/educational_config.py`. Crear o completar una carpeta nueva no exige cambiar el endpoint, pero sí revisar calidad, cobertura y pertinencia pedagógica de los archivos.

## Materias reconocidas

- `lenguaje`
- `matematica`
- `ciencias_naturales`
- `historia_geografia`
- `modo_explorador`

El backend convierte automáticamente nombres visibles como “Matemática”, “Ciencias Naturales”, “Historia” o “Historia, Geografía y Ciencias Sociales” a estas carpetas.

## Cómo nombrar los archivos

Usa nombres breves y descriptivos, sin espacios ni acentos. Se recomienda comenzar con un número para mantener un orden claro:

```text
09_adicion_y_sustraccion_de_fracciones.md
21_promedio_aritmetico.md
```

Cada archivo debería incluir un título principal como `# Tema: Promedio aritmético`. Puede incluir metadatos entre líneas `---`; el lector los omite del fragmento mostrado al estudiante.

## Cómo funciona la búsqueda

El backend convierte curso y materia a carpetas locales, normaliza la pregunta, elimina conectores y palabras muy cortas, y ordena los resultados por relevancia. Devuelve como máximo tres resultados, con extractos de hasta 800 caracteres.

Las rutas son relativas a `contenidos/`; nunca se expone una ruta personal del equipo.

### Normalización educativa

El análisis conserva siempre el texto original para el historial. Además genera una versión normalizada, intención, palabras clave, posible materia, posible tema y confianza de normalización.

El diccionario educativo tolera abreviaturas y errores leves conocidos sin aplicar correcciones agresivas a nombres propios. Por ejemplo, estas preguntas se interpretan como una consulta equivalente sobre hábitat:

- `q es habitat`
- `¿q es un havitat?`
- `k es habitat`
- `ke es un abitad`

El tutor responde al contenido de la pregunta sin reprender ni señalar el error de escritura.

### Puntuación y validación

La puntuación da mayor peso a:

1. nombre del archivo;
2. título;
3. tema declarado en metadatos;
4. palabras clave explícitas;
5. encabezados.

Las apariciones en el cuerpo tienen un peso bajo. Una coincidencia solo corporal no puede convertirse en fuente verificada. El umbral mínimo predeterminado es `24` y está centralizado en `MIN_RELEVANCE_SCORE` dentro de `backend/content_reader.py`.

Después de puntuar, el lector exige coherencia temática, elimina títulos duplicados, ordena por relevancia y devuelve fragmentos completos siempre que el límite lo permite. Para respuestas explicativas, evita usar como fuente principal archivos de índice, documentación, bancos, compendios o evaluaciones.

### Modo Escolar y Modo Explorador

- **Modo Escolar:** busca únicamente en la carpeta curricular del curso y materia seleccionados. Un tema externo, como tanques, no se presenta como parte de Ciencias Naturales.
- **Modo Explorador:** busca únicamente en una futura carpeta `modo_explorador`. Actualmente no existe una colección exploratoria verificada, por lo que esos temas usan un fallback transparente y seguro.

No se buscan temas exploratorios indiscriminadamente dentro de contenidos curriculares.

### Estados de procedencia

El buscador separa explícitamente la relación con la base Markdown local:

- `local_verified`: fuente local coherente que supera el umbral y se usa realmente.
- `local_related`: existe un tema local reconocido y relacionado, pero aparece como conexión, mención secundaria o referencia sin explicación suficiente para usarlo como fuente principal.
- `local_low_confidence`: hubo coincidencias débiles en la colección, pero sin un tema local reconocido con suficiente seguridad.
- `no_local_content`: no existe una colección local aplicable o no hubo candidatos locales para la consulta.
- `clarification_required`: la pregunta es demasiado ambigua y se pide precisar el tema.
- `demo_fallback`: respuesta demo genérica sin búsqueda local válida.
- `ollama_generated`: reservado para el futuro; todavía no está implementado.

Solo `local_verified` permite mostrar **Respuesta apoyada en contenidos locales** y una fuente. `local_related` puede devolver `related_results` con título, ruta relativa, sección y motivo de relación, pero esos datos no se tratan como fuente principal. `local_low_confidence` y `no_local_content` no exponen fuentes.

Ejemplo: si en 5° básico se pregunta por fotosíntesis y solo aparece como “Fotosíntesis de 6°” en **Conexiones con otros temas**, el estado correcto es `local_related`, no `local_verified`. Si se pregunta por fotosíntesis en 6° básico y existe una unidad directa, puede ser `local_verified`.

## Probar el endpoint

### Pruebas para 1° básico

Matemática y números:

```text
http://127.0.0.1:8000/content/search?course=1%C2%B0%20b%C3%A1sico&subject=Matem%C3%A1tica&q=numeros
```

Lenguaje y lectura:

```text
http://127.0.0.1:8000/content/search?course=1%C2%B0%20b%C3%A1sico&subject=Lenguaje&q=lectura
```

Ciencias Naturales y seres vivos:

```text
http://127.0.0.1:8000/content/search?course=1%C2%B0%20b%C3%A1sico&subject=Ciencias%20Naturales&q=seres%20vivos
```

Historia y comunidad:

```text
http://127.0.0.1:8000/content/search?course=1%C2%B0%20b%C3%A1sico&subject=Historia&q=comunidad
```

Estos cuatro ejemplos corresponden a temas presentes actualmente en las carpetas de 1° básico.

### Pruebas para 5° básico

Con el backend iniciado, puedes probar contenidos de 5° básico:

```text
http://127.0.0.1:8000/content/search?course=5%C2%B0%20b%C3%A1sico&subject=Matem%C3%A1tica&q=fracciones
```

Para probar promedio aritmético:

```text
http://127.0.0.1:8000/content/search?course=5%C2%B0%20b%C3%A1sico&subject=Matem%C3%A1tica&q=promedio%20aritm%C3%A9tico
```

La respuesta incluye `title`, `path`, `score` y `excerpt`.

El endpoint también acepta `mode` y devuelve `provenance_status`, `query_analysis`, `minimum_score` y `best_score`:

```text
http://127.0.0.1:8000/content/search?course=5%C2%B0%20b%C3%A1sico&subject=Ciencias%20Naturales&mode=Explorar%20mis%20intereses&q=tanques
```

### Pruebas para 6° básico

Matemática y fracciones:

```text
http://127.0.0.1:8000/content/search?course=6%C2%B0%20b%C3%A1sico&subject=Matem%C3%A1tica&q=fracciones
```

Ciencias Naturales y energía:

```text
http://127.0.0.1:8000/content/search?course=6%C2%B0%20b%C3%A1sico&subject=Ciencias%20Naturales&q=energia
```

Lenguaje y comprensión:

```text
http://127.0.0.1:8000/content/search?course=6%C2%B0%20b%C3%A1sico&subject=Lenguaje&q=comprension
```

Historia y Chile:

```text
http://127.0.0.1:8000/content/search?course=6%C2%B0%20b%C3%A1sico&subject=Historia&q=chile
```

### Preguntas sugeridas para probar 1° básico en el frontend

Selecciona un perfil de estudiante de `1° básico`, elige la materia correspondiente y prueba:

- Matemática: “¿Qué son los números?”
- Lenguaje: “¿Cómo reconozco una vocal?”
- Ciencias Naturales: “¿Qué necesitan los seres vivos?”
- Historia: “¿Qué es una comunidad?”

La respuesta debe usar el contenido local cuando exista una coincidencia, mostrar el indicador **Respuesta apoyada en contenidos locales** y guardar la pregunta en el historial del perfil. La interfaz muestra solamente el título de la fuente, no su ruta técnica.

### Preguntas sugeridas para probar 6° básico en el frontend

Selecciona `6° básico`, elige la materia correspondiente y prueba:

- Matemática: “¿Cómo se suman fracciones y números mixtos?”
- Ciencias Naturales: “¿Qué formas de energía existen y cómo se transforman?”
- Lenguaje: “¿Qué estrategias ayudan a comprender mejor un texto?”
- Historia: “¿Cómo se organiza Chile en regiones?”

Cuando haya una coincidencia, el chat debe mostrar el indicador **Respuesta apoyada en contenidos locales** y el título de la fuente utilizada.

## Convención para cursos futuros

Cuando los contenidos estén terminados e incorporados, las carpetas futuras podrán seguir esta convención:

- `contenidos/segundo_basico/`
- `contenidos/tercero_basico/`
- `contenidos/cuarto_basico/`
- `contenidos/septimo_basico/`
- `contenidos/octavo_basico/`

Crear una carpeta no basta para declarar un curso disponible: primero debe contener materiales revisados y el lector debe reconocer su nombre. No es necesario reiniciar el backend al agregar archivos dentro de una carpeta ya soportada; cada búsqueda lee el contenido disponible en ese momento.

## Derechos de autor y calidad

No copies libros completos, guías comerciales ni otros materiales protegidos. Se recomienda crear contenido original en Markdown, usar explicaciones propias y registrar las fuentes curriculares cuando corresponda.

Antes de publicar una colección, revisa su claridad, exactitud, nivel educativo y adecuación para estudiantes.

## Limitaciones y preparación futura

- Existe una memoria conversacional local ligera: usa hasta seis interacciones del mismo perfil y conversación para reconstruir preguntas de seguimiento confiables. No usa ni concatena todo el historial.
- Si no hay un tema activo confiable, una frase como “¿cuál fue el más usado?” solicita aclaración.
- Un cambio claro de tema, como “¿qué es un hábitat?”, descarta el tema conversacional anterior.
- La búsqueda utiliza la consulta contextual solo para recuperar contenido; el historial visible conserva siempre el texto original del estudiante.
- No existe todavía una colección Markdown de Modo Explorador.
- Ollama no está integrado.
- No se usa OpenAI API.

El contrato deja preparado este orden futuro: contenido curricular local confiable, contenido exploratorio local, IA local mediante Ollama y respuesta segura de respaldo.

## Preparación para Ollama

`POST /chat/demo` devuelve un campo `provider` y un objeto `ai_context` con la pregunta, curso, materia, estado de procedencia, fuentes verificadas, temas relacionados y contexto conversacional. Ese contrato permite alimentar una IA local en el futuro sin cambiar el flujo principal del frontend.

En esta etapa `ollama_enabled` es `false`, `future_provider` queda reservado como `ollama` y no se realiza ninguna llamada a `localhost:11434`.
