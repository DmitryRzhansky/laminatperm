from __future__ import annotations

import re
from unicodedata import normalize


_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(value: str, fallback: str = "item") -> str:
    text = normalize("NFKD", value or "").strip().lower()
    chars = []
    for char in text:
        if char in _TRANSLIT:
            chars.append(_TRANSLIT[char])
        elif char.isascii() and (char.isalnum() or char in "-_"):
            chars.append(char)
        elif char.isspace() or char in "./\\":
            chars.append("-")
    slug = re.sub(r"-{2,}", "-", "".join(chars)).strip("-")
    return slug or fallback


def unique_slug(model, base: str, current_id: int | None = None, field: str = "slug") -> str:
    slug = slugify(base)
    candidate = slug
    index = 2
    query = model.query.filter(getattr(model, field) == candidate)
    if current_id is not None:
        query = query.filter(model.id != current_id)
    while query.first():
        candidate = f"{slug}-{index}"
        index += 1
        query = model.query.filter(getattr(model, field) == candidate)
        if current_id is not None:
            query = query.filter(model.id != current_id)
    return candidate
