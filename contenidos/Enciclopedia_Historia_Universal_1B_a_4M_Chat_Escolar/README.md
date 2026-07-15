# Enciclopedia de Historia Universal — 1° básico a 4° medio

Base enciclopédica original, modular e inclusiva para **Chat Escolar**. Está diseñada para complementar las enciclopedias por curso y la colección especializada de Historia de Chile.

## Estado

- Versión: 1.0
- Verificación curricular: 2026-07-14
- Alcance: 1° básico a 4° medio
- Capítulos curriculares y de profundización: 279
- Uso: apoyo educativo local con FastAPI, Ollama y recuperación RAG

## Principio curricular

Historia Universal no tiene la misma presencia en todos los niveles. En primer ciclo se trabaja mediante tiempo, diversidad y comparación; en 3° y 4° básico existe cobertura directa de Grecia, Roma y civilizaciones americanas; en 7° y 8° básico se organizan procesos de Antigüedad, Edad Media y Modernidad; en 1° y 2° medio se profundiza en los siglos XIX y XX. En 3° y 4° medio se separa la Formación General de Educación Ciudadana del electivo Comprensión Histórica del Presente.

## Capítulos por curso

- **1° básico:** 8 capítulos.
- **2° básico:** 10 capítulos.
- **3° básico:** 23 capítulos.
- **4° básico:** 24 capítulos.
- **5° básico:** 14 capítulos.
- **6° básico:** 14 capítulos.
- **7° básico:** 30 capítulos.
- **8° básico:** 30 capítulos.
- **1° medio:** 31 capítulos.
- **2° medio:** 41 capítulos.
- **3° medio:** 16 capítulos.
- **4° medio:** 18 capítulos.

## Instalación

Renombre esta carpeta como `historia_universal` y ubíquela en:

```text
chat-escolar/contenidos/historia_universal/
```

## Indexación

Indexe los capítulos por curso y los temáticos transversales. Excluya `17_compendios` para evitar duplicados.

Consulte [el índice maestro](00_documentacion/00_indice_maestro.md) y [la guía de integración RAG](00_documentacion/05_integracion_ollama_rag.md).
