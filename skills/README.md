# Skills del equipo editorial

Cada carpeta es una **Claude Agent Skill**: una capacidad reutilizable con su
`SKILL.md` (instrucciones + criterios de calidad). Las skills encapsulan el
"cómo" de cada función; el workflow de agentes (en `src/` con LangGraph, o en
Claude Cowork con el prompt de `cowork/PROMPT.md`) las invoca para cumplir su
cometido.

| Skill | Rol | Nodo LangGraph equivalente |
|-------|-----|----------------------------|
| [`news-research`](news-research/SKILL.md) | Buscar y curar noticias de Real Estate | `scout` + `curator` |
| [`fact-check`](fact-check/SKILL.md) | Validar datos con fuentes independientes | `fact_checker` |
| [`editorial-writing`](editorial-writing/SKILL.md) | Redactar el editorial profesional | `writer` |
| [`critical-review`](critical-review/SKILL.md) | Revalidación crítica y control de calidad | `critic` |
| [`image-generation`](image-generation/SKILL.md) | Prompt visual + imagen que acompaña cada post | `illustrator` |
| [`blog-publishing`](blog-publishing/SKILL.md) | Publicar en el blog (WordPress) | `publisher` |
| [`social-publishing`](social-publishing/SKILL.md) | Adaptar y publicar en redes (upload-post) | `social_adapter` + `publisher` |

## Dos formas de usarlas

1. **Como conocimiento del workflow programático (LangGraph).** Cada nodo en
   `src/editorial_team/agents/` implementa la skill homónima. El `SKILL.md` es la
   especificación; el código es la implementación determinística.

2. **Como Agent Skills en Claude Cowork / Agent SDK.** Copiá estas carpetas a la
   ubicación de skills de tu agente y un agente Claude las cargará y ejecutará de
   forma autónoma siguiendo el prompt de `cowork/PROMPT.md`.

## Formato de un SKILL.md

```markdown
---
name: nombre-en-kebab-case
description: Cuándo usar la skill (una línea; es lo que el modelo lee para decidir).
---

# Instrucciones
...pasos, entradas, salidas y criterios de calidad...
```
