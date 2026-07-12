# Arquitectura de contenidos

```text
Enciclopedia_6_Basico_Chat_Escolar/
├── 00_documentacion/
├── lenguaje/
├── matematica/
├── ciencias_naturales/
├── historia_geografia/
├── evaluaciones/
├── bancos/
├── apoyo_inclusivo/
└── compendios/
```

Los capítulos modulares son la fuente primaria para RAG. Los compendios son para lectura humana y deben excluirse del índice vectorial. Evaluaciones y bancos pueden integrarse en un índice separado para evitar que una respuesta de práctica aparezca cuando se solicita una explicación.
