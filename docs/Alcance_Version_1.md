# Chat Escolar - Alcance Version 1

## 1. Objetivo de la Version 1

Construir la primera version funcional de **Chat Escolar**, una aplicacion web/PWA educativa, simple y moderna, que permita a un estudiante de ensenanza basica estudiar materias escolares y explorar temas de interes con ayuda de un tutor IA inclusivo.

La Version 1 debe servir como base real del proyecto, no solo como maqueta. Debe permitir probar conversaciones, materias, cursos, videos, preguntas de practica y reglas de lenguaje adaptado.

## 2. Principios de la Version 1

- Simple antes que compleja.
- Clara antes que llamativa.
- Util para ninos y adultos.
- No infantil en exceso.
- Pensada para lectura facil.
- Adaptada a estudiantes con dificultades de comprension o TEA.
- Con explicaciones por edad, curso y nivel.
- Con modo escolar y modo explorador desde el inicio.
- Con videos educativos desde la primera version.

## 3. Publico inicial

| Tipo de usuario | Necesidad |
|---|---|
| Estudiante | Preguntar, estudiar, practicar y explorar intereses |
| Apoderado | Acompanar el estudio y revisar temas trabajados |
| Adulto de apoyo | Usar explicaciones simples para ayudar al estudiante |

## 4. Cursos incluidos

La Version 1 incluira selector de curso con:

| Curso | Nivel de respuesta esperado |
|---|---|
| 1ro basico | Muy simple, frases cortas, apoyo a lectura inicial |
| 5to basico | Curso principal de referencia, explicaciones claras para 10 anos |
| 6to basico | Un poco mas avanzado, manteniendo lenguaje simple |

El foco de desarrollo y pruebas iniciales sera **5to basico**.

## 5. Materias incluidas

| Materia | Incluida V1 | Comentario |
|---|---:|---|
| Ciencias Naturales | Si | Prioridad alta para primeros contenidos |
| Matematica | Si | Resolucion paso a paso |
| Lenguaje | Si | Fomento lector y comprension |
| Historia | Si | Explicaciones cuidadas y lineas de tiempo simples |

## 6. Modos incluidos

### 6.1 Modo Escolar

Permite estudiar segun:

- Curso.
- Materia.
- Tema.
- Nivel de apoyo.

Funciones:

- Explicacion corta.
- Ejemplo facil.
- Mini resumen.
- Pregunta de practica.
- Correccion amable.
- Opcion de explicar mas facil.

### 6.2 Modo Explorador

Permite preguntar sobre temas fuera de la malla curricular.

Temas iniciales sugeridos:

- Segunda Guerra Mundial.
- Tanques.
- Aviones.
- Barcos.
- Naves espaciales.
- Planetas.
- Agujeros negros.
- Robots.
- Dinosaurios.
- Inventos.
- Tecnologia.

Regla principal:

El sistema debe responder de acuerdo a la edad y comprension del estudiante, sin usar lenguaje de adulto si el perfil es infantil.

### 6.3 Modo Practica

Permite practicar con preguntas simples.

Tipos de pregunta para V1:

- Alternativas.
- Verdadero o falso.
- Respuesta corta.

Regla:

Debe presentar una pregunta a la vez.

### 6.4 Modo Videos

Permite mostrar videos educativos relacionados con el tema.

Implementacion inicial recomendada:

1. Lista curada de videos por tema.
2. Luego conexion con YouTube Data API.

Reglas:

- Videos cortos cuando sea posible.
- Canales educativos confiables.
- Evitar contenido violento o sensacionalista.
- Para temas historicos sensibles, revisar con mas cuidado.

## 7. Funciones obligatorias V1

