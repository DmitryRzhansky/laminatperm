SERVICE_THUMBNAILS = {
    "Укладка ламината": "images/services/laminate.webp",
    "Укладка SPC": "images/services/spc.webp",
    "Кварцвинил / LVT": "images/services/lvt.webp",
    "Линолеум": "images/services/linoleum.webp",
    "Ковролин": "images/services/carpet.webp",
    "Демонтаж": "images/services/demolition.webp",
    "Подготовка основания": "images/services/subfloor.webp",
    "Плинтус": "images/services/skirting.webp",
}


def resolve_service_image(service) -> str:
    image = (getattr(service, "image", None) or "").strip()
    if image:
        return image
    return SERVICE_THUMBNAILS.get(getattr(service, "title", ""), "")
