---
proyecto: Chat Escolar
tipo_documento: mapa_general_base_conocimiento
cursos: [primero_basico, quinto_basico, sexto_basico]
asignaturas: [lenguaje_y_comunicacion, matematica, ciencias_naturales, historia_geografia_y_ciencias_sociales]
version: 1.0
fecha_verificacion: 2026-07-11
estado: mapa_inicial
---

# Mapa General de Contenidos para 1°, 5° y 6° Básico — Chat Escolar


> **Estado de verificación curricular:** revisión realizada el 11 de julio de 2026 en el portal oficial Currículum Nacional/MINEDUC. Para 1°, 5° y 6° básico, las páginas oficiales consultadas siguen presentando como base obligatoria las Bases Curriculares de 1° a 6° básico y utilizan los nombres **Lenguaje y Comunicación**, **Matemática**, **Ciencias Naturales** e **Historia, Geografía y Ciencias Sociales**. El MINEDUC mantiene un proceso de actualización curricular de 1° básico a 2° medio; por ello, este mapa se basa en el currículum publicado como vigente y no trata propuestas en evaluación como normativa aprobada.


## 1. Objetivo de la base de conocimiento

Crear una base local, organizada y ampliable que permita a **Chat Escolar**:

- Responder preguntas escolares con lenguaje apropiado para el curso.
- Explicar un mismo concepto en distintos niveles de dificultad.
- Ayudar a estudiantes que necesitan instrucciones más directas, predecibles o fragmentadas.
- Apoyar a estudiantes autistas o con dificultades de comprensión sin reducir innecesariamente la profundidad del contenido.
- Entregar ejemplos chilenos y situaciones cotidianas cercanas.
- Diferenciar contenidos curriculares, conocimientos complementarios y temas de curiosidad.
- Funcionar sin depender de servicios pagados ni de una conexión permanente a internet.
- Servir como fuente documental para una futura IA local mediante Ollama y un sistema de recuperación de información.

La base no reemplaza la enseñanza docente, la evaluación profesional ni los apoyos individuales definidos por cada establecimiento.

## 2. Cursos incluidos

- **1° básico:** inicio de la alfabetización, pensamiento matemático concreto, exploración del entorno y formación de nociones temporales, espaciales y ciudadanas.
- **5° básico:** consolidación de lectura y escritura, ampliación del razonamiento matemático, estudio de sistemas del cuerpo y energía, geografía de Chile, conquista, Colonia y derechos.
- **6° básico:** mayor autonomía lectora y argumentativa, razones y porcentajes, álgebra inicial, energía y materia, historia republicana de Chile, democracia y territorio nacional.

## 3. Materias incluidas

Los nombres oficiales usados en el portal curricular consultado son:

1. **Lenguaje y Comunicación**
2. **Matemática**
3. **Ciencias Naturales**
4. **Historia, Geografía y Ciencias Sociales**

### Diferencias de nombres que deben controlarse

- El portal también agrupa recursos bajo expresiones como **“Lenguaje y comunicación / Lengua y literatura”**, pero las páginas específicas de 1°, 5° y 6° básico consultadas mantienen **Lenguaje y Comunicación**.
- En la estructura de carpetas puede usarse `historia_geografia`, pero los documentos deben registrar el nombre oficial completo de la asignatura.
- Las “unidades” de los Programas de Estudio son una organización didáctica sugerida. Los **ejes** y los **Objetivos de Aprendizaje** son la referencia curricular principal. Por eso, los archivos futuros deberán registrar ambos cuando corresponda.

## 4. Reglas de redacción

1. Escribir contenido original, sin copiar páginas de textos escolares.
2. Usar español de Chile claro y neutral.
3. Preferir oraciones breves, voz activa y orden lógico.
4. Explicar cada término nuevo antes de usarlo repetidamente.
5. Presentar una idea principal por párrafo.
6. Empezar por lo concreto y avanzar hacia lo abstracto.
7. Incluir ejemplos resueltos paso a paso.
8. Separar claramente:
   - definición;
   - ejemplo;
   - procedimiento;
   - práctica;
   - respuesta.
