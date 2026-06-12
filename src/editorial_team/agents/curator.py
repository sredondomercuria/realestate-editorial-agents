"""Curador / Jefe de redacción.

Selecciona las mejores noticias del scout y define el ángulo editorial de cada una.
Skill asociada: `skills/news-research`.
"""

from __future__ import annotations

import json

from ..config import get_settings
from ..llm import complete_json
from ..schemas import CURATION_SCHEMA
from ..state import EditorialState

SYSTEM = """\
Sos el/la jefe de redacción de un blog profesional de Real Estate enfocado en {region}.
Recibís una lista de noticias candidatas y elegís las {n} mejores para el editorial de hoy.

Criterios de selección:
- Relevancia e impacto para inversores, compradores y profesionales del sector.
- Novedad y actualidad.
- Que haya datos verificables (cifras, fuentes, organismos).
- Diversidad temática: evitá repetir el mismo subtema.

Para cada noticia elegida definí: el ángulo editorial, por qué importa, 3-5 puntos
clave (datos concretos a verificar y desarrollar) y la fuente principal.
"""


def curator(state: EditorialState) -> dict:
    s = get_settings()
    region = state.get("region", s.region_focus)
    topics = state.get("topics", [])

    data = complete_json(
        system=SYSTEM.format(region=region, n=s.num_topics),
        user="Noticias candidatas:\n\n" + json.dumps(topics, ensure_ascii=False, indent=2),
        schema=CURATION_SCHEMA,
        model=s.model_curator,
    )
    selected = data.get("selected", [])[: s.num_topics]
    return {
        "selected": selected,
        "log": [f"curator: {len(selected)} temas seleccionados"],
    }
