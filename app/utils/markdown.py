from __future__ import annotations

import bleach
import mistune

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "b", "i", "u", "a", "ul", "ol", "li",
    "h2", "h3", "h4", "blockquote", "code", "pre", "hr", "img",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "width", "height"],
}


def render_markdown(source: str) -> str:
    html = mistune.html(source or "")
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=["http", "https", "mailto"],
        strip=True,
    )


def excerpt(text: str, limit: int = 160) -> str:
    clean = bleach.clean(text or "", tags=[], strip=True).strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rsplit(" ", 1)[0] + "…"
