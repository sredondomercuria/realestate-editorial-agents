"""Generación de imágenes para acompañar cada post.

Claude no genera imágenes: el agente *ilustrador* usa Claude para escribir un
prompt visual detallado y el alt-text, y aquí se renderiza con un proveedor de
imágenes configurable. Por defecto `IMAGE_PROVIDER=none` (no genera nada, sólo
deja el brief). Si se configura `openai`, usa el modelo `gpt-image-1`.

Es el único punto del proyecto que depende de un proveedor distinto de Anthropic;
está aislado detrás de esta interfaz para que puedas reemplazarlo (Stability,
Replicate, Vertex, etc.) sin tocar el resto del workflow.
"""

from __future__ import annotations

import base64
from pathlib import Path

from ..config import get_settings


def generate_image(prompt: str, *, out_path: str | Path) -> str | None:
    """Genera una imagen para `prompt` y la guarda en `out_path`.

    Devuelve la ruta del archivo generado, o `None` si no se generó (proveedor
    `none` o error controlado).
    """
    settings = get_settings()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if settings.image_provider == "openai":
        return _generate_openai(prompt, out_path=out_path)

    # Proveedor 'none': no genera imagen, sólo registra el brief al lado.
    out_path.with_suffix(".prompt.txt").write_text(prompt, encoding="utf-8")
    return None


def _generate_openai(prompt: str, *, out_path: Path) -> str | None:
    settings = get_settings()
    try:
        from openai import OpenAI  # import perezoso: dependencia opcional
    except ImportError:
        print("[images] openai no está instalado; instalá `pip install openai`.")
        return None

    try:
        client = OpenAI(api_key=settings.openai_api_key or None)
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=settings.image_size,
            n=1,
        )
        b64 = result.data[0].b64_json
        out_path.write_bytes(base64.b64decode(b64))
        return str(out_path)
    except Exception as exc:  # noqa: BLE001 — no queremos que una imagen tumbe el pipeline
        print(f"[images] fallo generando imagen: {exc}")
        return None
