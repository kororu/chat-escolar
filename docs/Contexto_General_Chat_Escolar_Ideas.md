# Contexto general del proyecto Chat Escolar

Este archivo sirve para cargar en un chat separado dedicado a **ideas, dudas, mejoras, planificación pedagógica, contenidos educativos y visión futura** del proyecto.

El chat técnico principal debe quedar reservado para instalación, comandos, errores, backend, frontend, Git, GitHub, Codex y preparación del programa.

---

## 1. Nombre del proyecto

El proyecto se llama:

**Chat Escolar**

---

## 2. Objetivo principal

Chat Escolar será una aplicación local gratuita pensada para apoyar el aprendizaje escolar de estudiantes de enseñanza básica, especialmente niños con dificultades de comprensión o TEA.

El objetivo principal es ayudar a mi hijo a:

- estudiar materias escolares;
- hacer preguntas;
- repasar contenidos;
- practicar con ejercicios;
- explorar temas que le interesan;
- recibir explicaciones simples y adaptadas;
- fomentar la lectura y la curiosidad;
- usar una herramienta que pueda funcionar gratis y localmente.

---

## 3. Público objetivo

El usuario principal inicial es mi hijo, de aproximadamente 10 años, pensado principalmente para 5° básico.

También quiero que la app pueda servir para:

- estudiantes;
- apoderados;
- docentes.

La aplicación debe poder diferenciar el tipo de usuario para responder de forma personalizada.

Ejemplos:

### Si el usuario es estudiante

> Claro, Ariel. Vamos paso a paso.

### Si el usuario es apoderado

> Claro, Ariel. Te explico una forma simple para enseñárselo al estudiante.

### Si el usuario es docente

> Claro, profesora/profesor. Puedes trabajarlo con una explicación breve y una actividad simple.

---

## 4. Cursos contemplados desde el inicio

La primera versión debe contemplar:

- 1° básico;
- 5° básico;
- 6° básico.

Más adelante se podría extender hasta 8° básico.

---

## 5. Materias principales

Las materias principales del proyecto son:

- Lenguaje y Comunicación;
- Matemática;
- Ciencias Naturales;
- Historia, Geografía y Ciencias Sociales;
- Geometría como parte de Matemática;
- Biología como parte de Ciencias Naturales, cuando corresponda.

---

## 6. Enfoque inclusivo

Chat Escolar debe estar diseñado desde el inicio para niños con dificultades de comprensión o TEA.

Reglas importantes:

- usar frases cortas;
- explicar paso a paso;
- evitar textos largos;
- usar ejemplos concretos;
- hacer una pregunta a la vez;
- evitar sarcasmo o dobles sentidos;
- mantener una estructura predecible;
- corregir sin retar;
- reforzar positivamente;
- usar lenguaje adecuado al curso;
- ofrecer una versión más fácil si el estudiante no entiende.

---

## 7. Modos principales

Chat Escolar tendrá varios modos.

### 7.1. Modo Escolar

Para estudiar materias del colegio según curso, materia y tema.

Ejemplo:

- 5° básico;
- Ciencias Naturales;
- Hábitat y ecosistemas.

### 7.2. Modo Explorador

Para temas de interés personal del niño, aunque no estén directamente en la malla curricular.

Ejemplos:

- Segunda Guerra Mundial;
- tanques;
- aviones;
- naves espaciales;
- agujeros negros;
- robots;
- dinosaurios;
- tecnología;
- inventos;
- espacio.

Este modo debe fomentar la lectura y el interés por aprender.

### 7.3. Modo Práctica

Para hacer preguntas tipo prueba, verdadero/falso, alternativas, completar frases y ejercicios cortos.

### 7.4. Modo Videos

Para mostrar videos educativos curados o sugeridos, evitando contenido inadecuado.

---

## 8. Reglas para temas sensibles

Como a mi hijo le interesan temas como Segunda Guerra Mundial, tanques y máquinas militares, el chatbot debe poder explicarlos, pero con cuidado.

Reglas:

- explicar desde historia, tecnología e ingeniería;
- no glorificar la guerra;
- no usar detalles gráficos;
- no presentar la violencia como entretenimiento;
- recordar que las guerras causan sufrimiento;
- adaptar todo a la edad del estudiante.

