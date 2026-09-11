from flask import Blueprint, render_template, url_for

from app.models import (
    Document,
    FaqItem,
    Partner,
    Review,
    Service,
    SitePage,
    TeamMember,
)
from app.utils.markdown import render_markdown
from app.utils.settings import get_setting
from app.services.service_media import resolve_service_image

pages_bp = Blueprint("pages", __name__)


def _crumbs(*labels):
    crumbs = [{"label": "Главная", "url": url_for("main.home")}]
    for index, label in enumerate(labels):
        if index == len(labels) - 1:
            crumbs.append({"label": label})
        else:
            crumbs.append(label)
    return crumbs


def _page(slug, template="public/pages/text.html"):
    item = SitePage.query.filter_by(slug=slug).first_or_404()
    return render_template(
        template,
        page=item,
        body=render_markdown(item.body_md),
        breadcrumbs=_crumbs(item.title),
    )


@pages_bp.route("/otzyvy/")
def reviews():
    items = Review.query.filter_by(is_published=True).order_by(Review.sort_order, Review.id).all()
    groups = {"avito": [], "yandex": [], "vk": []}
    for item in items:
        groups.setdefault(item.platform or "avito", []).append(item)
    return render_template(
        "public/pages/reviews.html",
        items=items,
        groups=groups,
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Отзывы"},
        ],
    )


@pages_bp.route("/ceny/")
def prices():
    items = Service.query.filter_by(is_published=True).order_by(Service.sort_order, Service.id).all()
    rows = [
        {
            "title": item.title,
            "text": item.text,
            "price": item.price,
            "image": resolve_service_image(item),
        }
        for item in items
    ]
    return render_template("public/pages/prices.html", items=rows)


@pages_bp.route("/komanda/")
def team():
    items = TeamMember.query.filter_by(is_published=True).order_by(TeamMember.sort_order, TeamMember.id).all()
    return render_template("public/pages/team.html", items=items)


@pages_bp.route("/dokumenty/")
def documents():
    items = Document.query.order_by(Document.sort_order, Document.id).all()
    intro = get_setting("documents.intro", "Сертификаты, гарантийные документы и материалы брендов.")
    return render_template("public/pages/documents.html", items=items, intro=intro)


@pages_bp.route("/partnery/")
def partners():
    items = Partner.query.filter_by(is_published=True).order_by(Partner.sort_order, Partner.id).all()
    return render_template("public/pages/partners.html", items=items)


@pages_bp.route("/akciya/")
def promo():
    return _page("akciya")


@pages_bp.route("/garantiya/")
def warranty():
    return _page("garantiya")


@pages_bp.route("/oplata/")
def payment():
    return _page("oplata")


@pages_bp.route("/dostavka/")
def delivery():
    return _page("dostavka")


@pages_bp.route("/voprosy/")
def faq():
    items = FaqItem.query.filter_by(is_published=True).order_by(FaqItem.sort_order, FaqItem.id).all()
    return render_template("public/pages/faq.html", items=items)


@pages_bp.route("/kontakty/")
def contacts():
    return render_template("public/pages/contacts.html")
