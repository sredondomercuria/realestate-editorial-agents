# 03 · Skills: una capacidad por funcionalidad

Una **skill** es una capacidad reutilizable empaquetada como carpeta con un
`SKILL.md`. El `SKILL.md` describe *cuándo* usar la skill (en su `description`) y
*cómo* ejecutarla (en el cuerpo). Es el patrón de **Claude Agent Skills**.

## Por qué skills (y no sólo prompts)

- **Reutilización**: la misma especificación sirve para el workflow programático
  (LangGraph) y para un agente autónomo (Cowork).
- **Divulgación progresiva**: el agente sólo lee el `SKILL.md` completo cuando la
  tarea lo amerita; el resto del tiempo ocupa contexto sólo la `description`.
- **Mantenibilidad**: el "cómo" vive en un lugar; cambiás la skill y cambia el
  comportamiento en todos lados.

## Anatomía de un SKILL.md

```markdown
---
name: fact-check
description: Verificar datos... (una línea: es lo que el modelo lee para decidir).
---

# Verificación de datos
## Objetivo / Cuándo usar / Entradas / Procedimiento / Salida / Criterios de calidad
```

La `description` es lo más importante para el *triggering*: debe decir **cuándo**
se usa, no sólo qué hace.

## Las 7 skills del equipo

| Skill | Hace | Implementada por |
|-------|------|------------------|
| `news-research` | Busca y cura noticias | `agents/scout.py` + `agents/curator.py` |
| `fact-check` | Valida datos con fuentes | `agents/fact_checker.py` |
| `editorial-writing` | Redacta el editorial | `agents/writer.py` |
| `critical-review` | Revalida y controla calidad | `agents/critic.py` |
| `image-generation` | Prompt visual + imagen | `agents/illustrator.py` |
| `blog-publishing` | Publica en WordPress | `agents/publisher.py` |
| `social-publishing` | Adapta y publica en redes | `agents/social_adapter.py` + `agents/publisher.py` |

Cada una está en `skills/<nombre>/SKILL.md`.

## La relación skill ⇄ agente

En este proyecto la skill es la **especificación** y el nodo del grafo es la
**implementación determinística**. Por ejemplo, `skills/fact-check/SKILL.md` define
los estados `verified/uncertain/refuted` y la `recommendation`, y
`agents/fact_checker.py` los implementa con `web_search` + structured outputs.

En Cowork, en cambio, **no hay código**: el agente Claude lee la skill y la ejecuta
con sus herramientas. Mismo "qué", distinto "quién".

## Crear o modificar una skill

1. Editá el `SKILL.md` (procedimiento y criterios).
2. Si cambia el contrato de datos, actualizá el JSON Schema en `schemas.py`.
3. Ajustá el nodo en `agents/` si hace falta.

> 💡 Para crear/optimizar skills con asistencia, en Claude Code existe la skill
> `skill-creator` (medición de *triggering*, evals, etc.).

## Siguiente
→ [04-agentes-langgraph.md](04-agentes-langgraph.md)
