"""Generate marketing product descriptions from catalog attributes."""

from __future__ import annotations

import html
import re

from app.models.catalog import Product

_SPEC_LINE = re.compile(r"^[^:]{2,40}:\s*.+$")


def looks_like_spec_dump(description_html: str | None) -> bool:
    """True when description is only attribute lines (typical Tilda import)."""
    if not description_html or not description_html.strip():
        return True

    # Already filled by our generator.
    if "Ламинейшен" in description_html and "<ul>" in description_html:
        return False
    if description_html.lstrip().startswith("<p><strong>") and "</ul>" in description_html:
        return False

    text = (
        description_html.replace("<br />", "\n")
        .replace("<br/>", "\n")
        .replace("<br>", "\n")
        .replace("&nbsp;", " ")
    )
    text = re.sub(r"<[^>]+>", "\n", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return True

    # Tilda often stores "Label<br>Value" without colons.
    if "<p>" not in description_html.lower() and len(lines) >= 2:
        return True

    spec_lines = sum(1 for line in lines if _SPEC_LINE.match(line))
    return spec_lines >= max(1, len(lines) - 1)



def _attr_map(product: Product) -> dict[str, str]:
    return {item.name.strip().lower(): item.value.strip() for item in product.attributes if item.name}


def _get(attrs: dict[str, str], *names: str) -> str:
    for name in names:
        value = attrs.get(name.lower())
        if value:
            return value
    return ""


def _decor_label(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", name).strip()
    if " - " in cleaned or " — " in cleaned:
        cleaned = re.split(r"\s+[—-]\s+", cleaned, maxsplit=1)[-1].strip()
    parts = cleaned.split()
    if len(parts) >= 2 and parts[0].isdigit():
        cleaned = " ".join(parts[1:])
    return cleaned.title() if cleaned.isupper() or cleaned == cleaned.upper() else cleaned


def display_name(product: Product) -> str:
    """Human title without duplicated brand / ALL CAPS noise."""
    raw = re.sub(r"\s+", " ", (product.name or "").strip())
    if not raw:
        return ""

    tokens = raw.split()
    deduped: list[str] = []
    for token in tokens:
        if deduped and deduped[-1].casefold() == token.casefold():
            continue
        deduped.append(token)
    name = " ".join(deduped)
    name = re.sub(r"\s+-\s+", " — ", name)

    pieces: list[str] = []
    for chunk in re.split(r"( — )", name):
        if chunk == " — ":
            pieces.append(chunk)
            continue
        if chunk.isupper() and any(ch.isalpha() for ch in chunk):
            pieces.append(chunk.title())
        else:
            pieces.append(chunk)
    return "".join(pieces).strip() or raw


def product_buybox_teaser(product: Product) -> str:
    """Short buy-box blurb without repeating the full product title."""
    attrs = _attr_map(product)
    brand = _brand_label(product)
    title = display_name(product) or product.name
    decor = _decor_label(title)
    category = _category_label(product)
    wear = _get(attrs, "класс помещения", "класс применения")
    thickness = _get(attrs, "общая толщина", "толщина")
    life = _get(attrs, "срок службы", "гарантия")

    if _category_kind(product) == "accessory":
        return "Подберём совместимый вариант под покрытие, посчитаем расход и наличие."

    bits: list[str] = []
    if wear:
        bits.append(f"класс {wear}")
    if thickness:
        bits.append(f"толщина {thickness}")
    if life:
        bits.append(f"срок службы до {life}")

    lead = f"{category[0].upper()}{category[1:]}"
    if decor and decor.casefold() not in title.casefold():
        lead += f" «{decor}»"
    elif brand and brand not in {"производителя", "сопутствующих материалов"}:
        lead += f" {brand}"
    if bits:
        return f"{lead}: {', '.join(bits)}. Поможем с расчётом метража и укладкой в Перми."
    return f"{lead}. Поможем с расчётом метража и укладкой в Перми."


def _category_label(product: Product) -> str:
    slug = product.category.slug if product.category else ""
    labels = {
        "laminat": "ламинат",
        "linoleum": "линолеум",
        "spc": "SPC-плитка",
        "kleevoy-lvt": "клеевой LVT",
        "aksessuary": "аксессуар для укладки",
    }
    return labels.get(slug, "напольное покрытие")


def _category_kind(product: Product) -> str:
    slug = product.category.slug if product.category else ""
    return {
        "laminat": "laminat",
        "linoleum": "linoleum",
        "spc": "spc",
        "kleevoy-lvt": "lvt",
        "aksessuary": "accessory",
    }.get(slug, "other")


def _brand_label(product: Product) -> str:
    brand = (product.brand or "").strip()
    if not brand:
        return "производителя"
    # Accessories sometimes store the whole title as brand.
    if product.category and product.category.slug == "aksessuary":
        if len(brand) > 24 or brand.lower() in product.name.lower()[: len(brand) + 2]:
            first = product.name.split()[0]
            if first.lower() not in {"подложка-гармошка", "подложка"}:
                return first.title()
            return "сопутствующих материалов"
    return brand


def build_product_description_html(product: Product) -> str:
    """Return unique marketing HTML for a product card."""
    attrs = _attr_map(product)
    brand = _brand_label(product)
    decor = _decor_label(product.name)
    kind = _category_kind(product)
    category = _category_label(product)
    wear = _get(attrs, "класс помещения", "класс применения")
    thickness = _get(attrs, "общая толщина", "толщина")
    lock = _get(attrs, "тип соединения", "замок", "тип замка")
    life = _get(attrs, "срок службы", "гарантия")
    base = _get(attrs, "тип основания", "основание")
    wear_layer = _get(attrs, "толщина защитного слоя", "защитный слой")
    base_type = _get(attrs, "тип основы")
    country = _get(attrs, "страна производства", "страна")
    application = _get(attrs, "назначение", "область применения")

    safe_brand = html.escape(brand)
    safe_decor = html.escape(decor)
    safe_title = html.escape(display_name(product) or product.name)

    if kind == "accessory":
        return _accessory_html(product, safe_brand, safe_title, attrs)

    intro = (
        f"<p><strong>{safe_title}</strong> — {category} {safe_brand} "
        f"в декоре «{safe_decor}». Подходит для квартир, домов и коммерческих "
        f"помещений в Перми: поможем с расчётом метража, подложкой и укладкой.</p>"
    )

    facts: list[str] = []
    if wear:
        facts.append(f"класс применения {html.escape(wear)}")
    if thickness:
        facts.append(f"толщина {html.escape(thickness)}")
    if lock:
        facts.append(f"соединение {html.escape(lock)}")
    if wear_layer:
        facts.append(f"защитный слой {html.escape(wear_layer)}")
    if base or base_type:
        facts.append(f"основание {html.escape(base or base_type)}")
    if life:
        facts.append(f"срок службы до {html.escape(life)}")
    if country:
        facts.append(f"производство: {html.escape(country)}")
    if application:
        facts.append(f"назначение: {html.escape(application)}")

    if kind == "laminat":
        body = (
            "<p>Ламинированное покрытие с реалистичной текстурой дерева: "
            "устойчиво к повседневным нагрузкам, легко моется и быстро монтируется "
            "на ровное основание. "
        )
        if facts:
            body += "Ключевые параметры: " + ", ".join(facts) + ".</p>"
        else:
            body += "Параметры партии уточняйте у менеджера в шоуруме.</p>"
        bullets = [
            "Подбор под интерьер и нагрузку помещения",
            "Расчёт материала с запасом на подрезку",
            "Доставка по Перми и профессиональная укладка",
        ]
    elif kind == "linoleum":
        body = (
            "<p>Рулонное покрытие с износостойким защитным слоем — практичный вариант "
            "для жилых комнат, кухни и коммерции. "
        )
        if facts:
            body += "В этой позиции: " + ", ".join(facts) + ".</p>"
        else:
            body += "Точные характеристики смотрите во вкладке «Характеристики».</p>"
        bullets = [
            "Можно посмотреть образцы в шоуруме на Агатовой, 28",
            "Помогаем стыковать цвет с плинтусом и порогами",
            "Возможен монтаж под ключ",
        ]
    elif kind == "spc":
        body = (
            "<p>Жёсткая SPC-плитка не боится влаги и перепадов температуры, "
            "поэтому её часто выбирают для кухни, коридора и коммерческих зон. "
        )
        if facts:
            body += "Характеристики модели: " + ", ".join(facts) + ".</p>"
        else:
            body += "Полный список параметров — во вкладке ниже.</p>"
        bullets = [
            "Влагостойкая конструкция без разбухания",
            "Замковый монтаж на подготовленное основание",
            "Совместимость с тёплым полом — уточняйте по коллекции",
        ]
    else:  # lvt / other
        body = (
            "<p>Клеевое виниловое покрытие с износостойкой поверхностью — "
            "для помещений, где важны влагостойкость и аккуратный шов. "
        )
        if facts:
            body += "Параметры: " + ", ".join(facts) + ".</p>"
        else:
            body += "Детали партии уточним при заказе.</p>"
        bullets = [
            "Ровный визуал и плотное прилегание к основанию",
            "Подходит для жилых и коммерческих объектов",
            "Подберём клей и сопутствующие материалы",
        ]

    list_html = "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in bullets) + "</ul>"
    outro = (
        "<p>В «Ламинейшен» можно заказать образцы, расчёт сметы и укладку. "
        "Оставьте заявку на странице — перезвоним и подтвердим наличие.</p>"
    )
    return intro + body + list_html + outro


def _accessory_html(product: Product, safe_brand: str, safe_name: str, attrs: dict[str, str]) -> str:
    name_l = product.name.lower()
    if "подлож" in name_l:
        role = "подложка выравнивает мелкие неровности, гасит шаги и продлевает срок службы покрытия"
    elif "плинт" in name_l:
        role = "плинтус закрывает компенсационный зазор и завершает вид пола"
    elif "клей" in name_l:
        role = "клей обеспечивает надёжную фиксацию клеевых покрытий"
    else:
        role = "комплектующее необходимо для аккуратного монтажа напольного покрытия"

    facts = []
    for key, value in attrs.items():
        facts.append(f"{html.escape(key)}: {html.escape(value)}")

    brand_bit = ""
    if safe_brand and safe_brand not in {"производителя", "сопутствующих материалов"}:
        brand_bit = f" Бренд {safe_brand}."

    intro = (
        f"<p><strong>{safe_name}</strong> — {role}.{brand_bit} "
        f"Подберём совместимый вариант под ваше покрытие.</p>"
    )
    body = "<p>Рекомендуем брать аксессуары вместе с основным материалом, чтобы совпали цвет, толщина и технология укладки.</p>"
    if facts:
        body += "<p>" + "; ".join(facts) + ".</p>"
    outro = "<p>Нужна консультация — оставьте заявку, подскажем расход и наличие на складе.</p>"
    return intro + body + outro


def description_teaser(description_html: str | None, limit: int = 220) -> str:
    """Plain-text teaser for the buy box."""
    if not description_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", description_html)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"
