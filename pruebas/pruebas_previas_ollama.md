# Pruebas previas a integración Ollama

Fecha:
Versión/commit:
Probador: Ariel

## Objetivo

Registrar fallos actuales antes de corregir normalización, búsqueda, contexto, fuentes y perfiles.

---

## Prueba 1: hábitat con escritura normal

Perfil:
Curso:
Modo:
Pregunta:
¿Qué es un hábitat?

Resultado:
Fuente mostrada:
Estado mostrado:
¿Fue correcto? Sí
Observaciones:

---

## Prueba 2: hábitat con abreviatura

Pregunta:
q es habitat

Resultado:
Fuente mostrada:
Estado mostrado:
¿Fue correcto? Sí
Observaciones:

---

## Prueba 3: hábitat con error ortográfico

Pregunta:
ke es un abitad

Resultado:
Fuente mostrada:Chat Escolar
Hola, Erik. ¿Qué quieres aprender hoy?

Erik
ke es un abitad

Chat Escolar
Claro, Erik. Vamos paso a paso.

Explicacion corta:
Esta es una respuesta demo para 5° básico, en el modo Estudiar para el colegio.

Ejemplo:
Si estas estudiando Ciencias Naturales, podemos dividir el tema en partes pequenas.

Mini resumen:
Cuando un tema parece dificil, lo revisamos paso a paso.

Pregunta de practica:
Que parte de tu pregunta quieres revisar primero?

Respuesta demo del tutor
Resumen: Respuesta demo general para estudiar el tema paso a paso.
Estado mostrado:
¿Fue correcto? No
Observaciones:



## Prueba 4: tanques en modo escolar

Modo:
Escolar

Pregunta:
me gustaria saber de tanques de la segunda guerra

Resultado:
Fuente mostrada:
¿Mostró tabaco, circuitos, agua u otra fuente incorrecta?
Estado mostrado:
¿Fue correcto? No
Observaciones:
Claro, Erik. Vamos paso a paso.

Revisé la base local de 5° básico para ayudarte.

Información de apoyo:
exposición pasiva también causa daño. La nicotina puede generar dependencia. Prevenir no requiere culpabilizar a personas. Conceptos importantes Humo de segunda mano humo respirado por personas cercanas. Dependencia dificultad para dejar una sustancia pese a consecuencias. Nicotina sustancia del tabaco asociada a dependencia. Prevención acciones para evitar o reducir riesgo. Explicación completa para estudiante Las sustancias del humo irritan vías respiratorias y aumentan riesgos para distintos órganos. La exposición de niñas y niños debe evitarse. La dependencia es un problema de salud, no una falla moral. El estudiante puede reconocer situaciones de riesgo, alejarse si es posible y solicitar apoyo a un adulto. No debe confrontar de forma peligrosa ni manipular productos. Ejemplo…

Explicacion corta:
La Segunda Guerra Mundial fue una guerra muy grande que ocurrio entre 1939 y 1945.

Ejemplo:
Muchos paises participaron. Algunos querian conquistar y otros se unieron para detenerlos.

Mini resumen:
Fue una etapa dificil y triste que se estudia con respeto.

Pregunta de practica:
Quieres aprender primero sobre paises, fechas o consecuencias?

Respuesta apoyada en contenidos locales
Fuente local usada
Tabaco, humo y salud
Resumen: La Segunda Guerra Mundial ocurrio entre 1939 y 1945 y se estudia con respeto. Apoyada en el contenido local: Tabaco, humo y salud.
---

## Prueba 5: tanques en modo explorador

Modo:
Explorador

Pregunta:
me gustaria saber de tanques de la segunda guerra

Resultado:
Fuente mostrada:
Estado mostrado:
¿Dijo que no existe contenido local específico?
¿Inventó datos?
¿Fue correcto? No
Observaciones:
Erik. ¿Qué quieres aprender hoy?

Erik
me gustaria saber de tanques de la segunda guerra

Chat Escolar
Claro, Erik. Vamos paso a paso.

Revisé la base local de 5° básico para ayudarte.

Información de apoyo:
exposición pasiva también causa daño. La nicotina puede generar dependencia. Prevenir no requiere culpabilizar a personas. Conceptos importantes Humo de segunda mano humo respirado por personas cercanas. Dependencia dificultad para dejar una sustancia pese a consecuencias. Nicotina sustancia del tabaco asociada a dependencia. Prevención acciones para evitar o reducir riesgo. Explicación completa para estudiante Las sustancias del humo irritan vías respiratorias y aumentan riesgos para distintos órganos. La exposición de niñas y niños debe evitarse. La dependencia es un problema de salud, no una falla moral. El estudiante puede reconocer situaciones de riesgo, alejarse si es posible y solicitar apoyo a un adulto. No debe confrontar de forma peligrosa ni manipular productos. Ejemplo…

Explicacion corta:
La Segunda Guerra Mundial fue una guerra muy grande que ocurrio entre 1939 y 1945.

Ejemplo:
Muchos paises participaron. Algunos querian conquistar y otros se unieron para detenerlos.

Mini resumen:
Fue una etapa dificil y triste que se estudia con respeto.

Pregunta de practica:
Quieres aprender primero sobre paises, fechas o consecuencias?

Respuesta apoyada en contenidos locales
Fuente local usada
Tabaco, humo y salud
Resumen: La Segunda Guerra Mundial ocurrio entre 1939 y 1945 y se estudia con respeto. Apoyada en el contenido local: Tabaco, humo y salud.
---