9. No presentar una opinión como hecho.
10. Evitar información histórica simplificada que borre conflictos, diversidad de actores o consecuencias.
11. En ciencias, distinguir observación, explicación, modelo y conclusión.
12. En matemática, mostrar procedimiento y no solo resultado.
13. En lenguaje, usar textos originales breves o de dominio público cuando se necesiten ejercicios.
14. En temas sensibles, usar lenguaje respetuoso, apropiado para la edad y sin estigmatización.
15. Añadir fecha de revisión y fuente curricular a cada archivo.
16. Marcar cualquier contenido que exceda el currículum como `ampliacion` o `curiosidad_guiada`.
17. No inventar códigos OA. Cuando no se haya comprobado un código exacto, usar una descripción curricular alineada y marcar `oa_por_verificar`.

## 5. Reglas de adaptación TEA y lectura fácil

Las adaptaciones deben entenderse como opciones de acceso, no como una reducción automática de expectativas.

### Principios

- No asumir que todos los estudiantes autistas aprenden de la misma manera.
- Permitir respuestas breves, extensas o paso a paso.
- Mantener una estructura predecible.
- Usar lenguaje literal; explicar metáforas, ironías y dobles sentidos.
- Evitar información innecesaria antes de responder la pregunta central.
- Dividir tareas largas en pasos numerados.
- Anticipar qué se hará: “Primero veremos…, después practicaremos…”.
- Destacar palabras clave sin llenar el texto de mayúsculas.
- Ofrecer ejemplos visuales descritos con palabras, tablas simples o esquemas.
- Permitir pausas y repetición sin emitir juicios.
- No usar frases como “esto es muy fácil”.
- Validar el esfuerzo y corregir el procedimiento de manera específica.
- Dar una instrucción principal por vez.
- Evitar preguntas demasiado abiertas cuando el estudiante necesita estructura.
- Ofrecer alternativas: selección, verdadero/falso, completar y respuesta libre.
- Explicar los cambios de actividad o de criterio.
- En conversaciones sobre emociones, pubertad o convivencia, usar descripciones directas y respetuosas.
- No diagnosticar, etiquetar ni atribuir una dificultad exclusivamente al autismo.

### Formato de lectura fácil recomendado

- Título directo.
- Respuesta inicial en 1 a 3 oraciones.
- Palabras clave.
- Explicación por pasos.
- Ejemplo.
- Comprobación breve.
- Opción “explícamelo más simple”.
- Opción “dame un desafío”.

## 6. Estructura de carpetas recomendada

```text
contenidos/
├── primero_basico/
│   ├── lenguaje/
│   ├── matematica/
│   ├── ciencias_naturales/
│   └── historia_geografia/
├── quinto_basico/
│   ├── lenguaje/
│   ├── matematica/
│   ├── ciencias_naturales/
│   └── historia_geografia/
└── sexto_basico/
    ├── lenguaje/
    ├── matematica/
    ├── ciencias_naturales/
    └── historia_geografia/
```

### Carpetas complementarias recomendadas

```text
contenidos/
├── _mapas/
├── _plantillas/
├── _glosarios/
├── _evaluaciones/
├── _fuentes/
└── _versiones/
```

- `_mapas/`: mapas generales y por curso.
- `_plantillas/`: plantilla de tema, actividad y evaluación.
- `_glosarios/`: términos comunes y equivalencias.
- `_evaluaciones/`: bancos de preguntas originales.
- `_fuentes/`: registro de enlaces y fecha de verificación.
- `_versiones/`: historial de cambios.

## 7. Convención de nombres de archivos

Formato recomendado:

```text
[curso]_[asignatura]_[eje]_[numero]_[tema].md
```

Ejemplos:

```text
1b_len_lectura_01_conciencia_fonologica.md
1b_mat_numeros_04_adicion_hasta_20.md
5b_csn_vida_03_sistema_digestivo.md
6b_his_historia_07_independencia_de_chile.md
```

### Reglas técnicas

- Usar minúsculas.
- No usar tildes ni espacios en el nombre físico.
- Usar guion bajo como separador.
- Mantener un número de orden de dos dígitos.
- No cambiar el identificador de un archivo publicado; crear una nueva versión.
- Evitar archivos demasiado grandes. Un tema principal por archivo.
- Conservar el nombre oficial completo dentro del documento.

### Metadatos mínimos sugeridos

