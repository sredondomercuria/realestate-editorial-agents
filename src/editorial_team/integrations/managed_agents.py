"""Managed Agents — los agentes "deployados en la plataforma de Claude".

En el runtime **híbrido**, la producción editorial autónoma (investigar → validar →
redactar → revalidar) NO corre como nodos LangGraph en este backend, sino como un
**Managed Agent** en la infraestructura de Anthropic: nosotros creamos un *agent*
(una vez), abrimos una *session* por corrida, le damos el objetivo y leemos el
resultado del stream de eventos. Anthropic corre el loop y aloja el sandbox de
herramientas.

Las **skills** (`skills/*/SKILL.md`) se cargan como manual operativo del agente
(system prompt). Si tenés las skills subidas vía Skills API, podés además
adjuntarlas por ID (ver `docs/11-managed-agents.md`).

Diseño defensivo: si Managed Agents no está disponible/configurado, `run_editorial_team`
devuelve `None` y el grafo cae al pipeline **local**. Así el tutorial corre siempre.

Uso (crear/inspeccionar el agente una vez):
    python -m editorial_team.integrations.managed_agents setup
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from ..config import get_settings
from ..llm import get_client

AGENT_NAME = "equipo-editorial-realestate"
ENV_NAME = "editorial-realestate-env"
SKILL_FILES = ["news-research", "fact-check", "editorial-writing", "critical-review"]

OUTPUT_CONTRACT = """\
Al terminar, devolvé EXCLUSIVAMENTE un bloque ```json con este shape (sin texto extra):
{
  "selected":  [ {"title","angle","why_it_matters","key_points":[...],"primary_source"} ],
  "factcheck": {"verdicts":[{"claim","status","sources":[...],"note"}],"recommendation","summary"},
  "draft":     {"title","slug","dek","body_markdown","tags":[...],"seo_description","sources":[...],"image_brief"},
  "review":    {"verdict","score","issues":[{"severity","type","detail","fix"}],"notes"}
}
status ∈ verified|uncertain|refuted · recommendation ∈ proceed|revise|drop ·
verdict ∈ approved|needs_revision
"""


def _skills_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "skills"


def _load_skill(name: str) -> str:
    f = _skills_dir() / name / "SKILL.md"
    try:
        return f.read_text(encoding="utf-8")
    except OSError:
        return ""


def _system_prompt() -> str:
    settings = get_settings()
    manual = "\n\n---\n\n".join(_load_skill(n) for n in SKILL_FILES if _load_skill(n))
    return (
        f"Sos el editor jefe de un equipo editorial autónomo de Real Estate enfocado en "
        f"{settings.region_focus}. Trabajás siguiendo estas SKILLS (tu manual operativo); "
        f"respetá su procedimiento y criterios de calidad al pie de la letra.\n\n"
        f"REGLAS NO NEGOCIABLES: cero datos inventados; verificá cada cifra con al menos "
        f"{settings.min_sources_per_claim} fuentes independientes; atribuí cada dato; sin "
        f"clickbait ni consejo financiero. Si la crítica pide cambios, reescribí (máx "
        f"{settings.max_revisions} reescrituras).\n\n"
        f"===== SKILLS =====\n{manual}\n"
    )


def ensure_environment(client) -> str:
    settings = get_settings()
    if settings.managed_env_id:
        return settings.managed_env_id
    for env in client.beta.environments.list():
        if getattr(env, "name", None) == ENV_NAME:
            return env.id
    env = client.beta.environments.create(
        name=ENV_NAME,
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )
    return env.id


def ensure_agent(client) -> str:
    settings = get_settings()
    if settings.managed_agent_id:
        return settings.managed_agent_id
    for agent in client.beta.agents.list():
        if getattr(agent, "name", None) == AGENT_NAME:
            return agent.id
    agent = client.beta.agents.create(
        name=AGENT_NAME,
        model=settings.model_writer,
        system=_system_prompt(),
        tools=[{"type": "agent_toolset_20260401"}],  # incluye web_search/web_fetch/read/write
    )
    return agent.id


def _extract_json(text: str) -> dict | None:
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    blob = m.group(1) if m else None
    if blob is None:
        start, end = text.find("{"), text.rfind("}")
        blob = text[start : end + 1] if start != -1 and end != -1 else None
    if not blob:
        return None
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return None


def run_editorial_team(*, region: str, run_date: str) -> dict | None:
    """Corre la producción editorial como Managed Agent. Devuelve dict o None (fallback)."""
    settings = get_settings()
    try:
        client = get_client()
        env_id = ensure_environment(client)
        agent_id = ensure_agent(client)

        session = client.beta.sessions.create(
            agent=agent_id,
            environment_id=env_id,
            title=f"Editorial {run_date}",
        )

        task = (
            f"Fecha: {run_date}. Producí el editorial de hoy para {region} siguiendo tus "
            f"skills: investigá y curá {settings.num_topics} noticias recientes, verificá los "
            f"datos, redactá el editorial y hacé la revalidación crítica.\n\n{OUTPUT_CONTRACT}"
        )

        final_text = ""
        # Stream-first: abrir el stream y luego enviar el mensaje.
        with client.beta.sessions.events.stream(session_id=session.id) as stream:
            client.beta.sessions.events.send(
                session_id=session.id,
                events=[{"type": "user.message", "content": [{"type": "text", "text": task}]}],
            )
            for event in stream:
                etype = getattr(event, "type", "")
                if etype == "agent.message":
                    for block in event.content:
                        if getattr(block, "type", None) == "text":
                            final_text += block.text
                elif etype == "session.status_idle":
                    stop = getattr(event, "stop_reason", None)
                    if getattr(stop, "type", None) == "requires_action":
                        continue
                    break
                elif etype == "session.status_terminated":
                    break

        data = _extract_json(final_text)
        if not data or "draft" not in data:
            print("[managed_agents] no se pudo parsear la salida; fallback a local.")
            return None
        return data
    except Exception as exc:  # noqa: BLE001 — si algo falla, el grafo usa el pipeline local
        print(f"[managed_agents] no disponible ({exc}); fallback a local.")
        return None


def setup() -> int:
    """Crea (o encuentra) el environment y el agent, e imprime los IDs para el .env."""
    client = get_client()
    print("Creando/obteniendo environment y agent en la plataforma de Claude...")
    env_id = ensure_environment(client)
    agent_id = ensure_agent(client)
    print("\n✅ Listo. Agregá esto a tu .env para cachearlos:\n")
    print(f"MANAGED_ENV_ID={env_id}")
    print(f"MANAGED_AGENT_ID={agent_id}")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        return setup()
    # Sin args: corre una producción de prueba y muestra el resultado.
    settings = get_settings()
    result = run_editorial_team(region=settings.region_focus, run_date=date.today().isoformat())
    print(json.dumps(result, ensure_ascii=False, indent=2) if result else "Sin resultado (fallback).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
