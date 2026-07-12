# Contenidos locales de Chat Escolar

## ¿Qué son?

Los contenidos locales son archivos Markdown educativos que Chat Escolar puede consultar sin conectarse a una inteligencia artificial ni a un servicio externo. Sirven como una base de conocimiento gratuita para apoyar las respuestas del tutor demo.

Los archivos se guardan en la carpeta `contenidos/` de la raíz del proyecto.

## Estructura de carpetas

```text
contenidos/
├── primero_basico/
│   ├── lenguaje/
│   ├── matematica/
│   ├── ciencias_naturales/
│   ├── historia_geografia/
│   └── modo_explorador/
├── quinto_basico/
│   └── ...
└── sexto_basico/
    └── ...
```

Actualmente la colección principal corresponde a 5° básico. El lector ya reconoce las carpetas de 1°, 5° y 6° básico para permitir agregar contenido gradualmente.

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

Con el backend iniciado, abre:

```text
http://127.0.0.1:8000/content/search?course=5%C2%B0%20b%C3%A1sico&subject=Matem%C3%A1tica&q=fracciones
```

Para probar promedio aritmético:

```text
http://127.0.0.1:8000/content/search?course=5%C2%B0%20b%C3%A1sico&subject=Matem%C3%A1tica&q=promedio%20aritm%C3%A9tico
```

La respuesta incluye `title`, `path`, `score` y `excerpt`.

## Agregar contenidos de 1° y 6° básico

1. Crea `contenidos/primero_basico/` o `contenidos/sexto_basico/`.
2. Crea dentro las carpetas de materias necesarias.
3. Agrega archivos `.md` originales siguiendo la convención de nombres.
4. Prueba `/content/search` con el curso y materia correspondientes.

No es necesario cambiar código ni reiniciar el backend para agregar archivos dentro de las carpetas soportadas; cada búsqueda lee el contenido disponible en ese momento.

## Derechos de autor y calidad

No copies libros completos, guías comerciales ni otros materiales protegidos. Se recomienda crear contenido original en Markdown, usar explicaciones propias y registrar las fuentes curriculares cuando corresponda.

Antes de publicar una colección, revisa su claridad, exactitud, nivel educativo y adecuación para estudiantes.
