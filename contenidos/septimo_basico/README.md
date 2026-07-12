---
proyecto: "Chat Escolar"
autor_proyecto: "Ariel Ponce"
curso: septimo_basico
version: 1.0
fecha_verificacion: 2026-07-12
---

# Enciclopedia de 7° básico para Chat Escolar

Base modular original en Markdown para un chatbot educativo local. Incluye contenidos de:

- Lengua y Literatura
- Matemática
- Ciencias Naturales
- Historia, Geografía y Ciencias Sociales

## Alcance

Esta versión contiene **100 capítulos curriculares**:

- 33 de Lengua y Literatura.
- 24 de Matemática.
- 20 de Ciencias Naturales.
- 23 de Historia, Geografía y Ciencias Sociales.

También contiene índices, rutas de aprendizaje, evaluaciones originales, bancos de práctica, glosarios, apoyos inclusivos, compendios y archivos JSONL para recuperación RAG.

## Criterio curricular

Las páginas oficiales del Currículum Nacional fueron revisadas el 2026-07-12. Los capítulos están **alineados temáticamente** con los ejes y contenidos publicados para el nivel. No se copiaron textos escolares ni formulaciones extensas protegidas.

Los códigos OA exactos no se inventan: deben verificarse individualmente en el portal oficial antes de usarlos en documentos normativos, planificaciones formales o informes de cobertura legal.

## Uso recomendado

Para respuestas del chatbot, indexar primero:

```text
septimo_basico/lenguaje/
septimo_basico/matematica/
septimo_basico/ciencias_naturales/
septimo_basico/historia_geografia/
```

Excluir de la primera indexación:

```text
septimo_basico/compendios/
septimo_basico/evaluaciones/
septimo_basico/bancos/
```

Los compendios duplican los capítulos. Evaluaciones y bancos pueden incorporarse después en colecciones separadas para los modos práctica, repaso y diagnóstico.

## Estructura

```text
septimo_basico/
├── 00_documentacion/
├── lenguaje/
├── matematica/
├── ciencias_naturales/
├── historia_geografia/
├── evaluaciones/
├── bancos/
├── apoyo_inclusivo/
└── compendios/
```

## Estado

Versión inicial amplia, lista para revisión pedagógica, pruebas de recuperación y mejora progresiva con preguntas reales de estudiantes.
