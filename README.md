# Chat Escolar

Aplicación educativa local con tutor demo, perfiles, historial y recursos curados.

## Cómo iniciar Chat Escolar en Windows

1. Ejecuta `scripts\00_verificar_entorno.bat`.
2. En el primer uso, ejecuta `scripts\01_instalar_dependencias.bat`.
3. Ejecuta `iniciar_chat_escolar.bat` desde la raíz del proyecto.
4. Abre `http://localhost:5173/` si el navegador no aparece solo.

Los scripts mantienen rutas relativas y abren backend/frontend en ventanas separadas. Ollama es opcional: la aplicación funciona en modo Básico si no está disponible. Consulta la [guía de ejecución en Windows](docs/Guia_Ejecucion_Windows_Chat_Escolar.md) para uso diario, cambio de PC y solución de problemas.

### Scripts disponibles

| Archivo | Uso |
| --- | --- |
| `scripts\00_verificar_entorno.bat` | Revisa Git, Node, npm, Python, las carpetas del proyecto y Ollama opcional. |
| `scripts\01_instalar_dependencias.bat` | Crea `backend\.venv` e instala las dependencias del backend y frontend. |
| `scripts\02_iniciar_backend.bat` | Inicia FastAPI en `http://127.0.0.1:8000`. |
| `scripts\03_iniciar_frontend.bat` | Inicia Vite en `http://localhost:5173/`. |
| `scripts\04_abrir_chat_escolar.bat` | Abre el frontend en el navegador. |
| `iniciar_chat_escolar.bat` | Inicia backend y frontend en ventanas separadas y abre el navegador. |

El backend está activo si `http://127.0.0.1:8000/health` responde. El frontend está activo si abre `http://localhost:5173/`. Si el puerto 8000 o 5173 está ocupado, detén la instancia anterior con `Ctrl+C` o cierra su ventana y vuelve a iniciar.

### Inicio manual para desarrollo

En dos terminales PowerShell separadas, desde la raíz del proyecto:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm run dev -- --host localhost --port 5173 --strictPort
```

Para detener cualquiera de los dos procesos, presiona `Ctrl+C` en su terminal.

## Base de conocimiento local

Chat Escolar puede leer archivos Markdown desde `contenidos/` y utilizarlos como apoyo para sus respuestas. La búsqueda funciona localmente, sin OpenAI API ni servicios pagados.

La base local reconoce carpetas curriculares Markdown de 1° a 8° básico. El backend centraliza los mapeos de cursos y materias para que el selector, la búsqueda y la futura capa de IA local usen la misma convención de carpetas.

La materia inicia en **Automática**: Chat Escolar detecta de forma local Ciencias Naturales, Matemática, Lenguaje o Historia con palabras clave normalizadas y busca primero en esa materia. La selección manual sigue disponible y se respeta. Si no hay suficiente contenido verificado, la búsqueda amplía de forma controlada a otras materias sin relajar sus umbrales de relevancia. La respuesta incluye la materia detectada como dato secundario y permite seleccionar la variante de Nexo correspondiente.

La guía para organizar, agregar y probar estos materiales está en [docs/README_CONTENIDOS_LOCALES.md](docs/README_CONTENIDOS_LOCALES.md).

El buscador valida relevancia antes de mostrar una fuente: pondera títulos, temas, palabras clave y encabezados, evita índices o compendios como fuente principal cuando corresponde, y separa el contenido curricular del futuro Modo Explorador. Las coincidencias débiles o relacionadas no se presentan como respaldo verificado.

La recuperación normaliza tildes y errores escolares frecuentes, descarta palabras de consulta poco informativas y usa equivalencias acotadas (por ejemplo, fracción/numerador/denominador o fotosíntesis/plantas/luz). Cada resultado conserva internamente términos coincidentes, coincidencia exacta, confianza y motivo. `local_verified` exige señal fuerte; una mención secundaria queda como `local_related`, las coincidencias débiles como `local_low_confidence` y la ausencia útil como `no_local_content`.

El curso asociado al perfil se usa como preferencia inicial, pero la búsqueda respeta siempre el curso activo que envía el frontend. Si el estudiante cambia de 5° a 6° básico en el selector, `/chat/demo` busca en 6° básico aunque el perfil siga asociado a 5°.

El selector incluye **Todos los cursos** para buscar en toda la base Markdown local. En Modo Escolar se busca primero en el curso activo; si no hay fuente local verificada, el backend puede revisar todos los cursos y marcar claramente `source_course` cuando la fuente viene de otro nivel. En Modo Explorador también se consulta la base local global antes de usar una respuesta demo de respaldo.

`POST /chat/demo` devuelve metadatos de procedencia como `effective_course`, `source_course`, `source_subject`, `used_local_content`, `content_sources` y `found_in_other_course`. El frontend muestra avisos simples para fuente verificada, tema relacionado, baja confianza, ausencia de contenido local y fuentes encontradas en otro curso.

Las preguntas de seguimiento usan una memoria local breve aislada por perfil y conversación. El historial conserva siempre el texto original del estudiante; las reconstrucciones se usan solo internamente para buscar contenido o pedir una aclaración segura.

El backend deja preparado un contrato `provider`/`ai_context` para una futura integración con Ollama, pero esta versión no llama Ollama ni OpenAI API.

## IA local opcional con Ollama

Chat Escolar puede usar Ollama de forma opcional, local y gratuita. El modelo predeterminado es `qwen3.5:2b`; `qwen3.5:4b` queda soportado cambiando la variable local `OLLAMA_MODEL`, sin descargarlo automáticamente. No se usa OpenAI API ni servicios externos.

```powershell
ollama pull qwen3.5:2b
ollama list
```

Con el backend iniciado, revisa `http://127.0.0.1:8000/ai/status`. Si Ollama o el modelo no están disponibles, la aplicación continúa con el tutor demo. Las respuestas pueden indicar `ollama_with_local_content` cuando la IA explica una fuente Markdown verificada, u `ollama_generated` cuando Modo Explorador ofrece una explicación general sin fuente local verificada. No se guardan prompts completos: el historial guarda proveedor, procedencia y fuentes utilizadas.