Ejemplo de tono:

> Los tanques fueron máquinas usadas en guerras. Podemos estudiarlos para aprender historia, tecnología e ingeniería, pero también es importante recordar que las guerras causan mucho daño.

---

## 9. Historial

Se decidió agregar historial de preguntas desde la versión inicial.

El historial debe permitir:

- ver preguntas anteriores;
- revisar respuestas;
- marcar como leído o pendiente;
- marcar favoritos;
- continuar donde quedó;
- ayudar al apoderado a ver qué temas se están estudiando.

Para la primera versión basta con un historial simple. Más adelante se puede mejorar con filtros por materia, curso, favoritos y pendientes.

---

## 10. Perfiles personalizados

Se propuso agregar un inicio con perfiles locales, sin contraseña por ahora.

Datos del perfil:

- nombre;
- tipo de usuario:
  - estudiante;
  - apoderado;
  - docente;
- curso asociado:
  - 1° básico;
  - 5° básico;
  - 6° básico.

Esto permitirá personalizar saludos y respuestas.

---

## 11. Mascota futura

Se quiere dejar preparado un espacio para una mascota o personaje del proyecto.

La mascota podría aparecer en la pantalla de inicio y saludar con un globo tipo cómic.

Por ahora no se diseñará la mascota. Más adelante se hará un boceto y se incorporará al diseño.

Ejemplo:

> ¡Hola, Ariel! ¿Qué quieres aprender hoy?

---

## 12. Uso gratuito

Por ahora el proyecto debe funcionar gratis.

Eso significa:

- no usar OpenAI API por ahora;
- no depender de servicios pagados;
- usar backend local;
- usar frontend local;
- usar SQLite local;
- usar videos curados;
- usar respuestas demo o contenidos preparados;
- más adelante usar IA local con Ollama.

---

## 13. IA local futura

Se decidió que, para poder preguntar temas más libres sin pagar API, se evaluará usar **Ollama** como IA local opcional.

La app debe seguir funcionando aunque Ollama no esté instalado.

Modo futuro:

- Tutor demo local;
- IA local Ollama opcional.

Para un PC con 12 GB de RAM o un poco más, se recomienda empezar con modelos pequeños o medianos, como:

- llama3.2:3b;
- qwen2.5:3b;
- gemma 3B/4B;
- evitar modelos grandes al inicio.

La IA local se usará más adelante, después de tener una demo local estable.

---

## 14. Base de conocimiento local

Más adelante se crearán bases de conocimiento en Markdown para cursos completos.

Cursos planificados:

- 1° básico;
- 5° básico;
- 6° básico.

Luego se integrarán en el proyecto.

Por ahora todavía no está implementado el lector de `.md`.

La base debe estar alineada con el Currículum Nacional chileno actualizado al 2026, pero sin copiar textos escolares completos ni material protegido.

El contenido debe ser original, adaptado para estudiantes, apoderados y docentes.

---

## 15. Estructura deseada para contenidos futuros

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

Cada tema debería tener:

- explicación para estudiante;
- explicación para apoderado;
- explicación para docente;
- palabras clave;
- ejemplos;
- actividades;
- preguntas;
- respuestas;
- errores comunes;
- versión más fácil;
- mini resumen;
- conexiones con otros temas.

---

## 16. Financiamiento futuro

Se conversó que el proyecto sí podría tener futuro si primero existe una demo funcional, útil y probada con estudiantes, apoderados o docentes.

Posibles caminos futuros:

- demo educativa para profesores;
- versión local gratuita;
- financiamiento por innovación educativa;
- apoyo de instituciones;
- versión con IA local;
- versión con IA en la nube si algún día hay presupuesto.

Pero por ahora el foco es construir una versión local gratuita y útil.

---

## 17. Uso recomendado de este chat

Este chat debe usarse para:

- dudas generales;
- ideas de mejora;
- planificación;
- contenido educativo;
- estrategia;
- preguntas sobre IA local;
- posibles funciones futuras;
- revisión de enfoque pedagógico;
- análisis de valor del proyecto;
- preparación de contenidos escolares.

El chat técnico principal quedará reservado para:

- instalación;
- comandos;
- Git;
- backend;
- frontend;
- Codex;
- errores;
- commits;
- preparación del programa.