```yaml
---
id: 5b_mat_numeros_07_fracciones_equivalentes
curso: 5_basico
asignatura: matematica
eje: numeros_y_operaciones
tema: fracciones_equivalentes
tipo: contenido_curricular
nivel_dificultad: inicial
oa_relacionado: descripcion_verificada_o_codigo
fuente_curricular: curriculum_nacional_mineduc
fecha_verificacion: AAAA-MM-DD
version: 1.0
---
```

## 8. Integración con Chat Escolar

### Flujo esperado

1. El frontend envía la pregunta, curso y preferencias de apoyo.
2. FastAPI normaliza la consulta.
3. El backend identifica asignatura, eje, tema y nivel de dificultad.
4. El sistema busca primero en los archivos del curso seleccionado.
5. Recupera fragmentos relevantes y sus metadatos.
6. La IA local construye una respuesta usando esos fragmentos.
7. Un validador revisa que:
   - el lenguaje corresponda al curso;
   - no se inventen fuentes u OA;
   - la respuesta contenga pasos cuando sean necesarios;
   - no se mezcle contenido de otro curso sin indicarlo.
8. Se registra en el historial la pregunta, tema, archivos usados y tipo de ayuda solicitada.

### Datos que debería enviar el frontend

```json
{
  "pregunta": "¿Qué es una fracción equivalente?",
  "curso": "5_basico",
  "modo_respuesta": "paso_a_paso",
  "perfil_apoyo": {
    "lectura_facil": true,
    "ejemplos_concretos": true,
    "cantidad_ejercicios": 2
  }
}
```

### Tipos de respuesta

- `respuesta_directa`
- `paso_a_paso`
- `lectura_facil`
- `ejemplo_resuelto`
- `practica_guiada`
- `repaso`
- `desafio`
- `explicacion_para_apoderado`

## 9. Uso con IA local tipo Ollama

### Arquitectura recomendada

- **Ollama:** ejecuta el modelo de lenguaje local.
- **FastAPI:** coordina consulta, recuperación y respuesta.
- **Base Markdown:** fuente pedagógica controlada.
- **Índice de búsqueda:** almacena fragmentos y metadatos.
- **Recuperación aumentada con documentos:** selecciona contenido antes de generar la respuesta.

### Reglas para la IA

- No responder solo desde la memoria general del modelo cuando exista contenido curricular recuperado.
- Citar internamente el `id` de los archivos utilizados.
- Indicar cuando no hay información suficiente.
- No inventar un OA.
- Priorizar el curso seleccionado.
- Explicar contenido de cursos superiores solo como ampliación y advertirlo.
- No mostrar instrucciones internas ni metadatos técnicos al estudiante.
- Mantener separados “respuesta”, “ejemplo” y “práctica”.
- Usar un modelo de respuesta predecible para estudiantes que lo requieran.

### Fragmentación e indexación

- Dividir por encabezados semánticos, no cortar ejemplos por la mitad.
- Guardar juntos la pregunta, explicación y respuesta esperada cuando formen una actividad.
- Añadir curso, asignatura, eje, tema, dificultad y tipo de contenido a cada fragmento.
- Evitar mezclar en un mismo fragmento una explicación para estudiante y otra para docente.
- Reindexar cuando cambie la versión de un archivo.
- Mantener un registro local de la versión curricular usada.

### Respuesta base sugerida

```text
Respuesta breve:
[idea principal]

Paso a paso:
1. [...]
2. [...]
3. [...]

Ejemplo:
[...]

Comprueba:
[pregunta breve]
```

## 10. Orden recomendado de creación

### Fase 1 — Fundamentos de alto uso

1. 1° básico: alfabetización inicial y números hasta 20.
2. 5° básico: comprensión lectora, operaciones, fracciones y cuerpo humano.
3. 6° básico: comprensión crítica, fracciones/decimales, pubertad y democracia.

### Fase 2 — Cobertura curricular completa

4. Completar todos los ejes de Matemática.
5. Completar lectura, escritura y comunicación oral.
6. Completar Ciencias de la Vida.
7. Completar Historia y Geografía.
8. Completar Ciencias Físicas y Químicas, Tierra y Universo.
9. Completar Formación Ciudadana.

### Fase 3 — Práctica y evaluación

