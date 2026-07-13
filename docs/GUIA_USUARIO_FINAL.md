# Guía de usuario

## ¿Qué es Chat Escolar?

Es un tutor para estudiar en tu computador. Nexo puede ayudar con Matemática, Ciencias, Lenguaje e Historia usando contenido local del proyecto.

## Abrir y usar

1. Abre `iniciar_chat_escolar.bat`.
2. Espera a que aparezca la página de Chat Escolar.
3. Crea un perfil o elige uno guardado.
4. Escribe una pregunta y presiona **Enviar**.

El perfil demo permite probar rápidamente la aplicación. Muestra la invitación **Prueba una pregunta** y botones pequeños con ejemplos. En un perfil normal verás un saludo de Nexo y un espacio limpio: escribe tu pregunta para comenzar.

## Opciones del chat

- **Materia automática**: Nexo intenta reconocer la materia según tu pregunta. Puedes elegir una materia manualmente si lo prefieres.
- **Preguntas sugeridas**: sirven para probar ideas; aparecen directamente en el perfil demo. En un perfil normal no se muestran solas.
- **Historial**: guarda tus preguntas para retomarlas, marcarlas como pendientes o favoritas.
- **Modo básico**: funciona sin IA local y usa los contenidos disponibles en el equipo.
- **IA local**: si alguien instaló y activó Ollama, puede ayudar a generar explicaciones. Es opcional.

## Si demora o no abre

Las respuestas con IA local pueden tardar más en computadores modestos. Espera el mensaje de procesamiento y evita enviar la misma pregunta varias veces. Para cerrar, presiona `Ctrl+C` en las ventanas de Backend y Frontend o ciérralas.

Si no abre, ejecuta primero `scripts\00_verificar_entorno.bat`; si es el primer uso, ejecuta `scripts\01_instalar_dependencias.bat`. Si sigue fallando, confirma que no haya otra ventana usando los puertos 8000 o 5173.
