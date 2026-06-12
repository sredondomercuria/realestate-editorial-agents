"""Adaptador de redes sociales / Community manager.

Genera una variante del editorial para cada red social configurada, respetando el
tono y los límites de cada plataforma. Skill asociada: `skills/social-publishing`.
"""

from __future__ import annotations

import json

from ..config import get_settings
from ..llm import complete_json
from ..schemas import SOCIAL_SCHEMA
from ..state import EditorialState

SYSTEM = """\
Sos community manager de un medio profesional de Real Estate. Creás una variante del
editorial para cada red indicada. Adaptá tono y longitud a cada plataforma:
- instagram: gancho visual + 3-5 hashtags, cálido y claro.
- linkedin: profesional, foco en el dato y la implicancia para inversores.
- facebook: informativo y cercano, llamada a leer la nota.
- x: <=270 caracteres, directo, 1-2 hashtags.
- threads: conversacional, una idea fuerte.
- tiktok: gancho hablado para un video corto.

Reglas: no exageres ni prometas rendimientos; mantené la precisión del dato; usá los
hashtags en `hashtags` (sin el texto). Escribí en español.
"""


def social_adapter(state: EditorialState) -> dict:
    s = get_settings()
    draft = state.get("draft", {})
    platforms = s.social_platform_list

    data = complete_json(
        system=SYSTEM,
        user=(
            f"Plataformas: {', '.join(platforms)}\n\n"
            "Editorial:\n"
            + json.dumps(
                {k: draft.get(k) for k in ("title", "dek", "seo_description", "tags")},
                ensure_ascii=False,
                indent=2,
            )
        ),
        schema=SOCIAL_SCHEMA,
        model=s.model_social,
    )
    variants = data.get("variants", [])
    return {"social": variants, "log": [f"social_adapter: {len(variants)} variantes"]}
