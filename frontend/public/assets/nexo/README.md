# Assets de Nexo

Reemplaza los placeholders CSS dejando imágenes PNG con estos nombres:

- `nexo_reposo.png`
- `nexo_respuesta.png`
- `nexo_pensando.png`
- `nexo_pregunta.png`
- `nexo_felicitacion.png`
- `nexo_matematica_01.png`
- `nexo_matematica_02.png`
- `nexo_ciencias_01.png`
- `nexo_ciencias_02.png`
- `nexo_historia_01.png`
- `nexo_historia_02.png`
- `nexo_lenguaje_01.png`
- `nexo_lenguaje_02.png`
- `nexo_bienvenida.png`

Los assets reales ahora se importan desde `frontend/src/assets/nexo/` mediante Vite. Este directorio público se conserva solo como referencia y no es necesario copiar PNG aquí.

Cada respuesta nueva elige una variante de materia una sola vez y la conserva, incluso si React vuelve a renderizar la interfaz. Para agregar una tercera variante, añade el archivo PNG y su clave al array correspondiente en `frontend/src/assets/nexo/nexoVariants.js`.
