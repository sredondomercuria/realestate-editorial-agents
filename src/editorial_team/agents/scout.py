"""Scout / Investigador de noticias.

Usa las herramientas web de Claude para encontrar noticias recientes de Real
Estate en la región objetivo y las estructura como lista de temas candidatos.
Skill asociada: `skills/news-research`.
"""

from __future__ import annotations

from ..config import get_settings
from ..llm import complete_json, research
from ..schemas import TOPICS_SCHEMA
from ..state import EditorialState

SYSTEM = """\
Sos un periodista de investigación senior especializado en el mercado inmobiliario
(Real Estate) de {region}. Tu trabajo es encontrar las noticias MÁS RELEVANTES y
RECIENTES (últimos 7 días) sobre: precios de propiedades, alquileres, créditos
hipotecarios, desarrollos, inversión inmobiliaria, regulación, blanqueo, dólar y su
impacto en ladrillos, y tendencias del sector.

Reglas:
- Priorizá fuentes primarias y medios reputados (diarios económicos, cámaras
  inmobiliarias, organismos oficiales, portales del sector).
- Para cada noticia anotá título, resumen, medio, URL y por qué importa.
- Descartá rumores sin fuente y contenido promocional/publicitario.
- No inventes datos ni URLs: todo debe venir de las búsquedas.
"""

STRUCTURE_SYSTEM = """\
Convertís hallazgos de investigación en datos estructurados. Extraé cada noticia
distinta como un item. `relevance` es un entero 0-100 según impacto y actualidad.
No inventes URLs: usá sólo las que aparecen en el texto.
"""


def scout(state: EditorialState) -> dict:
    s = get_settings()
    region = state.get("region", s.region_focus)
    run_date = state.get("run_date", "hoy")

    findings = research(
        system=SYSTEM.format(region=region),
        user=(
            f"Fecha de hoy: {run_date}. Buscá y listá entre 8 y 12 noticias de Real "
            f"Estate de {region} de los últimos 7 días. Para cada una incluí el medio "
            f"y la URL exacta. Terminá con un resumen de las más importantes."
        ),
        model=s.model_scout,
        max_uses=10,
    )

    data = complete_json(
        system=STRUCTURE_SYSTEM,
        user=f"Estructurá estos hallazgos en la lista de temas:\n\n{findings}",
        schema=TOPICS_SCHEMA,
        model=s.model_curator,
    )
    topics = data.get("topics", [])
    return {
        "topics": topics,
        "log": [f"scout: {len(topics)} noticias encontradas en '{region}'"],
    }
