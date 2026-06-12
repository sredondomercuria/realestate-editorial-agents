# 08 · Mejores prácticas

Las decisiones de diseño de este proyecto, para que las apliques en tus propios
sistemas multiagente.

## Diseño de agentes
- **Una responsabilidad por agente.** Cada nodo hace una cosa y la hace bien. Es
  más fácil de testear, depurar y reemplazar.
- **El modelo correcto para cada tarea.** Opus para razonamiento/investigación;
  Sonnet para tareas acotadas (curaduría, formato, social). Configurable por `.env`.
- **Empezá simple.** Un solo nodo o una cadena lineal antes de meter bucles y
  ramas. La complejidad se agrega cuando se justifica.

## Calidad y veracidad (lo más importante en contenido)
- **Separá investigar de redactar.** El que escribe sólo usa datos ya verificados.
- **Verificación con fuentes independientes** (mínimo configurable por dato).
- **Revalidación crítica adversarial** antes de publicar, con bucle de corrección
  acotado (`MAX_REVISIONS`) para no caer en loops infinitos.
- **Atribuí cada cifra.** Si no se puede verificar, no se publica.
- **Estados explícitos** (`verified/uncertain/refuted`) en vez de "parece bien".

## Uso de la API de Claude
- **Structured outputs** (`output_config.format`) para datos confiables y
  parseables, en vez de pedir "devolvé JSON" y rezar.
- **Herramientas server-side** (`web_search`/`web_fetch`) para datos actuales con
  citas; manejá `stop_reason == "pause_turn"`.
- **No combines** structured outputs con citas (web): investigá y luego estructurá.
- **Razonamiento adaptativo** (`thinking: {type: "adaptive"}`) + `effort` en los
  pasos que lo ameritan (redacción, crítica).
- En **Opus 4.8/Sonnet 4.6** no envíes `temperature`/`top_p` ni `budget_tokens`.
- **Prompt caching** si reusás prefijos grandes (system prompts estables).

## Seguridad y secretos
- **Secretos sólo en `.env` / secrets de CI.** Nunca en el código ni en el repo.
  Acá el repo es público: sólo `.env.example` con placeholders, y `.gitignore`
  estricto.
- **Application Passwords** para WordPress (no la contraseña real).
- **No loguees credenciales.**
- **`DRY_RUN=true` por defecto**: nada se publica sin intención explícita.
- **Estado `draft`** en el blog para revisión humana antes de salir en vivo.
- **Manejo de errores por canal**: si una red falla, las demás siguen.

## Operación
- **Determinismo donde importa.** El flujo (orden, bucles, ramas) vive en código
  (LangGraph), no en la improvisación del modelo.
- **Artefactos persistidos** por corrida (`output/<fecha>/`) para auditar.
- **Límites explícitos**: `recursion_limit`, `MAX_REVISIONS`, `max_uses` de
  herramientas; nada de bucles sin tope.
- **Observabilidad**: el `log` del estado registra cada paso; revisalo.

## Costos
- Modelos más chicos para estructuración/format.
- `effort` y `max_tokens` ajustados a cada tarea.
- `NUM_TOPICS` y `max_uses` controlan cuánto investiga (y cuánto gasta).

## Checklist antes de publicar en vivo
- [ ] Corriste varios días en `DRY_RUN=true` y revisaste los `output/`.
- [ ] `WORDPRESS_STATUS=draft` y revisaste un par de posts a mano.
- [ ] Las credenciales están en secrets (no en el repo).
- [ ] Verificaste los campos de la API de upload-post.
- [ ] Definiste la hora y zona horaria del scheduler.

## Fin del tutorial
Volvé al [README](../README.md) o revisá el [índice de docs](01-arquitectura.md).
