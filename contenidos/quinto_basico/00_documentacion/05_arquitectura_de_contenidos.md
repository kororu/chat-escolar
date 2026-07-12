# Arquitectura de contenidos

## Unidad mínima

Cada capítulo contiene front matter YAML y secciones semánticas. El `id` es estable y debe conservarse en futuras versiones.

## Tipos de documentos

- `contenido_curricular_original`: capítulos temáticos.
- `indice_asignatura`: navegación humana.
- `apoyo_inclusivo`: modos y estrategias.
- `banco_practica`: preguntas o actividades reutilizables.
- `evaluacion`: diagnóstico o instrumento.
- `documentacion_tecnica`: integración y control.
- `compendio`: duplicado para lectura humana; no indexar junto a módulos.

## Versionado

- Cambios menores: 1.0 → 1.1.
- Cambios pedagógicos importantes: 1.x → 2.0.
- No sobrescribir sin registrar en `CHANGELOG.md`.
- Reindexar al cambiar contenido o metadatos.

## Dependencias

Los capítulos pueden leerse solos, pero `Conexiones con otros temas` permite ampliar. En una consulta difícil, el recuperador debe añadir como máximo uno o dos prerrequisitos para no saturar contexto.
