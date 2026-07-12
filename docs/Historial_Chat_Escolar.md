# Chat Escolar - Historial de Preguntas y Continuidad

## 1. Objetivo

El historial de preguntas permitira que Chat Escolar recuerde lo que el estudiante pregunto, que temas estudio, que explicaciones quedaron pendientes y que contenidos fueron marcados como importantes.

Esta funcion debe existir desde la Version 1.

## 2. Por que es importante

- Permite revisar preguntas anteriores.
- Ayuda si el estudiante olvido leer una explicacion.
- Permite retomar un tema sin empezar desde cero.
- Ayuda al apoderado a ver que temas se estan trabajando.
- Permite detectar dificultades repetidas.
- Fomenta la lectura mediante relectura.
- Da continuidad y estructura para estudiantes con dificultades o TEA.

## 3. Datos a guardar

| Campo | Descripcion |
|---|---|
| ID | Identificador interno |
| Fecha y hora | Momento de la pregunta |
| Estudiante | Perfil usado |
| Curso | 1ro, 5to o 6to basico |
| Edad aproximada | Edad usada para adaptar respuesta |
| Nivel de apoyo | Normal, simple, tutor paciente o lectura facil |
| Modo | Escolar, Explorador, Practica o Videos |
| Materia | Materia si corresponde |
| Tema | Tema principal |
| Pregunta | Texto del estudiante |
| Resumen | Resumen corto de respuesta |
| Respuesta completa | Explicacion del tutor |
| Estado | Leido o pendiente |
| Favorito | Si o no |
| ID de conversación | Agrupa turnos del mismo perfil sin mezclar otras conversaciones |
| Pregunta normalizada | Versión interna para reconocer errores leves y abreviaturas |
| Pregunta contextual | Consulta interna reconstruida para buscar contenido; no reemplaza el texto visible |
| Tema activo | Tema reciente usado solo dentro de la misma conversación y perfil |
| Confianza de contexto | Seguridad de la reconstrucción antes de usarla |

## 4. Funciones Version 1

- Ver historial.
- Buscar por palabra.
- Filtrar por curso.
- Filtrar por materia.
- Filtrar por modo.
- Ver pendientes.
- Ver favoritos.
- Marcar como leido.
- Marcar como pendiente.
- Marcar como favorito.
- Volver a estudiar.
- Continuar donde quedo.

## 5. Continuar donde quede

Ejemplo:

```text
La ultima vez estabas aprendiendo sobre agujeros negros.
Te quedo pendiente leer una explicacion corta.
Quieres continuar?
```

Otro ejemplo:

```text
Ayer practicaste fracciones.
Te costo distinguir numerador y denominador.
Quieres repasarlo con un ejemplo facil?
```

## 6. Vista para el estudiante

Ejemplo de tarjeta:

```text
Tema: Agujeros negros
Modo: Explorador
Fecha: 8 de julio
Estado: Pendiente

Pregunta:
Que es un agujero negro?

Resumen:
Es una zona del espacio con mucha gravedad.

[Continuar] [Marcar como leido] [Favorito]
```

## 7. Vista para el apoderado

Debe mostrar:

- Temas mas preguntados.
- Materias revisadas.
- Preguntas pendientes.
- Favoritos.
- Temas que conviene repasar.
- Intereses frecuentes.

## 8. Privacidad

Como el historial contiene actividad de un menor:

- No debe ser publico.
- No debe compartirse automaticamente.
- Debe guardar solo lo necesario.
- Debe permitir borrar preguntas.
- Debe permitir borrar historial.

## 9. Tabla SQLite sugerida

```sql
CREATE TABLE chat_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_name TEXT,
  course TEXT NOT NULL,
  approximate_age INTEGER,
  support_level TEXT,
  mode TEXT NOT NULL,
  subject TEXT,
  topic TEXT,
  question TEXT NOT NULL,
  answer_summary TEXT,
  answer_full TEXT,
  status TEXT DEFAULT 'pendiente',
  is_favorite INTEGER DEFAULT 0,
  created_at TEXT NOT NULL
);
```

## 10. Endpoints sugeridos

| Metodo | Ruta | Uso |
|---|---|---|
| GET | /history | Listar historial |
| GET | /history/{id} | Ver entrada |
| POST | /history | Guardar entrada |
| PATCH | /history/{id}/status | Cambiar leido/pendiente |
| PATCH | /history/{id}/favorite | Marcar favorito |
| DELETE | /history/{id} | Borrar entrada |
| GET | /history/continue | Continuar donde quedo |

## 11. Prioridad

Prioridad: **Alta para Version 1**.

Debe ser simple, pero debe existir desde el inicio.

## 12. Memoria conversacional local

Chat Escolar conserva el mensaje original en el historial y guarda datos internos de contexto de forma separada. Para cada perfil y conversación utiliza una ventana máxima de seis interacciones recientes, dando prioridad al turno inmediatamente anterior.

Una pregunta breve puede reconstruirse solo cuando hay un tema activo confiable. Por ejemplo, después de “me gustaría saber de tanques de la Segunda Guerra”, “¿cuál fue el más usado?” se busca internamente como una pregunta sobre tanques de ese período.

Si cambia claramente el tema, por ejemplo a “¿qué es un hábitat?”, no se hereda el tema anterior. Si no hay un antecedente suficiente, el tutor solicita una aclaración en lugar de inventar una relación.

La memoria está aislada por `profile_id` y `conversation_id`; nunca se consulta el historial de otro perfil. Actualmente no existe contexto conversacional avanzado ni integración con Ollama.

