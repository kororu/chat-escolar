# Chat Escolar - Distribucion Local Gratuita

## 1. Decision oficial

Chat Escolar tendra una **Version Local 2** pensada para funcionar gratis en otro PC, por ejemplo en el computador de un familiar, profesora o adulto que quiera probar la aplicacion.

Esta version no sera todavia un instalador completo ni un `.exe` final, pero si tendra scripts que faciliten la configuracion y ejecucion.

## 2. Objetivo

Permitir que otra persona pueda usar Chat Escolar localmente con la menor cantidad de pasos posible.

La idea es que el usuario descargue o copie la carpeta del proyecto y use archivos `.bat` para:

- Verificar requisitos.
- Instalar dependencias.
- Iniciar backend.
- Iniciar frontend.
- Abrir la aplicacion en el navegador.

## 3. Que sera gratis

La version local sera gratuita mientras use:

- Frontend React/Vite local.
- Backend FastAPI local.
- SQLite local.
- Historial local.
- Videos curados como enlaces.
- Contenidos educativos preparados.
- Respuestas simuladas o respuestas predefinidas.

## 4. Que podria tener costo

Podria tener costo si se activa:

- OpenAI API.
- Busqueda automatica con YouTube Data API si se superan limites gratuitos.
- Hosting online.
- Base de datos online fuera de plan gratis.

Por eso la Version Local 2 debe funcionar sin depender de OpenAI API.

## 5. Modos de funcionamiento

### 5.1 Modo Demo Gratuito

Funcionara sin API key.

Debe incluir:

- Respuestas preparadas.
- Contenidos iniciales.
- Preguntas frecuentes.
- Videos curados.
- Historial local.
- Modo Escolar.
- Modo Explorador.

Este modo sirve para que una profesora, familiar o adulto pruebe el concepto sin costo.

### 5.2 Modo IA Opcional

Funcionara solo si el usuario configura:

```env
OPENAI_API_KEY=...
```

Reglas:

- Debe ser opcional.
- La app no debe romperse si no existe API key.
- Si no hay API key, usar Modo Demo Gratuito.
- Informar claramente que la IA real puede tener costo por uso.

## 6. Estructura esperada de distribucion

```text
chat-escolar/
├── iniciar_chat_escolar.bat
├── instalar_dependencias.bat
├── verificar_requisitos.bat
├── README_LOCAL.md
├── frontend/
├── backend/
├── docs/
├── prompts/
├── contenidos/
└── pruebas/
```

## 7. Script verificar_requisitos.bat

Objetivo:

Revisar si el PC tiene lo necesario.

Debe verificar:

- Git opcional.
- Node.js.
- npm.
- Python.
- pip.

Si falta algo, debe mostrar instrucciones simples.

Ejemplo esperado:

```text
Verificando requisitos de Chat Escolar...

Node.js: OK
npm: OK
Python: OK
pip: OK

El PC esta listo para instalar dependencias.
```

Si falta Node:

```text
Node.js no esta instalado.
Descargalo desde:
https://nodejs.org/
```

## 8. Script instalar_dependencias.bat

Objetivo:

Preparar frontend y backend.

Debe hacer:

1. Entrar a `frontend`.
2. Ejecutar `npm install`.
3. Volver a raiz.
4. Entrar a `backend`.
5. Crear entorno virtual si no existe.
6. Activar entorno virtual.
7. Ejecutar `pip install -r requirements.txt`.
8. Volver a raiz.

No debe borrar archivos del usuario.

## 9. Script iniciar_chat_escolar.bat

Objetivo:

Iniciar la app localmente.

Debe:

1. Abrir backend en una ventana de terminal.
2. Abrir frontend en otra ventana de terminal.
3. Esperar unos segundos.
4. Abrir navegador en:

```text
http://localhost:5173/
```

Debe mostrar mensaje:

```text
Chat Escolar se esta iniciando...
Backend: http://127.0.0.1:8000
Frontend: http://localhost:5173
```

## 10. README_LOCAL.md

Debe explicar a un usuario no tecnico:

1. Instalar Node.js.
2. Instalar Python.
3. Descargar o copiar carpeta de Chat Escolar.
4. Ejecutar `verificar_requisitos.bat`.
5. Ejecutar `instalar_dependencias.bat`.
6. Ejecutar `iniciar_chat_escolar.bat`.
7. Abrir navegador.

Tambien debe incluir solucion a errores comunes:

- npm bloqueado por PowerShell.
- Python no reconocido.
- Puerto 5173 ocupado.
- Puerto 8000 ocupado.
- Backend no conectado.

## 11. Reglas tecnicas

- No depender de servicios pagados para el modo demo.
- No exigir API key para abrir la app.
- No guardar datos sensibles.
- No subir `.env` a GitHub.
- Mantener SQLite local.
- Mantener videos como lista curada al inicio.
- Mantener respuestas demo en archivos locales o backend.

## 12. Cambios futuros necesarios

Para cumplir esta version se deben implementar:

1. Endpoint backend para respuesta simulada del tutor.
2. Historial local en SQLite o memoria inicial.
3. Lista de videos curados local.
4. Frontend conectado al backend.
5. Deteccion de backend conectado.
6. Scripts `.bat`.
7. README local para usuarios no tecnicos.

## 13. Orden recomendado de desarrollo

1. Conectar frontend con backend usando `/health`.
2. Crear endpoint `/chat/demo`.
3. Hacer que el chat use respuestas simuladas.
4. Crear historial local.
5. Crear videos curados locales.
6. Crear scripts `.bat`.
7. Probar en el PC actual.
8. Probar en otro PC.
9. Ajustar instrucciones.
10. Recién despues evaluar IA real con OpenAI API.

## 14. Criterio de exito

La Version Local 2 sera exitosa si otra persona puede:

- Copiar o descargar el proyecto.
- Ejecutar una guia simple.
- Instalar dependencias.
- Abrir Chat Escolar localmente.
- Usar el modo demo sin pagar.
- Revisar historial.
- Ver videos curados.
- Probar preguntas educativas sin configurar OpenAI API.

## 15. Prompt para Codex

Cuando se quiera implementar los scripts, usar:

```text
Lee docs/Distribucion_Local_Gratuita_Chat_Escolar.md.

Implementa la Version Local 2 de Chat Escolar.

Crea en la raiz:
- verificar_requisitos.bat
- instalar_dependencias.bat
- iniciar_chat_escolar.bat
- README_LOCAL.md

Los scripts deben funcionar en Windows con PowerShell/CMD, no deben borrar archivos y deben mostrar mensajes claros.

La app debe poder funcionar en modo demo sin OpenAI API.

No conectes todavia OpenAI API.
Primero deja funcionando frontend, backend, respuesta demo, historial local basico y videos curados.
```

