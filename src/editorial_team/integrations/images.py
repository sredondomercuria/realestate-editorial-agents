"""Generación de imágenes para acompañar cada post.

Claude no genera imágenes: el agente *ilustrador* usa Claude para escribir el
prompt visual y el alt-text, y aquí se renderiza con un proveedor configurable
(`IMAGE_PROVIDER`):

* `gemini` → API de Google AI Studio (key `GEMINI_API_KEY`, crédito prepago).
* `vertex` → **Vertex AI** en tu proyecto GCP. Factura por GCP (no por el prepago
   de AI Studio). En Cloud Run usa la service account (sin key); localmente usa tus
   credenciales `gcloud` (ADC: `gcloud auth application-default login`).
* `openai` → modelo `gpt-image-1`.
* `none`   → no genera (sólo guarda el prompt).

Modelos: "Nano Banana" (`gemini-3-pro-image`, `gemini-3.1-flash-image`,
`gemini-2.5-flash-image`) o, en Vertex, **Imagen** (`imagen-4.0-generate-001`,
`imagen-4.0-fast-generate-001`). El proveedor está aislado tras `generate_image(...)`.
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
    if provider == "vertex":
        return _generate_vertex(prompt, out_path=out_path)
    if provider == "openai":
        return _generate_openai(prompt, out_path=out_path)

    out_path.with_suffix(".prompt.txt").write_text(prompt, encoding="utf-8")
    return None


def _save_inline_image(resp, out_path: Path) -> str | None:
    """Extrae los bytes de imagen de una respuesta generate_content y los guarda."""
    parts = getattr(resp, "parts", None)
    if parts is None and getattr(resp, "candidates", None):
        parts = resp.candidates[0].content.parts
    for part in parts or []:
        inline = getattr(part, "inline_data", None)
        if inline is not None and getattr(inline, "data", None):
            data = inline.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            out_path.write_bytes(data)
            return str(out_path)
    return None


def _generate_gemini(prompt: str, *, out_path: Path) -> str | None:
    settings = get_settings()
    try:
        from google import genai
    except ImportError:
        print("[images] falta `google-genai`; instalá `pip install google-genai`.")
        return None
    try:
        client = genai.Client(api_key=settings.gemini_api_key or None)
        resp = client.models.generate_content(model=settings.image_model, contents=[prompt])
        saved = _save_inline_image(resp, out_path)
        if not saved:
            print("[images] Gemini no devolvió imagen (¿prompt bloqueado?).")
        return saved
    except Exception as exc:  # noqa: BLE001
        print(f"[images] fallo Gemini: {exc}")
        return None


def _generate_vertex(prompt: str, *, out_path: Path) -> str | None:
    settings = get_settings()
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("[images] falta `google-genai`; instalá `pip install google-genai`.")
        return None
    try:
        client = genai.Client(
            vertexai=True,
            project=settings.gcp_project or None,
            location=settings.vertex_location or "global",
        )
        model = settings.image_model
        if model.startswith("imagen"):
            resp = client.models.generate_images(
                model=model,
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=1),
            )
            imgs = getattr(resp, "generated_images", None) or []
            if imgs:
                out_path.write_bytes(imgs[0].image.image_bytes)
                return str(out_path)
            print("[images] Vertex/Imagen no devolvió imagen.")
            return None
        resp = client.models.generate_content(model=model, contents=[prompt])
        saved = _save_inline_image(resp, out_path)
        if not saved:
            print("[images] Vertex/Gemini no devolvió imagen.")
        return saved
    except Exception as exc:  # noqa: BLE001
        print(f"[images] fallo Vertex: {exc}")
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
