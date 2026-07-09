# Chat Escolar - Videos Curados Iniciales

## 1. Objetivo

Definir como se usaran videos educativos en Chat Escolar desde la Version 1.

Al inicio se recomienda usar una lista curada manual antes de conectar busqueda automatica con YouTube Data API.

## 2. Reglas de seleccion

Un video recomendado debe:

- Ser educativo.
- Tener lenguaje adecuado para ninos.
- Ser claro y no demasiado largo.
- Evitar sensacionalismo.
- Evitar violencia grafica.
- Tener relacion directa con el tema.
- Ser revisable por un adulto.

## 3. Reglas para temas sensibles

Para Segunda Guerra Mundial, tanques, armas o batallas:

- Preferir videos historicos educativos.
- Evitar videos con tono belico exagerado.
- Evitar miniaturas violentas.
- Evitar contenido grafico.
- Priorizar explicaciones para estudiantes.

## 4. Estructura sugerida de archivo JSON

```json
[
  {
    "id": "video-001",
    "curso": "5to_basico",
    "materia": "ciencias_naturales",
    "tema": "habitat",
    "titulo": "Que es un habitat",
    "canal": "Canal educativo revisado",
    "url": "https://youtube.com/...",
    "duracion_aproximada": "5 min",
    "estado": "pendiente_revision_adulto"
  }
]
```

## 5. Categorias iniciales

### Ciencias Naturales

Temas:

- Habitat.
- Ecosistemas.
- Cadenas alimentarias.
- Adaptaciones.
- Sistema Solar.

### Matematica

Temas:

- Fracciones.
- Multiplicacion.
- Division.
- Problemas matematicos.
- Geometria simple.

### Lenguaje

Temas:

- Comprension lectora.
- Idea principal.
- Resumen.
- Vocabulario.

### Historia

Temas:

- Linea de tiempo.
- Zonas de Chile.
- Pueblos originarios.

### Modo Explorador

Temas:

- Segunda Guerra Mundial explicada para ninos.
- Tanques como historia y tecnologia.
- Planetas.
- Agujeros negros.
- Naves espaciales.
- Robots.
- Dinosaurios.

## 6. Pantalla de videos

Cada tarjeta debe mostrar:

- Titulo.
- Tema.
- Canal.
- Duracion.
- Boton abrir.
- Estado de revision.

Mensaje recomendado:

```text
Este video es un apoyo para estudiar.
Si el tema es sensible, revisalo con un adulto.
```

## 7. Version 1

Para la primera version:

- Crear lista manual.
- Guardarla en archivo JSON.
- Mostrar videos dentro de la pantalla de videos.
- No depender todavia de busqueda automatica.

## 8. Version futura

Luego se puede agregar:

- YouTube Data API.
- Canales aprobados.
- Busqueda filtrada.
- Bloqueo de canales no aprobados.
- Panel para que el adulto apruebe videos.