### Control de IA local

La configuración persistente está en `backend/data/settings.json` y se ajusta desde la tarjeta **IA local**. El modo inicial es **Básico**, que no llama a Ollama y usa contenidos locales o el fallback educativo para priorizar rapidez en equipos modestos. **Automático** permite usar Ollama con un timeout configurable (15, 25 o 40 segundos; 25 s predeterminado). **Solo Explorar** permite Ollama únicamente en *Explorar mis intereses* o al consultar *Todos los cursos*; el modo escolar sigue priorizando contenido local.

`GET /settings` muestra la preferencia y `PATCH /settings` la actualiza localmente. `GET /ai/status` incluye el modo, modelo, timeout y disponibilidad. Todo funciona sin servicios externos ni API de OpenAI; si Ollama está apagado o alcanza el timeout, el chat conserva el fallback local y muestra su procedencia.

## Indicador de procesamiento

Al enviar una pregunta, el chat muestra una burbuja temporal de procesamiento con un indicador visual. El botón Enviar queda deshabilitado para evitar duplicados y, después de 10 y 30 segundos, el aviso informa que un equipo modesto puede tardar más. La burbuja no se guarda en el historial y desaparece al recibir la respuesta o un error.

Cuando Ollama está disponible, la interfaz avisa que la IA local está trabajando, pero nunca muestra razonamiento interno ni texto `Thinking`. Streaming, cancelación, progreso real por etapas y cola de solicitudes quedan como mejoras futuras.

Cada respuesta nueva también muestra debajo el tiempo total de procesamiento, por ejemplo `Procesado en 3,2 s`. El dato incluye búsqueda local, generación opcional con Ollama y cualquier respaldo demo; sirve para reconocer respuestas lentas sin exponer métricas internas ni razonamiento.

## Fallback educativo local

Cuando existe una fuente Markdown verificada pero Ollama no responde o llega al timeout, Chat Escolar usa `local_content_fallback`. Construye una explicación desde secciones educativas del material local (respuesta breve, explicación, ejemplo, resumen y práctica), mantiene la fuente visible y evita reemplazarla por una respuesta demo genérica. `demo_fallback` queda reservado para preguntas sin contenido local útil. La duración mostrada incluye el intento de Ollama y este respaldo, sin revelar razonamiento interno.

## Adaptación por curso y lectura fácil

`backend/educational_level.py` centraliza el curso, edad aproximada, nivel lector, cantidad de ideas, límite de palabras y una sola pregunta de práctica. El fallback local y los prompts de Ollama usan estas reglas: 1°–2° básico recibe frases muy cortas; 3°–4° explicaciones simples; 5°–6° conceptos escolares aclarados; y 7°–8° mayor precisión y relaciones entre ideas. La estructura mantiene bloques predecibles, ejemplos concretos y lenguaje claro sin infantilizar.

Las respuestas pedagógicas mantienen el orden **Explicación corta, Ejemplo, Mini resumen y una sola pregunta de práctica**. El fallback local limpia los textos curriculares para no mostrar OA, metadatos ni instrucciones editoriales dentro de la explicación. Ante una pregunta ambigua sin contexto, pide una aclaración simple con ejemplos; los errores de escritura se interpretan de forma amable mediante la normalización local.

## Nexo, identidad visual del chat

Nexo es el tutor visual de Chat Escolar. Las preguntas del perfil y las respuestas de Nexo usan globos distintos; durante el procesamiento se muestra la variante de Nexo pensando. La pantalla de perfiles incorpora la variante `nexo_bienvenida.png` como imagen principal. Las variantes y rutas de assets están documentadas en [docs/README_NEXO_VISUAL.md](docs/README_NEXO_VISUAL.md). Mientras no existan imágenes finales, la interfaz usa un placeholder seguro.

## Perfiles locales

Los perfiles se pueden crear, cambiar y eliminar desde la pantalla de selección. También pueden usar un avatar opcional guardado solo en el equipo; sin avatar se muestra la inicial del nombre. Eliminar un perfil requiere confirmación y borra únicamente su historial, favoritos, pendientes, contexto conversacional local y avatar asociado. Consulta [docs/README_PERFILES_LOCALES.md](docs/README_PERFILES_LOCALES.md).

## Demo rápida

La bienvenida ofrece **Usar demo rápida**. Crea o reutiliza el perfil local `Estudiante Demo` (5° básico) para mostrar la aplicación sin configurar un perfil manualmente. El chat incluye preguntas sugeridas y una guía breve; las sugerencias usan Materia automática, por lo que permiten probar distintos temas sin cambiar el selector.

## Autoría

Chat Escolar es un proyecto desarrollado por **Ariel Ponce**.

Versión actual: `0.1.0`
Año: `2026`

La marca de autoría no debe eliminarse de las versiones de prueba distribuidas por el autor.

Consulta [docs/AUTORIA_Y_VERSIONADO.md](docs/AUTORIA_Y_VERSIONADO.md) para conocer dónde se centraliza esta información y cómo actualizar la versión.
