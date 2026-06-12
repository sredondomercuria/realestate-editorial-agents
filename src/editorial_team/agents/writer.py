"""Redactor / Editor.

Escribe el editorial profesional combinando los temas seleccionados con los
veredictos del fact-checker. Si el crítico pidió cambios, reescribe atendiendo
sus notas. Skill asociada: `skills/editorial-writing`.
"""

from __future__ import annotations

import json

from ..config import get_settings
from ..llm import complete_json
from ..schemas import EDITORIAL_SCHEMA
from ..state import EditorialState

SYSTEM = """\
Sos redactor/a editorial senior de un blog profesional de Real Estate enfocado en
{region}. Escribís en español rioplatense neutro, claro y con autoridad.

Escribí UN editorial cohesivo (no una lista de noticias sueltas) que hile los temas
seleccionados con una tesis clara. Requisitos:
- Sólo usá datos con estado `verified`. Los `uncertain` se mencionan con cautela
  ("según...", "estimaciones preliminares") o se omiten. NUNCA uses datos `refuted`.
- Cada cifra relevante debe atribuirse a su fuente.
- Estructura en Markdown: titular potente, bajada (dek), subtítulos `##`, párrafos
  legibles, y una sección final "Fuentes" con las URLs.
- Tono profesional, sin clickbait ni promesas de inversión. Cumplí estándares
  periodísticos: equilibrio, contexto y precisión.
- Longitud: 700-1100 palabras.
- `image_brief`: describí en 1-2 frases la imagen editorial que debería acompañar
  la nota (concepto visual, no texto).

Si recibís NOTAS DE REVISIÓN del editor crítico, corregí TODOS los puntos señalados.
"""


def writer(state: EditorialState) -> dict:
    s = get_settings()
    region = state.get("region", s.region_focus)
    selected = state.get("selected", [])
    factcheck = state.get("factcheck", {})
    review = state.get("review")
    revision_count = state.get("revision_count", 0)

    context = {
        "temas_seleccionados": selected,
        "verificacion": factcheck,
    }
    user = "Material para el editorial:\n\n" + json.dumps(context, ensure_ascii=False, indent=2)

    if review and review.get("verdict") == "needs_revision":
        user += (
            "\n\nNOTAS DE REVISIÓN DEL EDITOR CRÍTICO (corregí cada punto):\n"
            + json.dumps(review.get("issues", []), ensure_ascii=False, indent=2)
            + f"\n\nComentario: {review.get('notes', '')}"
        )

    draft = complete_json(
        system=SYSTEM.format(region=region),
        user=user,
        schema=EDITORIAL_SCHEMA,
        model=s.model_writer,
        max_tokens=12000,
        thinking=True,  # razonamiento adaptativo para mejor calidad de redacción
    )
    n = revision_count + (1 if review else 0)
    return {
        "draft": draft,
        "revision_count": revision_count + 1,
        "log": [f"writer: editorial '{draft.get('title')}' (iteración {n + 1})"],
    }
