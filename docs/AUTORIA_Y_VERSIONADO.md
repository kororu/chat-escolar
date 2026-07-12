# Autoría y versionado de Chat Escolar

## Información oficial

- Proyecto: Chat Escolar.
- Autor: Ariel Ponce.
- Año de inicio: 2026.
- Versión actual: `0.1.0`.

Este documento no incluye correo, dirección, teléfono ni otros datos personales sensibles.

## Configuración central del frontend

La información de autoría y versión usada por la interfaz se encuentra en:

```text
frontend/src/config/appInfo.js
```

Para cambiar la versión visible en el frontend, actualiza la propiedad `version` de `APP_INFO`. El mismo archivo centraliza nombre del proyecto, autor, año y descripción.

El backend mantiene su versión en la configuración de `FastAPI` y en el endpoint raíz de `backend/main.py`. Cuando cambie una versión pública, actualiza ambos lugares para conservar la coherencia entre frontend, API y documentación.

## Lugares donde aparece la autoría

- Footer de la pantalla principal.
- Panel “Acerca de”.
- README principal.
- Endpoint raíz `GET /` del backend.

## Convención sugerida de versiones

- `0.1.0`: desarrollo inicial.
- `0.2.0`: incorporación de nuevas funciones relevantes.
- `1.0.0`: primera versión estable.

Se recomienda registrar cada cambio de versión en la documentación de continuidad o en un historial de cambios.

## Alcance

Agregar una marca de autoría al software no reemplaza una licencia formal, un registro legal de propiedad intelectual ni otros mecanismos jurídicos. Si el proyecto se distribuye públicamente, conviene definir además una licencia adecuada.

