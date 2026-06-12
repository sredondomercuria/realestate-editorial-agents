"""Publicador / Distribución.

Publica el editorial en el blog (WordPress) y distribuye las variantes a las redes
sociales vía upload-post. Respeta `DRY_RUN`: si está activo, arma todo pero NO
publica. Skills asociadas: `skills/blog-publishing`, `skills/social-publishing`.
"""

from __future__ import annotations

import re

from ..config import get_settings
from ..integrations.upload_post import UploadPostClient
from ..integrations.wordpress import WordPressClient
from ..state import EditorialState


def _inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def md_to_html(md: str) -> str:
    """Conversión mínima Markdown -> HTML (titulares, párrafos, listas, énfasis, links).

    Para necesidades más complejas reemplazá por la librería `markdown`.
    """
    out: list[str] = []
    in_list = False
    for raw in md.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            continue
        if re.match(r"^[-*]\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = _inline(re.sub(r"^[-*]\s+", "", line))
            out.append(f"<li>{item}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        out.append(f"<p>{_inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def _hashtags(tags: list[str]) -> str:
    if not tags:
        return ""
    return "\n\n" + " ".join("#" + t.lstrip("#").replace(" ", "") for t in tags)


def publisher(state: EditorialState) -> dict:
    s = get_settings()
    draft = state.get("draft", {})
    images = state.get("images", [])
    social = state.get("social", [])
    hero = images[0] if images else {}

    result: dict = {"dry_run": s.dry_run, "blog": None, "social": [], "errors": []}
    body_html = md_to_html(draft.get("body_markdown", ""))

    # --- Modo simulación: no publica, pero deja todo listo para revisar ---
    if s.dry_run:
        result["blog"] = {
            "status": "skipped (dry_run)",
            "title": draft.get("title"),
            "html_chars": len(body_html),
        }
        for v in social:
            result["social"].append(
                {"platform": v.get("platform"), "status": "skipped (dry_run)", "text": v.get("text")}
            )
        return {"publication": result, "log": ["publisher: DRY_RUN activo, no se publicó nada"]}

    # --- Blog: WordPress ---
    try:
        wp = WordPressClient(s.wordpress_url, s.wordpress_user, s.wordpress_app_password)
        featured = None
        if hero.get("path"):
            media = wp.upload_media(hero["path"], hero.get("alt_text", ""))
            featured = media["id"]
        post = wp.create_post(
            title=draft.get("title", ""),
            content_html=body_html,
            status=s.wordpress_status,
            excerpt=draft.get("seo_description", ""),
            slug=draft.get("slug", ""),
            featured_media=featured,
        )
        result["blog"] = {"status": "published", "id": post.get("id"), "link": post.get("link")}
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"wordpress: {exc}")

    # --- Redes sociales: upload-post (una llamada por plataforma con su variante) ---
    if s.uploadpost_api_key and s.uploadpost_user:
        up = UploadPostClient(s.uploadpost_api_key, s.uploadpost_user)
        photos = [hero["path"]] if hero.get("path") else []
        for v in social:
            platform = v.get("platform")
            text = v.get("text", "") + _hashtags(v.get("hashtags", []))
            try:
                if photos:
                    resp = up.upload_photos(
                        title=draft.get("title", ""),
                        photo_paths=photos,
                        platforms=[platform],
                        caption=text,
                    )
                else:
                    resp = up.upload_text(
                        title=draft.get("title", ""), text=text, platforms=[platform]
                    )
                result["social"].append({"platform": platform, "status": "published", "response": resp})
            except Exception as exc:  # noqa: BLE001
                result["social"].append({"platform": platform, "status": "error", "error": str(exc)})
    else:
        result["errors"].append("upload-post: credenciales no configuradas")

    published = result["blog"] and result["blog"].get("status") == "published"
    return {
        "publication": result,
        "log": [f"publisher: blog={'ok' if published else 'fallo'}, redes={len(result['social'])}"],
    }