10. Crear preguntas fáciles, medias y desafío.
11. Crear errores comunes y explicaciones alternativas.
12. Crear actividades breves sin materiales especiales.
13. Crear evaluaciones diagnósticas originales.
14. Crear glosarios por curso.

### Fase 4 — Inclusión y calidad

15. Revisar todos los temas con criterios de lectura fácil.
16. Crear variantes paso a paso y apoyos visuales descritos.
17. Probar preguntas reales de estudiantes.
18. Revisar sesgos, precisión histórica y seguridad científica.
19. Verificar nuevamente las fuentes oficiales antes de publicar una versión anual.

## 11. Plantilla estándar para futuros archivos por tema

```markdown
---
id: [identificador_unico]
curso: [curso]
asignatura: [asignatura]
eje: [eje]
tema: [tema]
tipo: contenido_curricular
nivel_dificultad: [inicial|medio|desafio]
oa_relacionado: [codigo_verificado_o_descripcion]
fecha_verificacion: [AAAA-MM-DD]
version: 1.0
---

# Tema: [Nombre del tema]

## Curso

[Curso]

## Asignatura

[Asignatura]

## Unidad o eje

[Unidad o eje]

## Objetivo de aprendizaje relacionado

[OA o descripción alineada al currículum]

## Explicación para estudiante

[Explicación simple]

## Explicación para apoderado

[Cómo explicarlo en casa]

## Explicación para docente

[Cómo trabajarlo en clase]

## Palabras clave

[Conceptos importantes]

## Ejemplo simple

[Ejemplo fácil]

## Actividad breve

[Actividad de 5 a 10 minutos]

## Preguntas de práctica

### Fácil

[Preguntas]

### Media

[Preguntas]

### Desafío

[Preguntas]

## Respuestas esperadas

[Respuestas]

## Errores comunes

[Errores típicos]

## Cómo explicarlo si el estudiante no entiende

[Versión más simple y concreta]

## Mini resumen

[Resumen breve]

## Conexión con otros temas

[Temas relacionados]
```

## 12. Control de calidad antes de incorporar un tema

- [ ] El tema pertenece al curso indicado.
- [ ] El eje coincide con la publicación oficial.
- [ ] El OA fue verificado o está marcado como descripción por verificar.
- [ ] El texto es original.
- [ ] La explicación inicial responde directamente.
- [ ] Incluye un ejemplo apropiado para la edad.
- [ ] Incluye al menos una adaptación de acceso.
- [ ] Las respuestas de práctica están revisadas.
- [ ] No hay lenguaje discriminatorio ni infantilización.
- [ ] La fecha y versión están registradas.
- [ ] El archivo puede entenderse sin depender de otro archivo.
- [ ] Los enlaces externos no son necesarios para comprender la explicación.


## Fuentes oficiales de referencia

Consulta y verificación realizadas el 11 de julio de 2026:

- Currículum Nacional, Bases Curriculares de 1° a 6° básico: https://www.curriculumnacional.cl/curriculum/1o-6o-basico
- Marco de Bases Curriculares, Ayuda MINEDUC: https://www.ayudamineduc.cl/ficha/marco-bases-curriculares
- Proceso de Actualización Curricular: https://www.curriculumnacional.cl/actualizacion-curricular
- Currículum de 1° básico: https://www.curriculumnacional.cl/curriculum/1o-6o-basico/curso/1-basico
- Currículum de 5° básico: https://www.curriculumnacional.cl/curriculum/1o-6o-basico/curso/5-basico
- Currículum de 6° básico: https://www.curriculumnacional.cl/curriculum/1o-6o-basico/curso/6-basico
- Educación Especial MINEDUC, recursos sobre estudiantes autistas: https://especial.mineduc.cl/implementacion-ley-n21-545/
- Lectura accesible, Educación Especial MINEDUC: https://especial.mineduc.cl/recursos-apoyo-al-aprendizaje/recursos-las-los-docentes/lectura-accesible/

### Criterio de uso de las fuentes

Este proyecto no reproduce libros escolares ni copia programas completos. Los mapas convierten los ejes, habilidades y aprendizajes esperados en una organización original para una base de conocimiento educativa local. Antes de incorporar códigos OA exactos en archivos futuros, se deberá comprobar cada código directamente en el portal oficial.
