"""Crítico / Editor responsable (revalidación crítica).

Hace una revisión adversarial del borrador: revalida los datos centrales con la web
(independientemente del fact-checker), busca sesgos, problemas de claridad, de
atribución de fuentes y riesgos legales, y emite un veredicto. Si pide cambios, el
grafo devuelve el control al redactor. Skill asociada: `skills/critical-review`.
"""

from __future__ import annotations

import json

from ..config import get_settings
from ..llm import complete_json, research
from ..schemas import REVIEW_SCHEMA
from ..state import EditorialState

REVALIDATE_SYSTEM = """\
Sos editor/a responsable y escéptico/a. Tomá las 2-3 cifras o afirmaciones MÁS
importantes de este editorial y revalidalas con búsquedas web INDEPENDIENTES (no
confíes en el fact-check previo). Reportá si cada una se sostiene, con la URL de la
fuente. Sé breve y concreto/a.
"""

REVIEW_SYSTEM = """\
Sos el/la editor/a responsable de la publicación. Hacés el control de calidad final
antes de publicar, con mirada adversarial. Evaluá el borrador en estas dimensiones:
- factual: ¿hay datos sin respaldo, contradichos por tu revalidación, o mal atribuidos?
- sourcing: ¿cada cifra tiene fuente citada? ¿las fuentes son confiables?
- clarity: ¿la tesis es clara? ¿se entiende?
- bias: ¿hay sesgo, lenguaje promocional o conclusiones no sustentadas?
- legal: ¿promete rendimientos, da consejo financiero, o difama?
- style: ¿cumple el estándar profesional y la guía de estilo?

`score` es 0-100. Devolvé `verdict = needs_revision` si hay CUALQUIER issue de
severidad `high`, o varios `medium`. Para cada issue incluí un `fix` accionable.
Sé exigente: es preferible una revisión más que publicar algo con un error.
"""


def critic(state: EditorialState) -> dict:
    s = get_settings()
    draft = state.get("draft", {})
    factcheck = state.get("factcheck", {})

    # Paso 1: revalidación independiente de las cifras centrales (con web).
    revalidation = research(
        system=REVALIDATE_SYSTEM,
        user=(
            f"Título: {draft.get('title')}\n\n"
            f"Editorial:\n{draft.get('body_markdown', '')}"
        ),
        model=s.model_critic,
        max_uses=6,
    )

    # Paso 2: veredicto estructurado de calidad.
    user = (
        "BORRADOR:\n"
        + json.dumps(
            {k: draft.get(k) for k in ("title", "dek", "body_markdown", "sources")},
            ensure_ascii=False,
            indent=2,
        )
        + "\n\nVERIFICACIÓN PREVIA (fact-checker):\n"
        + json.dumps(factcheck, ensure_ascii=False, indent=2)
        + "\n\nTU REVALIDACIÓN INDEPENDIENTE:\n"
        + revalidation
    )

    review = complete_json(
        system=REVIEW_SYSTEM,
        user=user,
        schema=REVIEW_SCHEMA,
        model=s.model_critic,
        max_tokens=8000,
        thinking=True,
    )
    return {
        "review": review,
        "log": [
            f"critic: verdict={review.get('verdict')} score={review.get('score')} "
            f"issues={len(review.get('issues', []))}"
        ],
    }
