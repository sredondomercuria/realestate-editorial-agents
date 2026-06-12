"""Cliente mínimo de la REST API de WordPress.

Publica el editorial en un blog WordPress usando autenticación por
*Application Password* (WordPress -> Usuarios -> Perfil -> Contraseñas de
aplicación). Soporta subir una imagen destacada y crear el post.

Docs: https://developer.wordpress.org/rest-api/reference/posts/
"""

from __future__ import annotations

import mimetypes
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth


class WordPressClient:
    def __init__(self, base_url: str, user: str, app_password: str, timeout: int = 30):
        self.base = base_url.rstrip("/")
        self.auth = HTTPBasicAuth(user, app_password)
        self.timeout = timeout

    @property
    def api(self) -> str:
        return f"{self.base}/wp-json/wp/v2"

    def upload_media(self, image_path: str | Path, alt_text: str = "") -> dict:
        """Sube una imagen a la biblioteca de medios. Devuelve el objeto media."""
        image_path = Path(image_path)
        mime = mimetypes.guess_type(image_path.name)[0] or "image/png"
        with image_path.open("rb") as fh:
            resp = requests.post(
                f"{self.api}/media",
                auth=self.auth,
                headers={"Content-Disposition": f'attachment; filename="{image_path.name}"'},
                files={"file": (image_path.name, fh, mime)},
                timeout=self.timeout,
            )
        resp.raise_for_status()
        media = resp.json()

        if alt_text:
            requests.post(
                f"{self.api}/media/{media['id']}",
                auth=self.auth,
                json={"alt_text": alt_text},
                timeout=self.timeout,
            )
        return media

    def create_post(
        self,
        *,
        title: str,
        content_html: str,
        status: str = "draft",
        excerpt: str = "",
        slug: str = "",
        featured_media: int | None = None,
        tags: list[int] | None = None,
    ) -> dict:
        """Crea un post. Devuelve el objeto post (incluye `link` e `id`)."""
        payload: dict = {
            "title": title,
            "content": content_html,
            "status": status,
            "excerpt": excerpt,
            "slug": slug,
        }
        if featured_media:
            payload["featured_media"] = featured_media
        if tags:
            payload["tags"] = tags

        resp = requests.post(
            f"{self.api}/posts", auth=self.auth, json=payload, timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()
