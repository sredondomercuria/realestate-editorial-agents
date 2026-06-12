# 07 · Correr el equipo en Claude Cowork

Hasta acá ejecutamos el equipo de forma **programática** (LangGraph en `src/`).
La misma idea se puede expresar como un **agente autónomo** en Claude Cowork: un
agente Claude que carga las **skills** y ejecuta el workflow descripto en un prompt.

## ¿Cuándo usar cada modo?

| | LangGraph (programático) | Cowork (agente autónomo) |
|---|---|---|
| Control del flujo | Determinístico (código) | Dirigido por el modelo |
| Ideal para | Producción, cron/CI, costos predecibles | Iteración rápida, ajustes en lenguaje natural |
| Dónde corre | Tu servidor / Actions | Cowork |
| Define el "cómo" | `agents/` + `skills/` | `skills/` + `cowork/PROMPT.md` |

Lo bueno: **comparten las skills**. La especificación del "cómo" es la misma.

## Pasos

1. **Instalá las skills** en tu agente de Cowork (copiá las carpetas de `skills/`
   a la ubicación de skills del agente).
2. **Cargá el prompt** de [`cowork/PROMPT.md`](../cowork/PROMPT.md) como
   instrucción del agente. Define el rol (editor jefe), el objetivo y el workflow
   de 8 pasos que usa las skills.
3. **Configurá las credenciales** como variables de entorno / secretos del agente
   (blog y upload-post). **No** las pegues en el chat.
4. **Programá** el prompt para que corra todos los días a la hora elegida (tarea
   programada de Cowork).

## Qué hace el agente

Sigue el workflow de `cowork/PROMPT.md`:

```
news-research → fact-check → editorial-writing ⇄ critical-review
   → image-generation → social-publishing (variantes) → blog-publishing + social-publishing (publicar)
```

Con las mismas reglas no negociables: cero datos inventados, atribución de cada
cifra, sin clickbait, y modo seguro `DRY_RUN` para aprobación humana.

## Managed Agents (ya implementado: runtime híbrido)

Cowork es un producto interactivo. Si querés que **Anthropic** corra el bucle del
agente de forma programática (desde tu backend), eso es **Managed Agents**, y en
este proyecto **ya está implementado** como el runtime `hybrid`: el nodo `producer`
crea un *agent* (modelo + system prompt + skills) y abre una *session* por corrida.
Es la diferencia entre Cowork (lo manejás vos en la UI de Claude) y Managed Agents
(lo maneja tu código). Ver [11-managed-agents.md](11-managed-agents.md).

## Siguiente
→ [08-mejores-practicas.md](08-mejores-practicas.md)
