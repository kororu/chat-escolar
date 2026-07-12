# Enciclopedia de 5° básico para Chat Escolar

**Versión:** 1.0  
**Fecha de verificación curricular:** 2026-07-11  
**Formato:** Markdown UTF-8 + índices JSONL para recuperación local  
**Estado:** base inicial completa, lista para revisión pedagógica continua

## Qué es

Esta carpeta es una base de conocimiento original y modular para un chatbot educativo local. Desarrolla contenidos de **Lenguaje y Comunicación, Matemática, Ciencias Naturales e Historia, Geografía y Ciencias Sociales** de 5° básico chileno. No reproduce textos escolares ni pretende reemplazar la planificación docente.

## Cobertura actual

- Lenguaje y Comunicación: **23 capítulos**.
- Matemática: **24 capítulos**.
- Ciencias Naturales: **17 capítulos**.
- Historia, Geografía y Ciencias Sociales: **22 capítulos**.
- Total de capítulos curriculares: **86**.
- Además incluye documentación, glosarios, evaluaciones, bancos, apoyos inclusivos, compendios e índices para RAG/Ollama.

## Cómo comenzar

1. Leer [`00_documentacion/00_indice_maestro.md`](00_documentacion/00_indice_maestro.md).
2. Revisar [`00_documentacion/01_estado_curricular_y_fuentes.md`](00_documentacion/01_estado_curricular_y_fuentes.md).
3. Para integrar con Ollama, seguir [`00_documentacion/06_integracion_ollama_rag.md`](00_documentacion/06_integracion_ollama_rag.md).
4. Indexar preferentemente los capítulos modulares y no los compendios al mismo tiempo.
5. Ejecutar las pruebas de recuperación descritas en [`00_documentacion/09_pruebas_de_recuperacion.md`](00_documentacion/09_pruebas_de_recuperacion.md).

## Principios editoriales

- Explicación directa antes de la profundidad.
- Contenido original y alineado al currículum oficial consultado.
- Código OA como referencia, con advertencia de verificación normativa.
- Ejemplos apropiados para 10–11 años.
- Distinción entre hecho, modelo, inferencia y opinión.
- Adaptaciones como opciones de acceso, no reducción automática de expectativas.
- Lenguaje respetuoso, literal y predecible cuando sea necesario.
- Seguridad explícita en experimentos, electricidad, salud y situaciones de riesgo.

## Estructura

```text
Enciclopedia_5_Basico_Chat_Escolar/
├── README.md
├── 00_documentacion/
├── lenguaje/
├── matematica/
├── ciencias_naturales/
├── historia_geografia/
├── apoyo_inclusivo/
├── bancos/
├── evaluaciones/
└── compendios/
```

## Importante para la IA local

Los archivos de `compendios/` son cómodos para lectura humana, pero duplican el contenido de los capítulos. Para evitar resultados repetidos, el índice vectorial debe usar **o bien los archivos modulares o bien los compendios**, nunca ambos en la misma colección.
