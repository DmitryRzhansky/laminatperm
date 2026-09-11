from __future__ import annotations

import html
import re
from typing import Callable, Iterable
from urllib.parse import urlencode

from flask import request
from werkzeug.datastructures import MultiDict

Normalizer = Callable[[str], str]


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(str(value)).replace("\xa0", " ").replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.rstrip(" .")


def normalize_thickness(value: str) -> str:
    text = clean_text(value).replace(",", ".")
    match = re.search(r"(\d+(?:\.\d+)?)\s*мм", text, flags=re.IGNORECASE)
    if match:
        number = match.group(1)
        if number.endswith(".0"):
            number = number[:-2]
        return f"{number} мм"
    match = re.fullmatch(r"(\d+(?:\.\d+)?)", text)
    if match:
        number = match.group(1)
        if number.endswith(".0"):
            number = number[:-2]
        return f"{number} мм"
    return clean_text(value)


def normalize_wear(value: str) -> str:
    text = clean_text(value)
    text = re.sub(r"(?i)^класс\s*", "", text).strip(" :.-")
    return text


def normalize_generic(value: str) -> str:
    return clean_text(value)


def _thickness_from_html(description_html: str | None) -> str:
    if not description_html:
        return ""
    text = html.unescape(description_html).replace("\xa0", " ")
    match = re.search(
        r"Толщина(?:\s*,?\s*мм)?\s*(?:</[^>]+>\s*)*([\d.,]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return ""
    return normalize_thickness(f"{match.group(1)} мм")


class FilterSpec:
    def __init__(
        self,
        key: str,
        label: str,
        attr_names: tuple[str, ...] = (),
        normalize: Normalizer = normalize_generic,
        source: str = "attr",
    ) -> None:
        self.key = key
        self.label = label
        self.attr_names = attr_names
        self.normalize = normalize
        self.source = source

    def values_for(self, product) -> list[str]:
        if self.source == "brand":
            brand = clean_text(product.brand)
            return [brand] if brand else []

        values: list[str] = []
        wanted = {name.lower() for name in self.attr_names}
        for item in product.attributes:
            name = clean_text(item.name)
            if name.lower() not in wanted:
                continue
            raw = clean_text(item.value)
            if not raw or len(raw) > 60:
                continue
            normalized = self.normalize(raw)
            if normalized and normalized not in values:
                values.append(normalized)

        if self.key == "thickness" and not values:
            from_html = _thickness_from_html(getattr(product, "description_html", ""))
            if from_html:
                values.append(from_html)
        return values


FILTER_SPECS: tuple[FilterSpec, ...] = (
    FilterSpec("brand", "Бренд", source="brand"),
    FilterSpec(
        "thickness",
        "Толщина",
        ("Общая толщина", "Толщина", "Высота", "Толщина полотна, мм", "Толщина, мм"),
        normalize=normalize_thickness,
    ),
    FilterSpec(
        "wear",
        "Класс помещения",
        ("Класс помещения", "Класс износостойкости"),
        normalize=normalize_wear,
    ),
    FilterSpec(
        "wear_layer",
        "Защитный слой",
        ("Толщина защитного слоя",),
        normalize=normalize_thickness,
    ),
    FilterSpec("connection", "Тип соединения", ("Тип соединения",)),
    FilterSpec("lifetime", "Срок службы", ("Срок службы",)),
    FilterSpec("bevel", "Фаска", ("Фаска", "Вид фаски")),
    FilterSpec("base", "Тип основы", ("Тип основы",)),
    FilterSpec("application", "Сфера применения", ("Сфера применения",)),
    FilterSpec("country", "Страна", ("Страна производства",)),
)

SORT_OPTIONS = (
    ("default", "По умолчанию"),
    ("price_asc", "Сначала дешевле"),
    ("price_desc", "Сначала дороже"),
    ("name", "По названию"),
)


def selected_values(spec: FilterSpec | str) -> list[str]:
    if isinstance(spec, str):
        key = spec
        normalize = clean_text
    else:
        key = spec.key
        normalize = spec.normalize if spec.source == "attr" else clean_text

    values: list[str] = []
    for value in request.args.getlist(key):
        cleaned = clean_text(value)
        if not cleaned:
            continue
        normalized = normalize(cleaned)
        if normalized and normalized not in values:
            values.append(normalized)
    return values


def collect_filter_options(products: Iterable) -> list[dict]:
    groups: list[dict] = []
    for spec in FILTER_SPECS:
        bucket: dict[str, int] = {}
        for product in products:
            for value in spec.values_for(product):
                bucket[value] = bucket.get(value, 0) + 1
        options = [
            {"value": value, "count": count}
            for value, count in sorted(bucket.items(), key=lambda item: item[0].lower())
        ]
        selected = selected_values(spec)
        if spec.key == "brand":
            if options:
                groups.append(
                    {
                        "key": spec.key,
                        "label": spec.label,
                        "options": options,
                        "selected": selected,
                    }
                )
            continue
        if len(options) >= 2:
            groups.append(
                {
                    "key": spec.key,
                    "label": spec.label,
                    "options": options,
                    "selected": selected,
                }
            )
    return groups


def apply_product_filters(products: list) -> list:
    selected = {spec.key: set(selected_values(spec)) for spec in FILTER_SPECS}
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)

    filtered = []
    for product in products:
        price = float(product.price or 0)
        if price_min is not None and price < price_min:
            continue
        if price_max is not None and price > price_max:
            continue

        matches = True
        for spec in FILTER_SPECS:
            wanted = selected[spec.key]
            if not wanted:
                continue
            values = set(spec.values_for(product))
            if not values.intersection(wanted):
                matches = False
                break
        if matches:
            filtered.append(product)
    return filtered


def sort_products(products: list) -> list:
    sort = request.args.get("sort", "default")
    items = list(products)
    if sort == "price_asc":
        items.sort(key=lambda item: float(item.price or 0))
    elif sort == "price_desc":
        items.sort(key=lambda item: float(item.price or 0), reverse=True)
    elif sort == "name":
        items.sort(key=lambda item: item.name.lower())
    else:
        items.sort(key=lambda item: (item.sort_order, item.id))
    return items


def catalog_query(**overrides) -> str:
    args = MultiDict()
    for key in request.args:
        for value in request.args.getlist(key):
            if key in {"price_min", "price_max"}:
                if str(value).strip() != "":
                    args.add(key, value)
                continue
            cleaned = clean_text(value)
            if cleaned:
                args.add(key, cleaned)

    for key, value in overrides.items():
        args.poplist(key)
        if value is None or value == "":
            continue
        if isinstance(value, (list, tuple, set)):
            for item in value:
                if item is not None and str(item) != "":
                    args.add(key, str(item))
        else:
            args.add(key, str(value))

    return urlencode(list(args.items(multi=True)))
