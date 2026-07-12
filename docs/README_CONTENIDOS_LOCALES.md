# Contenidos locales de Chat Escolar

## ¿Qué son?

Los contenidos locales son archivos Markdown educativos que Chat Escolar puede consultar sin conectarse a una inteligencia artificial ni a un servicio externo. Sirven como una base de conocimiento gratuita para apoyar las respuestas del tutor demo.

Los archivos se guardan en la carpeta `contenidos/` de la raíz del proyecto.

## Estructura de carpetas

```text
contenidos/
├── quinto_basico/
│   ├── lenguaje/
│   ├── matematica/
│   ├── ciencias_naturales/
│   └── historia_geografia/
├── sexto_basico/
│   ├── lenguaje/
│   ├── matematica/
│   ├── ciencias_naturales/
│   └── historia_geografia/
└── primero_basico/          (pendiente)
```

## Cursos disponibles

Actualmente la base local contiene materiales curriculares para:

- 5° básico, en `contenidos/quinto_basico/`.
- 6° básico, en `contenidos/sexto_basico/`.

Los contenidos de 1° básico están pendientes o en preparación. El lector ya reconoce `contenidos/primero_basico/`, por lo que podrán agregarse más adelante sin cambiar el código.

## Materias reconocidas

- `lenguaje`
- `matematica`
- `ciencias_naturales`
- `historia_geografia`
- `modo_explorador`

El backend convierte automáticamente nombres visibles como “Matemática”, “Ciencias Naturales” o “Historia” a estas carpetas.

## Cómo nombrar los archivos

Usa nombres breves y descriptivos, sin espacios ni acentos. Se recomienda comenzar con un número para mantener un orden claro:

```text
09_adicion_y_sustraccion_de_fracciones.md
21_promedio_aritmetico.md
```

Cada archivo debería incluir un título principal como `# Tema: Promedio aritmético`. Puede incluir metadatos entre líneas `---`; el lector los omite del fragmento mostrado al estudiante.

## Cómo funciona la búsqueda

El backend convierte curso y materia a carpetas locales, elimina conectores y palabras muy cortas, busca coincidencias en nombre, título y contenido, y ordena los resultados por relevancia. Devuelve como máximo tres resultados, con extractos de hasta 800 caracteres.

Las rutas son relativas a `contenidos/`; nunca se expone una ruta personal del equipo.

## Probar el endpoint

Con el backend iniciado, puedes probar contenidos de 5° básico:

```text
http://127.0.0.1:8000/content/search?course=5%C2%B0%20b%C3%A1sico&subject=Matem%C3%A1tica&q=fracciones
```

Para probar promedio aritmético:

```text
http://127.0.0.1:8000/content/search?course=5%C2%B0%20b%C3%A1sico&subject=Matem%C3%A1tica&q=promedio%20aritm%C3%A9tico
```

La respuesta incluye `title`, `path`, `score` y `excerpt`.

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

### Preguntas sugeridas para probar en el frontend

Selecciona `6° básico`, elige la materia correspondiente y prueba:

- Matemática: “¿Cómo se suman fracciones y números mixtos?”
- Ciencias Naturales: “¿Qué formas de energía existen y cómo se transforman?”
- Lenguaje: “¿Qué estrategias ayudan a comprender mejor un texto?”
- Historia: “¿Cómo se organiza Chile en regiones?”

Cuando haya una coincidencia, el chat debe mostrar el indicador **Respuesta apoyada en contenidos locales** y el título de la fuente utilizada.

## Agregar contenidos de 1° básico

1. Crea `contenidos/primero_basico/` cuando los materiales estén listos.
2. Crea dentro las carpetas de materias necesarias.
3. Agrega archivos `.md` originales siguiendo la convención de nombres.
4. Prueba `/content/search` con el curso y materia correspondientes.

No es necesario cambiar código ni reiniciar el backend para agregar archivos dentro de las carpetas soportadas; cada búsqueda lee el contenido disponible en ese momento.

## Derechos de autor y calidad

No copies libros completos, guías comerciales ni otros materiales protegidos. Se recomienda crear contenido original en Markdown, usar explicaciones propias y registrar las fuentes curriculares cuando corresponda.

Antes de publicar una colección, revisa su claridad, exactitud, nivel educativo y adecuación para estudiantes.
