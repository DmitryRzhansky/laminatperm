from flask import Blueprint, abort, render_template, url_for

from app.services.service_pages import SERVICE_PAGES, get_service, related_services

services_bp = Blueprint("services", __name__)


@services_bp.route("/uslugi/")
def index():
    return render_template(
        "public/pages/services_list.html",
        services=SERVICE_PAGES,
        title="Услуги по укладке и подготовке пола",
        description=(
            "Укладка ламината, SPC, кварцвинила и LVT, линолеума и ковролина в Перми. "
            "Демонтаж, подготовка основания и монтаж плинтуса."
        ),
        intro=(
            "Можно заказать отдельную услугу или весь цикл — от демонтажа "
            "и подготовки основания до укладки покрытия и плинтуса."
        ),
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Услуги"},
        ],
    )


@services_bp.route("/uslugi/<slug>/")
def detail(slug):
    service = get_service(slug)
    if service is None:
        abort(404)

    return render_template(
        "public/pages/service_detail.html",
        service=service,
        related=related_services(slug),
        title=service.seo_title,
        description=service.seo_description,
        lead_source=f"service:{service.slug}",
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Услуги", "url": url_for("services.index")},
            {"label": service.title},
        ],
    )
