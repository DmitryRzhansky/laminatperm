from __future__ import annotations

DELIVERY_LABELS = {
    "pickup": "Самовывоз — Агатовая, 28",
    "delivery": "Доставка по Перми",
}

PAYMENT_LABELS = {
    "cash": "Наличные при получении",
    "card": "Карта при получении",
    "transfer": "Перевод",
}

LEAD_SERVICE_LABELS = {
    "ukladka-laminata": "Укладка ламината",
    "ukladka-spc": "Укладка SPC",
    "ukladka-kvartsvinila-lvt": "Укладка кварцвинила и LVT",
    "ukladka-linoleuma": "Укладка линолеума",
    "ukladka-kovrolina": "Укладка ковролина",
    "demontazh-pokrytiya": "Демонтаж старого покрытия",
    "podgotovka-osnovaniya": "Подготовка основания",
    "montazh-plintusa": "Монтаж плинтуса",
    "podbor-pokrytiya": "Подбор покрытия и замер",
}

LEAD_SOURCE_LABELS = {
    "consultation": "Форма консультации",
    "contacts": "Контакты",
    "services": "Услуги",
    "delivery": "Доставка",
    "warranty": "Гарантия",
    "payment": "Оплата",
    "promo": "Акция",
    "test": "Тест",
}


def label_or_raw(mapping: dict[str, str], value: str | None, fallback: str = "—") -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    return mapping.get(text, text)


def delivery_label(value: str | None) -> str:
    return label_or_raw(DELIVERY_LABELS, value)


def payment_label(value: str | None) -> str:
    return label_or_raw(PAYMENT_LABELS, value)


def lead_service_label(value: str | None) -> str:
    return label_or_raw(LEAD_SERVICE_LABELS, value)


def lead_source_label(value: str | None) -> str:
    return label_or_raw(LEAD_SOURCE_LABELS, value)
