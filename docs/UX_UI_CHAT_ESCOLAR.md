# UX/UI de Chat Escolar

## Objetivo y público

La experiencia debe sentirse como un tutor local claro, amable y no excesivamente infantil. Sirve a estudiantes de 1.º a 8.º básico, apoderados, docentes y personas que requieren lectura fácil, incluidas necesidades TEA.

Principios: claridad, bajo ruido visual, pasos simples, respuestas ordenadas, legibilidad, consistencia y Nexo como apoyo, no distracción. Evitar textos largos, animaciones intensas y exceso de estímulos; mantener contraste, frases directas y botones claros.

## Nexo y conversación

Nexo se ubica normalmente a la izquierda, mira hacia la derecha y acompaña su globo con colita. No debe estar encerrado en círculo, con marco o fondo blanco: usa PNG transparente, puede sobresalir levemente del margen y nunca tapa texto. El usuario aparece a la derecha con avatar circular; las fuentes y metadatos son secundarios y no deben saturar la respuesta.

Assets actuales en `frontend/src/assets/nexo/`: `nexo_reposo.png`, `nexo_respuesta.png`, `nexo_pensando.png`, `nexo_pregunta.png`, `nexo_felicitacion.png`, `nexo_bienvenida.png`, y variantes `_matematica_01/_02`, `_ciencias_01/_02`, `_historia_01/_02`, `_lenguaje_01/_02`.

## Regla crítica: normal versus demo

- **Perfil normal**: Nexo saluda y ofrece un mensaje simple para comenzar; no muestra preguntas sugeridas automáticamente.
- **Perfil demo**: Nexo saluda, muestra **Prueba una pregunta** y sugerencias visibles como chips compactos.

Esta diferencia no debe romperse en cambios visuales futuros. Si existe historial, no se debe superponer un estado vacío sobre los mensajes.

## Espacios de mejora

Un diseñador puede evolucionar paleta, icono, splash, microinteracciones suaves de Nexo, responsive, onboarding, errores, jerarquía, espaciado, tarjetas y diseño del instalador. No debe comprometer lectura fácil, materia automática, el flujo simple, accesibilidad, legibilidad ni Nexo como guía.
