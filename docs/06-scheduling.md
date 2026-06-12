# 06 · Ejecución diaria (scheduling)

El workflow está pensado para correr **todos los días a una hora fija**. Tenés tres
opciones según dónde quieras que viva.

## Opción A — GitHub Actions (recomendada para "se ejecuta solo en la nube")

Ya está en `.github/workflows/daily-editorial.yml`. Corre a las **11:00 UTC =
08:00 Argentina** y también se puede disparar a mano.

1. Subí el repo a GitHub.
2. En **Settings → Secrets and variables → Actions** cargá los *secrets*:
   `ANTHROPIC_API_KEY`, `WORDPRESS_URL`, `WORDPRESS_USER`,
   `WORDPRESS_APP_PASSWORD`, `UPLOADPOST_API_KEY`, `UPLOADPOST_USER`,
   y opcionalmente `OPENAI_API_KEY`.
3. (Opcional) en *Variables* definí `DRY_RUN`, `IMAGE_PROVIDER`, `SOCIAL_PLATFORMS`,
   `REGION_FOCUS`.
4. Probá con **Run workflow** (deja `dry_run` en `true` la primera vez).

> El cron de GitHub Actions usa **UTC**. Para otra hora local, convertí a UTC y
> editá la línea `cron`.

## Opción B — cron (Linux/servidor propio)

```bash
# Editá las rutas en scheduling/crontab.example y luego:
crontab scheduling/crontab.example
```

La línea ya carga tu `.env` antes de ejecutar (cron no lo hace solo):

```cron
0 8 * * *  cd /ruta/proyecto && set -a && . ./.env && set +a && /ruta/venv/bin/python -m editorial_team.run_daily >> output/cron.log 2>&1
```

## Opción C — launchd (macOS)

```bash
cp scheduling/launchd.plist.example ~/Library/LaunchAgents/com.realestate.editorial.plist
# editá las rutas dentro del plist, luego:
launchctl load ~/Library/LaunchAgents/com.realestate.editorial.plist
```

## Opción D — Claude Cowork / agente programado

Si corrés el equipo como agente autónomo (ver [07-cowork.md](07-cowork.md)),
programá el prompt de `cowork/PROMPT.md` con la **herramienta de tareas
programadas** de Cowork para que se ejecute diariamente. En Claude Code, la skill
`schedule` crea rutinas (cron) para agentes en la nube.

## Consejos de operación

- **Empezá en `DRY_RUN=true`** unos días; revisá los `output/<fecha>/` antes de
  publicar en vivo.
- **`WORDPRESS_STATUS=draft`** al principio: el post queda para aprobación humana.
- **Logs**: revisá `output/cron.log` (cron) o los artefactos del run (Actions).
- **Idempotencia/zona horaria**: el run usa la fecha del sistema; fijá el TZ del
  entorno si publicás cerca de medianoche.

## Siguiente
→ [07-cowork.md](07-cowork.md)
