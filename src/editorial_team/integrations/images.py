"""Generación de imágenes para acompañar cada post.

Claude no genera imágenes: el agente *ilustrador* usa Claude para escribir el
prompt visual y el alt-text, y aquí se renderiza con un proveedor configurable:

* `gemini` (por defecto) → modelos "Nano Banana" de Google
   - `gemini-3-pro-image`     (Nano Banana Pro, calidad pro, texto fiel)
   - `gemini-3.1-flash-image` (Nano Banana 2, rápido, 4K)
   - `gemini-2.5-flash-image` (Nano Banana)
* `openai` → modelo `gpt-image-1`
* `none`   → no genera (sólo guarda el prompt)

Cada proveedor está aislado tras `generate_image(...)` para que puedas
reemplazarlo sin tocar el resto del workflow.
"""

from __future__ import annotations

import base64
from pathlib import Path

from ..config import get_settings


def generate_image(prompt: str, *, out_path: str | Path) -> str | None:
    """Genera una imagen para `prompt` y la guarda en `out_path`.

    Devuelve la ruta del archivo generado, o `None` si no se generó.
    """
    settings = get_settings()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    provider = settings.image_provider
    if provider == "gemini":
        return _generate_gemini(prompt, out_path=out_path)
    if provider == "openai":
        return _generate_openai(prompt, out_path=out_path)

    # 'none': no genera imagen, sólo registra el prompt al lado.
    out_path.with_suffix(".prompt.txt").write_text(prompt, encoding="utf-8")
    return None


def _generate_gemini(prompt: str, *, out_path: Path) -> str | None:
    settings = get_settings()
    try:
        from google import genai  # import perezoso: dependencia opcional
    except ImportError:
        print("[images] falta `google-genai`; instalá `pip install google-genai`.")
        return None

    try:
        # El cliente toma la API key de GEMINI_API_KEY/GOOGLE_API_KEY o del arg.
        client = genai.Client(api_key=settings.gemini_api_key or None)
        resp = client.models.generate_content(
            model=settings.image_model,
            contents=[prompt],
        )
        # La imagen viene como inline_data (bytes) en alguna de las parts.
        parts = getattr(resp, "parts", None)
        if parts is None and getattr(resp, "candidates", None):
            parts = resp.candidates[0].content.parts
        for part in parts or []:
            inline = getattr(part, "inline_data", None)
            if inline is not None and getattr(inline, "data", None):
                data = inline.data
                if isinstance(data, str):  # por si viene en base64
                    data = base64.b64decode(data)
                out_path.write_bytes(data)
                return str(out_path)
        print("[images] Gemini no devolvió imagen (¿prompt bloqueado?).")
        return None
    except Exception as exc:  # noqa: BLE001 — una imagen no debe tumbar el pipeline
        print(f"[images] fallo Gemini: {exc}")
        return None


def _generate_openai(prompt: str, *, out_path: Path) -> str | None:
    settings = get_settings()
    try:
        from openai import OpenAI
    except ImportError:
        print("[images] falta `openai`; instalá `pip install openai`.")
        return None

    try:
        client = OpenAI(api_key=settings.openai_api_key or None)
        result = client.images.generate(
            model="gpt-image-1", prompt=prompt, size=settings.image_size, n=1
        )
        out_path.write_bytes(base64.b64decode(result.data[0].b64_json))
        return str(out_path)
    except Exception as exc:  # noqa: BLE001
        print(f"[images] fallo OpenAI: {exc}")
        return None
