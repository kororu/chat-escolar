# Plan del instalador Windows 1.0

Este instalador **todavía no existe**. Es planificación para la fase final 1.0; el archivo esperado es `ChatEscolar_Setup.exe`.

## Objetivo

Instalar y abrir Chat Escolar para una persona no técnica, ocultando la preparación de Python, frontend, backend y arranque local. Inno Setup es la herramienta sugerida para empaquetar y crear accesos directos.

## Opciones previstas

1. **Básica**: Chat Escolar sin Ollama; usa modo básico.
2. **Recomendada**: Ollama y un modelo liviano, si el equipo e internet lo permiten.
3. **Avanzada**: Ollama, modelo liviano y modelo superior.

El instalador debería incluir recursos, scripts internos, acceso directo, verificación de puertos y arranque coordinado. Debe conservar modo básico como fallback y no exigir descarga de modelos para terminar la instalación.

## Riesgos y pruebas

Riesgos: tamaño del paquete, licencias de Ollama/modelos, descargas e internet, rendimiento, antivirus y puertos ocupados. Probar en PC Windows limpio: instalación básica, inicio/cierre, perfiles, chat sin Ollama, instalación opcional de modelos, recuperación ante puerto ocupado y desinstalación.
