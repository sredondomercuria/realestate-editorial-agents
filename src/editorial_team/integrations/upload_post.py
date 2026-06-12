"""Cliente de upload-post.com para publicar en varias redes a la vez.

upload-post.com expone una API que reenvía el mismo contenido a TikTok,
Instagram, LinkedIn, Facebook, X/Twitter, Threads, Pinterest y YouTube.

Autenticación: header `Authorization: Apikey <API_KEY>`.

Endpoints usados:
* POST https://api.upload-post.com/api/upload_photos  -> post con imágenes
* POST https://api.upload-post.com/api/upload_text     -> post sólo texto

NOTA: los nombres exactos de campos pueden cambiar; verificá la documentación
vigente en https://docs.upload-post.com/ y ajustá si hace falta. El cliente está
hecho para ser fácil de adaptar.
"""

from __future__ import annotations

from pathlib import Path

import requests

BASE = "https://api.upload-post.com/api"


class UploadPostClient:
    def __init__(self, api_key: str, user: str, timeout: int = 60):
        self.api_key = api_key
        self.user = user
        self.timeout = timeout

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Apikey {self.api_key}"}

    def upload_photos(
        self,
        *,
        title: str,
        photo_paths: list[str | Path],
        platforms: list[str],
        caption: str = "",
    ) -> dict:
        """Publica una o más fotos con título/caption en las plataformas indicadas."""
        data: list[tuple[str, str]] = [
            ("user", self.user),
            ("title", title),
            ("caption", caption or title),
        ]
        for platform in platforms:
            data.append(("platform[]", platform))

        files = []
        open_handles = []
        try:
            for p in photo_paths:
                fh = Path(p).open("rb")
                open_handles.append(fh)
                files.append(("photos[]", (Path(p).name, fh, "image/png")))

            resp = requests.post(
                f"{BASE}/upload_photos",
                headers=self._headers,
                data=data,
                files=files or None,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()
        finally:
            for fh in open_handles:
                fh.close()

    def upload_text(self, *, title: str, text: str, platforms: list[str]) -> dict:
        """Publica un post sólo de texto."""
        data: list[tuple[str, str]] = [
            ("user", self.user),
            ("title", title),
            ("text", text),
        ]
        for platform in platforms:
            data.append(("platform[]", platform))

        resp = requests.post(
            f"{BASE}/upload_text",
            headers=self._headers,
            data=data,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()
