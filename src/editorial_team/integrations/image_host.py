"""Hosting de imágenes en un CDN para obtener una URL pública.

Útil para incrustar la imagen en el blog/redes desde una URL estable. Proveedor
configurable con `IMAGE_HOST`:

* `cloudinary` → sube a Cloudinary (usa `CLOUDINARY_URL`).
* `none`       → no sube; devuelve None.

Alternativa GCP: Google Cloud Storage (subir el blob y hacerlo público o firmar
una URL). Ver `docs/10-deploy-gcp.md`.
"""

from __future__ import annotations

from pathlib import Path

from ..config import get_settings


def upload_public(image_path: str | Path, *, public_id: str | None = None) -> str | None:
    """Sube `image_path` al CDN configurado. Devuelve la URL pública o None."""
    settings = get_settings()
    if settings.image_host != "cloudinary" or not image_path:
        return None

    try:
        import cloudinary
        import cloudinary.uploader
    except ImportError:
        print("[image_host] falta `cloudinary`; instalá `pip install cloudinary`.")
        return None

    try:
        # cloudinary.config() lee CLOUDINARY_URL del entorno automáticamente.
        cloudinary.config(cloudinary_url=settings.cloudinary_url or None)
        result = cloudinary.uploader.upload(
            str(image_path),
            public_id=public_id,
            folder="editorial",
            overwrite=True,
            resource_type="image",
        )
        return result.get("secure_url")
    except Exception as exc:  # noqa: BLE001
        print(f"[image_host] fallo Cloudinary: {exc}")
        return None
