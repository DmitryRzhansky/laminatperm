"""Parse and import review cards from static homepage markup."""

from __future__ import annotations

import html
import re
from pathlib import Path

from app.extensions import db
from app.models import Review, ReviewPhoto

BASE_DIR = Path(__file__).resolve().parents[2]

_SLIDE_RE = re.compile(
    r'<li[^>]*\bdata-reviews-slide="(\w+)"[^>]*>\s*<article class="reviews__card">(.*?)</article>',
    re.DOTALL | re.IGNORECASE,
)


def clean_review_text(raw: str) -> str:
    """Strip HTML tags, turn <br> into newlines, normalize whitespace."""
    text = raw or ""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    cleaned: list[str] = []
    blank = False
    for line in lines:
        if not line:
            if cleaned and not blank:
                cleaned.append("")
            blank = True
            continue
        cleaned.append(line)
        blank = False
    return "\n".join(cleaned)


def _static_relpath(url: str) -> str:
    text = (url or "").strip()
    text = text.replace("assets/", "")
    if text.startswith("/static/"):
        text = text[len("/static/") :]
    return text.lstrip("/")


def parse_reviews_html(html_text: str) -> list[dict]:
    items: list[dict] = []
    for index, match in enumerate(_SLIDE_RE.finditer(html_text), start=1):
        platform = match.group(1).strip().lower() or "avito"
        card = match.group(2)
        avatar_match = re.search(r'class="reviews__avatar[^"]*"[^>]*src="([^"]+)"', card)
        if not avatar_match:
            avatar_match = re.search(r'src="([^"]+)"', card)
        author_match = re.search(r'reviews__name">([^<]+)', card)
        role_match = re.search(r'reviews__meta">([^<]+)', card)
        date_match = re.search(r'reviews__date">([^<]+)', card)
        item_match = re.search(r'reviews__item">([^<]+)', card)
        text_match = re.search(r'reviews__text">\s*(.*?)\s*</p>', card, flags=re.DOTALL)
        photo_urls = re.findall(r'data-reviews-letter="([^"]+)"', card)

        items.append(
            {
                "platform": platform if platform in {"avito", "yandex", "vk"} else "avito",
                "author": (author_match.group(1).strip() if author_match else "Клиент"),
                "role": (role_match.group(1).strip() if role_match else ""),
                "date_text": (date_match.group(1).strip() if date_match else ""),
                "item": (item_match.group(1).strip() if item_match else ""),
                "text": clean_review_text(text_match.group(1) if text_match else ""),
                "avatar": _static_relpath(avatar_match.group(1) if avatar_match else ""),
                "photos": [_static_relpath(url) for url in photo_urls if url],
                "sort_order": index,
                "rating": 5,
                "is_published": True,
            }
        )
    return items


def load_reviews_source() -> str:
    candidates = [
        BASE_DIR / "app" / "templates" / "components" / "reviews_section.html",
        BASE_DIR / "index.html",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8")
    return ""


def replace_reviews_from_html(html_text: str | None = None) -> dict[str, int]:
    """Wipe reviews and reimport from homepage markup. Returns counts per platform."""
    source = html_text if html_text is not None else load_reviews_source()
    parsed = parse_reviews_html(source)
    if not parsed:
        return {"total": 0, "avito": 0, "yandex": 0, "vk": 0}

    for review in Review.query.all():
        db.session.delete(review)
    db.session.flush()

    counts = {"avito": 0, "yandex": 0, "vk": 0}
    for data in parsed:
        photos = data.pop("photos")
        platform = data["platform"]
        review = Review(**data)
        db.session.add(review)
        db.session.flush()
        for order, filename in enumerate(photos):
            if not filename:
                continue
            db.session.add(ReviewPhoto(review_id=review.id, filename=filename, sort_order=order))
        counts[platform] = counts.get(platform, 0) + 1

    db.session.commit()
    counts["total"] = sum(v for k, v in counts.items() if k != "total")
    return counts
