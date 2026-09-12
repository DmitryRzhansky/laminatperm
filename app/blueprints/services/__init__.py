from flask import Blueprint, abort, render_template, url_for
from sqlalchemy.orm import joinedload

from app.models import Case, Service

services_bp = Blueprint("services", __name__)


def _home_cases():
    return (
        Case.query.filter_by(is_published=True, show_on_home=True)
        .order_by(Case.sort_order, Case.id)
        .all()
    )

def _published_services():
    return (
        Service.query.options(joinedload(Service.faqs))
        .filter(Service.is_published.is_(True), Service.slug.isnot(None))
        .filter(Service.slug != "")
        .order_by(Service.sort_order, Service.id)
        .all()
    )


def get_service(slug: str) -> Service | None:
    return (
        Service.query.options(joinedload(Service.faqs))
        .filter_by(slug=slug, is_published=True)
        .first()
    )


def related_services(slug: str, limit: int = 4) -> list[Service]:
    items = [item for item in _published_services() if item.slug != slug]
    return items[:limit]


@services_bp.route("/uslugi/")
def index():
    services = _published_services()
    return render_template(
        "public/pages/services_list.html",
        services=services,
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
        home_cases=_home_cases(),
        title=service.seo_title or service.display_heading or service.title,
        description=service.seo_description or service.intro or service.text,
        lead_source=f"service:{service.slug}",
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Услуги", "url": url_for("services.index")},
            {"label": service.title},
        ],
    )
