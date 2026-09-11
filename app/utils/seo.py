from __future__ import annotations

from app.utils.markdown import excerpt
from app.utils.slugs import unique_slug


def apply_seo(instance, title: str, summary: str = "", slug_model=None) -> None:
    clean = title.strip()
    if hasattr(instance, "title"):
        instance.title = clean
    if not instance.slug and slug_model is not None:
        instance.slug = unique_slug(slug_model, clean, getattr(instance, "id", None))
    if not (instance.seo_title or "").strip():
        instance.seo_title = clean
    if not (instance.seo_description or "").strip():
        instance.seo_description = excerpt(summary or clean, 160)