| Funcion | Prioridad | Descripcion |
|---|---|---|
| Pantalla de inicio | Alta | Entrada simple a la aplicacion |
| Perfil del estudiante | Alta | Nombre, curso, edad aproximada y nivel de apoyo |
| Selector de curso | Alta | 1ro, 5to y 6to basico |
| Selector de modo | Alta | Escolar, Explorador, Practica, Videos |
| Selector de materia | Alta | Ciencias, Matematica, Lenguaje, Historia |
| Chat educativo | Alta | Conversacion con tutor IA |
| Boton "No entendi" | Alta | Reexplica de forma mas simple |
| Boton "Explicalo mas facil" | Alta | Baja dificultad y acorta respuesta |
| Boton "Dame un ejemplo" | Alta | Entrega ejemplo concreto |
| Boton "Hazme una pregunta" | Alta | Genera una pregunta de practica |
| Correccion amable | Alta | Corrige sin retar |
| Videos educativos | Alta | Desde V1, primero con lista curada |
| Historial simple | Media | Guarda temas estudiados |
| Panel apoderado basico | Media | Resumen simple de temas vistos |

## 8. Funciones que quedan fuera de V1

Estas funciones no deben bloquear la primera version:

- App Android nativa.
- Sistema de pagos.
- Multiples colegios.
- Cuentas familiares avanzadas.
- Panel estadistico complejo.
- Reconocimiento de voz.
- Lectura en voz alta.
- Subir foto de tarea.
- Generacion avanzada de PDF.
- Gamificacion completa.
- Modo offline completo.

Pueden ser Version 2 o posteriores.

## 9. Interfaz esperada

La interfaz debe ser:

- Simple.
- Moderna.
- Limpia.
- Clara para ninos.
- No demasiado infantil.
- Util para adultos.
- Con texto grande y legible.
- Con botones claros.
- Con pocas opciones visibles al mismo tiempo.

No usar:

- Pantallas sobrecargadas.
- Demasiadas animaciones.
- Textos largos.
- Estilo excesivamente infantil.
- Colores muy fuertes o distractores.

## 10. Pantallas V1

### Pantalla 1: Inicio

Debe mostrar:

- Nombre: Chat Escolar.
- Boton para comenzar.
- Acceso al perfil del estudiante.

### Pantalla 2: Perfil del estudiante

Campos:

- Nombre.
- Curso.
- Edad aproximada.
- Nivel de apoyo:
  - Normal.
  - Explicacion simple.
  - Tutor paciente.
  - Lectura facil / apoyo TEA.

### Pantalla 3: Selector de modo

Opciones:

- Estudiar para el colegio.
- Explorar mis intereses.
- Practicar.
- Ver videos.

### Pantalla 4: Selector de materia

Disponible en Modo Escolar:

- Ciencias Naturales.
- Matematica.
- Lenguaje.
- Historia.

### Pantalla 5: Chat

Debe incluir:

- Area de conversacion.
- Campo para escribir.
- Boton enviar.
- Botones rapidos:
  - No entendi.
  - Explicalo mas facil.
  - Dame un ejemplo.
  - Hazme una pregunta.

### Pantalla 6: Videos

Debe mostrar:

- Titulo del tema.
- Lista de videos sugeridos.
- Canal o fuente.
- Boton para abrir video.
- Advertencia simple: "Videos recomendados como apoyo. Revisar con un adulto cuando sea necesario."

### Pantalla 7: Historial simple

Debe mostrar:

- Fecha.
- Curso.
- Materia o modo.
- Tema estudiado.
- Ultima actividad.

### Pantalla 8: Panel apoderado basico

Debe mostrar:

- Temas estudiados.
- Dificultades detectadas.
- Temas sugeridos para repasar.
- Intereses explorados.

## 11. Reglas de respuesta del tutor

El tutor debe:

- Responder segun curso y edad.
- Usar frases cortas.
- Explicar una idea por bloque.
- Usar ejemplos concretos.
- Evitar tecnicismos innecesarios.
- Preguntar una cosa a la vez.
- Corregir con paciencia.
- No retar ni ridiculizar.
- Repetir si el estudiante no entiende.
- Ofrecer practica.
- Fomentar lectura con textos breves.

## 12. Formato base de respuesta

```text
Explicacion corta:
[respuesta simple]

Ejemplo:
[ejemplo concreto]

Mini resumen:
[idea principal]

Pregunta:
[una pregunta simple]
```

## 13. Reglas para Modo Explorador

El Modo Explorador debe permitir aprender por curiosidad.

Para temas complejos:

