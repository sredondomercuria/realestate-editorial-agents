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

## Managed Agents (alternativa avanzada)

Si querés que **Anthropic** corra el bucle del agente y aloje el sandbox de
herramientas (en vez de tu servidor), mirá **Managed Agents** de la plataforma
Claude: creás un *agent* (modelo + system prompt + tools + skills) una vez y abrís
*sessions* por corrida; podés adjuntar las skills y programar la ejecución vía
webhooks/cron. Es el camino "todo gestionado". Ver la documentación de la
plataforma Claude → Managed Agents.

## Siguiente
→ [08-mejores-practicas.md](08-mejores-practicas.md)