## Prueba 6: pregunta de seguimiento

Secuencia:
1. me gustaria saber de tanques de la segunda guerra
2. cual fue el mas usado?

Resultado de la segunda pregunta:
Fuente mostrada:
¿Mantuvo contexto?
¿Usó fuente incorrecta?
¿Pidió aclaración?
¿Fue correcto? No
Observaciones:

Erik
cual fue el mas usado?

Chat Escolar
Claro, Erik. Vamos paso a paso.

Revisé la base local de 5° básico para ayudarte.

Información de apoyo:
rencia de alineación. La formulación completa y vigente debe comprobarse en el portal oficial antes de una publicación normativa. Ideas fundamentales Una fuente entrega energía al circuito. Los receptores producen efectos observables. Parte de la energía suele dispersarse como calor. La energía se conserva aunque cambie de forma. Conceptos importantes Energía capacidad asociada a cambios y procesos. Transformación cambio de una forma de energía a otra. Receptor componente que transforma energía eléctrica. Fuente dispositivo que mantiene una diferencia que impulsa corriente. Explicación completa para estudiante Una ampolleta transforma energía eléctrica principalmente en luz y calor; un motor, en movimiento y calor; un parlante, en sonido. “Gastar energía” en lenguaje cotidiano significa…

Explicacion corta:
Esta es una respuesta demo para 5° básico, en el modo Estudiar para el colegio.

Ejemplo:
Si estas estudiando Ciencias Naturales, podemos dividir el tema en partes pequenas.

Mini resumen:
Cuando un tema parece dificil, lo revisamos paso a paso.

Pregunta de practica:
Que parte de tu pregunta quieres revisar primero?

Respuesta apoyada en contenidos locales
Fuentes locales usadas
Energía eléctrica y transformaciones
Circuitos eléctricos simples
Distribución de agua dulce y salada en la Tierra
Resumen: Respuesta demo general para estudiar el tema paso a paso. Apoyada en el contenido local: Energía eléctrica y transformaciones.

## Prueba 7: cambio claro de tema

Secuencia:
1. me gustaria saber de tanques de la segunda guerra
2. que es un habitat

Resultado:
¿Heredó incorrectamente tanques?
¿Respondió sobre hábitat?
Fuente mostrada:
¿Fue correcto? No
Observaciones:

Chat Escolar
Hola, Erik. ¿Qué quieres aprender hoy?

Erik
me gustaria saber de tanques de la segunda guerra

Chat Escolar
Claro, Erik. Vamos paso a paso.

Revisé la base local de 5° básico para ayudarte.

Información de apoyo:
exposición pasiva también causa daño. La nicotina puede generar dependencia. Prevenir no requiere culpabilizar a personas. Conceptos importantes Humo de segunda mano humo respirado por personas cercanas. Dependencia dificultad para dejar una sustancia pese a consecuencias. Nicotina sustancia del tabaco asociada a dependencia. Prevención acciones para evitar o reducir riesgo. Explicación completa para estudiante Las sustancias del humo irritan vías respiratorias y aumentan riesgos para distintos órganos. La exposición de niñas y niños debe evitarse. La dependencia es un problema de salud, no una falla moral. El estudiante puede reconocer situaciones de riesgo, alejarse si es posible y solicitar apoyo a un adulto. No debe confrontar de forma peligrosa ni manipular productos. Ejemplo…

Explicacion corta:
La Segunda Guerra Mundial fue una guerra muy grande que ocurrio entre 1939 y 1945.

Ejemplo:
Muchos paises participaron. Algunos querian conquistar y otros se unieron para detenerlos.

Mini resumen:
Fue una etapa dificil y triste que se estudia con respeto.

Pregunta de practica:
Quieres aprender primero sobre paises, fechas o consecuencias?

Respuesta apoyada en contenidos locales
Fuente local usada
Tabaco, humo y salud
Resumen: La Segunda Guerra Mundial ocurrio entre 1939 y 1945 y se estudia con respeto. Apoyada en el contenido local: Tabaco, humo y salud.
Erik
que es un habitat

Chat Escolar
Claro, Erik. Vamos paso a paso.

Explicacion corta:
Un habitat es el lugar donde vive un ser vivo.

Ejemplo:
Un pez vive en el agua. Un cactus vive en el desierto.

Mini resumen:
El habitat es el hogar natural de un ser vivo.

Pregunta de practica:
Donde vive un pez?

Respuesta demo del tutor
Resumen: Un habitat es el lugar donde vive un ser vivo.

## Prueba 8: separación de perfiles

Perfil 1:
Erik

Pregunta:
me gustaria saber de tanques de la segunda guerra

Perfil 2:
Ariel

Pregunta:
cual fue el mas usado?

Resultado en Ariel:
¿Heredó contexto de Erik?
¿Fue correcto? Sí/No
Observaciones:

---

## Prueba 9: fuentes irrelevantes

Pregunta:
me gustaria saber de tanques de la segunda guerra

Fuentes incorrectas detectadas:
- Tabaco, humo y salud:
- Energía eléctrica:
- Circuitos:
- Agua:
- Otra:

Observaciones:

---

## Prueba 10: perfiles duplicados

Perfiles existentes:
- Ariel:
- Arieñ:
- Erik:

¿Existe forma de eliminar Arieñ?
¿Requiere confirmación?
¿Se puede cancelar?
Observaciones:

---

## Conclusión previa

Fallos confirmados:

1.
2.
3.

Prioridad antes de Ollama:

1.
2.
3.