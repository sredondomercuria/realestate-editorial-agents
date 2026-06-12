"""Lógica de publicación reutilizable (blog + redes).

Se separa del nodo `publisher` para que también la pueda invocar la UI cuando un
humano aprueba un editorial guardado ("aprobar y publicar"). Recibe `dry_run`
explícito: el nodo usa el de la config; la UI fuerza `dry_run=False` al aprobar.
"""

from __future__ import annotations

import re

from .config import get_settings
from .integrations.upload_post import UploadPostClient
from .integrations.wordpress import WordPressClient


def _inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def md_to_html(md: str) -> str:
    """Markdown -> HTML. Usa la librería `markdown` si está; si no, fallback mínimo."""
    try:
        import markdown as _md

        return _md.markdown(md or "", extensions=["extra", "sane_lists"])
    except ImportError:
        pass

    out: list[str] = []
    in_list = False
    for raw in (md or "").split("\n"):
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


def do_publish(*, draft: dict, images: list[dict], social: list[dict], dry_run: bool) -> dict:
    """Publica el editorial en blog + redes. Devuelve un dict con el resultado."""
    settings = get_settings()
    hero = images[0] if images else {}
    result: dict = {"dry_run": dry_run, "blog": None, "social": [], "errors": []}
    body_html = md_to_html(draft.get("body_markdown", ""))

    if dry_run:
        result["blog"] = {
            "status": "skipped (dry_run)",
            "title": draft.get("title"),
            "html_chars": len(body_html),
        }
        for v in social:
            result["social"].append(
                {"platform": v.get("platform"), "status": "skipped (dry_run)", "text": v.get("text")}
            )
        return result

    # --- Blog: WordPress ---
    try:
        wp = WordPressClient(
            settings.wordpress_url, settings.wordpress_user, settings.wordpress_app_password
        )
        featured = None
        if hero.get("path"):
            media = wp.upload_media(hero["path"], hero.get("alt_text", ""))
            featured = media["id"]
        post = wp.create_post(
            title=draft.get("title", ""),
            content_html=body_html,
            status=settings.wordpress_status,
            excerpt=draft.get("seo_description", ""),
            slug=draft.get("slug", ""),
            featured_media=featured,
        )
        result["blog"] = {"status": "published", "id": post.get("id"), "link": post.get("link")}
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"wordpress: {exc}")

    # --- Redes: upload-post (una llamada por plataforma con su variante) ---
    if settings.uploadpost_api_key and settings.uploadpost_user:
        up = UploadPostClient(settings.uploadpost_api_key, settings.uploadpost_user)
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
                    resp = up.upload_text(title=draft.get("title", ""), text=text, platforms=[platform])
                result["social"].append({"platform": platform, "status": "published", "response": resp})
            except Exception as exc:  # noqa: BLE001
                result["social"].append({"platform": platform, "status": "error", "error": str(exc)})
    else:
        result["errors"].append("upload-post: credenciales no configuradas")

    return result
