"""Fact-checker / Verificador de datos.

Toma los puntos clave de los temas seleccionados y los verifica con búsquedas web
independientes, emitiendo un veredicto por afirmación y una recomendación global.
Skill asociada: `skills/fact-check`.
"""

from __future__ import annotations

import json

from ..config import get_settings
from ..llm import complete_json, research
from ..schemas import FACTCHECK_SCHEMA
from ..state import EditorialState

SYSTEM = """\
Sos verificador/a de datos (fact-checker) de un medio profesional. Recibís
afirmaciones y datos sobre Real Estate de {region} y debés CONFIRMARLOS con fuentes
INDEPENDIENTES (al menos {min_sources} por dato clave).

Para cada afirmación buscá en la web evidencia que la respalde o refute:
- `verified`: confirmada por fuentes independientes confiables.
- `uncertain`: no encontrás suficiente respaldo o las fuentes discrepan.
- `refuted`: la evidencia la contradice.

Sé escéptico/a: las cifras inventadas o exageradas son el principal riesgo.
Citá las URLs de las fuentes que usás.
"""

STRUCTURE_SYSTEM = """\
Convertís el análisis de verificación en datos estructurados. `recommendation`:
- `proceed` si la mayoría está verificada y no hay nada refutado importante,
- `revise` si hay datos `uncertain` que requieren matizar,
- `drop` si hay afirmaciones centrales `refuted`.
Incluí las URLs reales de las fuentes en cada veredicto.
"""


def fact_checker(state: EditorialState) -> dict:
    s = get_settings()
    region = state.get("region", s.region_focus)
    selected = state.get("selected", [])

    claims = []
    for item in selected:
        claims.append({"tema": item.get("title"), "puntos_clave": item.get("key_points", [])})

    analysis = research(
        system=SYSTEM.format(region=region, min_sources=s.min_sources_per_claim),
        user=(
            "Verificá los siguientes puntos clave con fuentes independientes y "
            "citá las URLs:\n\n" + json.dumps(claims, ensure_ascii=False, indent=2)
        ),
        model=s.model_fact_checker,
        max_uses=12,
    )

    result = complete_json(
        system=STRUCTURE_SYSTEM,
        user=f"Estructurá esta verificación:\n\n{analysis}",
        schema=FACTCHECK_SCHEMA,
        model=s.model_curator,
    )
    n_ver = sum(1 for v in result.get("verdicts", []) if v.get("status") == "verified")
    return {
        "factcheck": result,
        "log": [
            f"fact_checker: {n_ver}/{len(result.get('verdicts', []))} verificados, "
            f"recomendación={result.get('recommendation')}"
        ],
    }