- Dividir en partes.
- Usar palabras simples.
- Proponer rutas de aprendizaje.
- Relacionar con materias escolares cuando sea posible.

Ejemplo:

Si el estudiante pregunta por tanques, se puede conectar con:

- Historia.
- Tecnologia.
- Matematica: peso, velocidad, distancia.
- Lenguaje: lectura comprensiva.
- Ciencias: energia, materiales, motores.

## 14. Reglas para guerra, tanques y armas

Cuando el tema sea guerra, tanques, armas o batallas:

- Explicar de forma historica y educativa.
- Evitar glorificar la violencia.
- No entregar detalles graficos.
- No convertir la guerra en celebracion.
- Recordar que las guerras causan sufrimiento.
- Enfocar maquinas como tecnologia e ingenieria.
- Mantener contenido adecuado para ninos.

## 15. Contenido inicial recomendado

### Ciencias Naturales - 5to basico

- Habitat.
- Ecosistemas.
- Seres vivos.
- Cadenas alimentarias.
- Adaptaciones.

### Matematica - 5to basico

- Operaciones basicas.
- Problemas paso a paso.
- Fracciones.
- Geometria simple.
- Medicion.

### Lenguaje - 5to basico

- Comprension lectora.
- Idea principal.
- Personajes.
- Resumen.
- Vocabulario.

### Historia - 5to basico

- Linea de tiempo.
- Chile y sus zonas.
- Pueblos originarios.
- Historia explicada simple.

### Modo Explorador

- Segunda Guerra Mundial para 10 anos.
- Tanques como historia y tecnologia.
- Espacio.
- Naves espaciales.
- Agujeros negros.
- Robots.

## 16. Arquitectura tecnica V1

### Frontend

- React.
- Vite.
- Aplicacion web instalable como PWA.

### Backend

- Python.
- FastAPI.

### Base de datos

- SQLite para desarrollo inicial.

### IA

- OpenAI API.
- Responses API.
- Prompt interno de Chat Escolar.

### Videos

- Lista curada en archivos JSON o Markdown al inicio.
- YouTube Data API despues de validar el flujo.

## 17. Entregables de la Version 1

| Entregable | Descripcion |
|---|---|
| Documento de contexto | Base general del proyecto |
| Alcance V1 | Este documento |
| Prompt tutor | Instrucciones internas del chatbot |
| Prototipo UI | Pantallas basicas navegables |
| Backend inicial | API para preguntas y respuestas |
| Contenidos iniciales | Material base por curso, materia y tema |
| Lista curada de videos | Videos educativos iniciales |
| Historial simple | Registro basico de temas |
| Guia de instalacion | Pasos para preparar el PC nuevo |

## 18. Criterios de exito V1

La Version 1 sera exitosa si:

- El estudiante puede entrar y elegir curso.
- Puede elegir modo escolar o explorador.
- Puede hacer preguntas.
- El tutor responde segun edad y curso.
- Las respuestas son cortas y comprensibles.
- Puede pedir "explicalo mas facil".
- Puede practicar con una pregunta.
- Puede ver videos recomendados.
- El adulto puede revisar temas estudiados.
- El sistema se puede ejecutar en el PC de desarrollo.

## 19. Orden de desarrollo recomendado

1. Crear documentos base.
2. Crear guia de preparacion del PC.
3. Crear prompt interno definitivo.
4. Crear diseno UI.
5. Crear estructura del repositorio.
6. Crear frontend inicial.
7. Crear backend inicial.
8. Crear contenidos iniciales.
9. Conectar IA.
10. Agregar lista curada de videos.
11. Guardar historial simple.
12. Probar con preguntas reales.
13. Ajustar lenguaje y diseno.

## 20. Estado actual

Decisiones confirmadas:

| Punto | Estado |
|---|---|
| Nombre Chat Escolar | Confirmado |
| Cursos 1ro, 5to, 6to | Confirmado |
| Materias iniciales | Confirmado |
| Modo Explorador V1 | Confirmado |
| Videos V1 | Confirmado |
| Interfaz simple y moderna | Confirmado |
| Enfoque inclusivo / TEA | Confirmado |
| Desarrollo en otro PC | Confirmado |

