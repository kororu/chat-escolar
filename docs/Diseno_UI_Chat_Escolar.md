# Chat Escolar - Diseno UI Version 1

## 1. Objetivo visual

Crear una interfaz simple, moderna y clara, que pueda usar un nino, pero que no se vea demasiado infantil.

Debe servir tambien para adultos que acompanen el aprendizaje.

## 2. Principios de diseno

- Pocas opciones por pantalla.
- Texto grande y legible.
- Botones claros.
- Colores tranquilos.
- Navegacion simple.
- Sin exceso de decoracion.
- Sin sobrecargar al estudiante.
- Siempre mostrar donde esta el usuario.
- Mantener una estructura predecible.

## 3. Estilo recomendado

| Elemento | Recomendacion |
|---|---|
| Colores | Azul suave, verde suave, blanco, gris claro |
| Tipografia | Moderna, redonda, muy legible |
| Botones | Grandes, con texto claro |
| Iconos | Simples, no excesivos |
| Animaciones | Minimas |
| Tarjetas | Solo para temas, historial y videos |
| Modo oscuro | Opcional futuro |

## 4. Pantallas Version 1

### 4.1 Inicio

Debe mostrar:

- Logo o nombre: Chat Escolar.
- Frase corta: "Aprende paso a paso".
- Boton: Comenzar.
- Boton secundario: Ver historial.

### 4.2 Perfil del estudiante

Campos:

- Nombre.
- Curso.
- Edad aproximada.
- Nivel de apoyo.

Niveles:

- Normal.
- Explicacion simple.
- Tutor paciente.
- Lectura facil / apoyo TEA.

### 4.3 Selector de curso

Opciones:

- 1ro basico.
- 5to basico.
- 6to basico.

Cada opcion debe verse como tarjeta grande.

### 4.4 Selector de modo

Opciones:

- Estudiar para el colegio.
- Explorar mis intereses.
- Practicar.
- Ver videos.

### 4.5 Selector de materia

Solo en Modo Escolar:

- Ciencias Naturales.
- Matematica.
- Lenguaje.
- Historia.

### 4.6 Chat educativo

Debe incluir:

- Encabezado con curso, materia y modo.
- Area de mensajes.
- Campo para escribir.
- Boton enviar.
- Botones rapidos:
  - No entendi.
  - Explicalo mas facil.
  - Dame un ejemplo.
  - Hazme una pregunta.

Los mensajes del tutor deben separarse en bloques:

- Explicacion.
- Ejemplo.
- Mini resumen.
- Pregunta.

### 4.7 Historial

Debe mostrar tarjetas con:

- Fecha.
- Curso.
- Modo.
- Materia.
- Tema.
- Pregunta.
- Resumen.
- Estado: leido o pendiente.
- Favorito.

Acciones:

- Continuar.
- Marcar como leido.
- Marcar como pendiente.
- Favorito.

### 4.8 Videos

Debe mostrar:

- Tema.
- Titulo del video.
- Canal.
- Duracion estimada si esta disponible.
- Boton abrir.
- Advertencia: "Revisar con un adulto cuando sea necesario."

### 4.9 Panel apoderado basico

Debe mostrar:

- Temas estudiados.
- Preguntas pendientes.
- Favoritos.
- Temas sugeridos para repasar.
- Intereses frecuentes.

## 5. Flujo principal

```text
Inicio
> Perfil
> Curso
> Modo
> Materia o tema
> Chat
> Practica o videos
> Historial
```

## 6. Flujo "Continuar donde quede"

```text
Inicio
> Continuar donde quede
> Ver ultimo tema pendiente
> Releer explicacion
> Practicar una pregunta
```

## 7. Reglas de accesibilidad

- No mostrar textos muy largos de una sola vez.
- Usar contraste suficiente.
- Usar botones faciles de tocar en celular.
- Evitar ventanas emergentes innecesarias.
- Evitar sonidos automaticos.
- Permitir volver atras.
- Mantener historial visible.

## 8. Componentes iniciales

Frontend React:

- `App`
- `HomePage`
- `StudentProfile`
- `CourseSelector`
- `ModeSelector`
- `SubjectSelector`
- `ChatPage`
- `QuickActions`
- `HistoryPage`
- `VideoList`
- `ParentPanel`

## 9. Primer prototipo visual

El primer prototipo debe permitir navegar entre pantallas aunque todavia no tenga IA real.

Prioridad:

1. Inicio.
2. Perfil.
3. Selector de curso.
4. Selector de modo.
5. Chat.
6. Historial.
7. Videos.

