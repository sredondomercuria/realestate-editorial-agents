"""Ilustrador / Director de arte.

Convierte el brief visual del editorial en un prompt de imagen profesional + alt-text,
genera la imagen con el proveedor configurado (Gemini "Nano Banana" por defecto) y,
si hay CDN configurado, la sube para obtener una URL pública. Skill: `skills/image-generation`.
"""

from __future__ import annotations

from pathlib import Path

from ..config import get_settings
from ..integrations.image_host import upload_public
from ..integrations.images import generate_image
from ..llm import complete_json
from ..schemas import IMAGE_PROMPT_SCHEMA
from ..state import EditorialState

SYSTEM = """\
Sos director/a de arte de un medio profesional de Real Estate. A partir del título y
el brief, escribís UN prompt en inglés para un modelo de generación de imágenes que
produzca una foto/ilustración editorial de calidad (realista, sobria, sin texto
incrustado, sin logos, sin marcas de agua). Incluí: encuadre, iluminación, paleta y
mood. `negative_prompt` lista lo que hay que evitar. `alt_text` describe la imagen en
español para accesibilidad. `caption` es un epígrafe breve en español.
"""


def illustrator(state: EditorialState) -> dict:
    s = get_settings()
    draft = state.get("draft", {})

    spec = complete_json(
        system=SYSTEM,
        user=(
            f"Título: {draft.get('title')}\n"
            f"Bajada: {draft.get('dek')}\n"
            f"Brief visual: {draft.get('image_brief')}"
        ),
        schema=IMAGE_PROMPT_SCHEMA,
        model=s.model_illustrator,
    )

    slug = draft.get("slug") or "editorial"
    out_path = Path("images") / f"{slug}.png"
    full_prompt = spec["prompt"]
    if spec.get("style"):
        full_prompt += f" Style: {spec['style']}."

    image_path = generate_image(full_prompt, out_path=out_path)
    public_url = upload_public(image_path, public_id=slug) if image_path else None

    images = [
        {
            "role": "hero",
            "path": image_path,         # None si IMAGE_PROVIDER=none
            "public_url": public_url,   # None si IMAGE_HOST=none
            "prompt": full_prompt,
            "negative_prompt": spec.get("negative_prompt", ""),
            "alt_text": spec.get("alt_text", ""),
            "caption": spec.get("caption", ""),
        }
    ]
    where = "Gemini" if s.image_provider == "gemini" else s.image_provider
    state_msg = f"generada ({where})" if image_path else f"no generada ({s.image_provider})"
    hosted = " + CDN" if public_url else ""
    return {"images": images, "log": [f"illustrator: imagen hero {state_msg}{hosted}"]}
