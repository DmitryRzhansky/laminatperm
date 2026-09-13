from __future__ import annotations

from datetime import datetime
from html import escape

from flask import Blueprint, Response, url_for

from app.models import Case, News, Product, ProductCategory, Service, SitePage
from app.services import seo_meta

seo_bp = Blueprint("seo", __name__)


def _xml_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.date().isoformat()


def _url_entry(location: str, *, lastmod: datetime | None = None, priority: str | None = None) -> str:
    parts = ["  <url>", f"    <loc>{escape(seo_meta.absolute_url(location))}</loc>"]
    formatted_lastmod = _xml_datetime(lastmod)
    if formatted_lastmod:
        parts.append(f"    <lastmod>{formatted_lastmod}</lastmod>")
    if priority:
        parts.append(f"    <priority>{priority}</priority>")
    parts.append("  </url>")
    return "\n".join(parts)


def _static_urls() -> list[tuple[str, str]]:
    return [
        (url_for("main.home"), "1.0"),
        (url_for("catalog.index"), "0.9"),
        (url_for("services.index"), "0.9"),
        (url_for("pages.prices"), "0.8"),
        (url_for("cases.index"), "0.7"),
        (url_for("pages.reviews"), "0.7"),
        (url_for("news.index"), "0.7"),
        (url_for("pages.partners"), "0.6"),
        (url_for("pages.promo"), "0.6"),
        (url_for("pages.warranty"), "0.6"),
        (url_for("pages.payment"), "0.6"),
        (url_for("pages.delivery"), "0.6"),
        (url_for("pages.faq"), "0.6"),
        (url_for("pages.contacts"), "0.6"),
        (url_for("pages.privacy"), "0.3"),
        (url_for("pages.personal_data_consent"), "0.3"),
    ]


@seo_bp.route("/robots.txt")
def robots_txt():
    body = "\n".join(
        [
            "User-agent: *",
            "Disallow: /catalog/cart/",
            "Disallow: /catalog/checkout/",
            "",
            f"Sitemap: {seo_meta.absolute_url(url_for('seo.sitemap_xml'))}",
            "",
        ]
    )
    return Response(body, mimetype="text/plain; charset=utf-8")


@seo_bp.route("/sitemap.xml")
def sitemap_xml():
    entries = [_url_entry(path, priority=priority) for path, priority in _static_urls()]

    pages = SitePage.query.filter(SitePage.slug.in_(["akciya", "garantiya", "oplata", "dostavka"])).all()
    page_paths = {
        "akciya": url_for("pages.promo"),
        "garantiya": url_for("pages.warranty"),
        "oplata": url_for("pages.payment"),
        "dostavka": url_for("pages.delivery"),
    }
    for page in pages:
        entries.append(_url_entry(page_paths[page.slug], lastmod=page.updated_at, priority="0.6"))

    for service in Service.query.filter(Service.is_published.is_(True), Service.slug.isnot(None), Service.slug != "").all():
        entries.append(_url_entry(url_for("services.detail", slug=service.slug), priority="0.8"))

    for category in ProductCategory.query.order_by(ProductCategory.sort_order, ProductCategory.id).all():
        entries.append(_url_entry(url_for("catalog.category", category_slug=category.slug), priority="0.8"))

    products = Product.query.filter_by(is_published=True).join(ProductCategory).order_by(Product.sort_order, Product.id).all()
    for product in products:
        entries.append(
            _url_entry(
                url_for("catalog.product", category_slug=product.category.slug, product_slug=product.slug),
                priority="0.7",
            )
        )

    for case in Case.query.filter_by(is_published=True).order_by(Case.sort_order, Case.id).all():
        entries.append(_url_entry(url_for("cases.detail", slug=case.slug), lastmod=case.created_at, priority="0.6"))

    for item in News.query.filter_by(is_published=True).order_by(News.published_at.desc()).all():
        entries.append(_url_entry(url_for("news.detail", slug=item.slug), lastmod=item.updated_at, priority="0.6"))

    body = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            *entries,
            "</urlset>",
            "",
        ]
    )
    return Response(body, mimetype="application/xml; charset=utf-8")
