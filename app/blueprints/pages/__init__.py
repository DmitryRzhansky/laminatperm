from flask import Blueprint, render_template, url_for

from app.models import (
    FaqItem,
    Partner,
    Review,
    Service,
    SitePage,
)
from app.services import seo_meta
from app.services.service_media import resolve_service_image
from app.utils.markdown import render_markdown
from app.utils.settings import get_setting

pages_bp = Blueprint("pages", __name__)


def _crumbs(*labels):
    crumbs = [{"label": "Главная", "url": url_for("main.home")}]
    for index, label in enumerate(labels):
        if index == len(labels) - 1:
            crumbs.append({"label": label})
        else:
            crumbs.append(label)
    return crumbs


def _page(slug, template="public/pages/text.html", *, page_type="WebPage"):
    item = SitePage.query.filter_by(slug=slug).first_or_404()
    route_map = {
        "akciya": "pages.promo",
        "garantiya": "pages.warranty",
        "oplata": "pages.payment",
        "dostavka": "pages.delivery",
    }
    endpoint = route_map.get(slug)
    path = url_for(endpoint) if endpoint else f"/{slug}/"
    title = (item.seo_title or item.title).strip()
    description = (item.seo_description or item.summary or item.title).strip()
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name=title,
            description=description,
            path=path,
            page_type=page_type,
        )
    )
    return render_template(
        template,
        page=item,
        body=render_markdown(item.body_md),
        breadcrumbs=_crumbs(item.title),
        json_ld=json_ld,
    )


@pages_bp.route("/otzyvy/")
def reviews():
    from sqlalchemy.orm import joinedload

    items = (
        Review.query.options(joinedload(Review.photos))
        .filter_by(is_published=True)
        .order_by(Review.sort_order, Review.id)
        .all()
    )
    groups = {"avito": [], "yandex": [], "vk": []}
    for item in items:
        key = item.platform if item.platform in groups else "avito"
        groups[key].append(item)
    path = url_for("pages.reviews")
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name="Отзывы",
            description="Отзывы клиентов Ламинейшен о подборе и укладке напольных покрытий в Перми.",
            path=path,
        )
    )
    return render_template(
        "public/pages/reviews.html",
        items=items,
        groups=groups,
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Отзывы"},
        ],
        json_ld=json_ld,
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
            "slug": item.slug,
        }
        for item in items
    ]
    path = url_for("pages.prices")
    list_items = []
    for item in items:
        entry = {
            "name": item.title,
            "item": {
                "@type": "Service",
                "name": item.title,
                "description": (item.text or item.intro or item.title).strip(),
                "provider": {"@type": "Organization", "name": seo_meta.SITE_NAME},
            },
        }
        if item.slug:
            entry["url"] = url_for("services.detail", slug=item.slug)
            entry["item"]["url"] = seo_meta.absolute_url(entry["url"])
        price = seo_meta.offer_price(item.price)
        if price:
            entry["item"]["offers"] = {
                "@type": "Offer",
                "price": price,
                "priceCurrency": "RUB",
            }
        elif (item.price or "").strip():
            entry["item"]["offers"] = {
                "@type": "Offer",
                "description": item.price.strip(),
                "priceCurrency": "RUB",
            }
        list_items.append(entry)

    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name="Цены на укладку и подготовку пола",
            description="Ориентиры по укладке напольных покрытий в Перми. Точную смету считаем после замера.",
            path=path,
        ),
        seo_meta.item_list_ld(
            name="Прайс на укладку и подготовку пола",
            path=path,
            description="Цены на услуги Ламинейшен по укладке и подготовке пола.",
            items=list_items,
        ),
    )
    return render_template("public/pages/prices.html", items=rows, json_ld=json_ld)


@pages_bp.route("/partnery/")
def partners():
    items = Partner.query.filter_by(is_published=True).order_by(Partner.sort_order, Partner.id).all()
    path = url_for("pages.partners")
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name="Партнёры",
            description="Бренды и партнёры, с которыми работает Ламинейшен.",
            path=path,
        ),
        seo_meta.item_list_ld(
            name="Партнёры Ламинейшен",
            path=path,
            items=[{"name": item.name, "url": item.url or path} for item in items],
        ),
    )
    return render_template("public/pages/partners.html", items=items, json_ld=json_ld)


@pages_bp.route("/akciya/")
def promo():
    return _page("akciya", template="public/pages/promo.html")


@pages_bp.route("/garantiya/")
def warranty():
    return _page("garantiya", template="public/pages/warranty.html")


@pages_bp.route("/oplata/")
def payment():
    return _page("oplata", template="public/pages/payment.html")


@pages_bp.route("/dostavka/")
def delivery():
    return _page("dostavka", template="public/pages/delivery.html")


@pages_bp.route("/voprosy/")
def faq():
    items = FaqItem.query.filter_by(is_published=True).order_by(FaqItem.sort_order, FaqItem.id).all()
    path = url_for("pages.faq")
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name="Ответы на вопросы",
            description="Коротко про замер, укладку, сроки и стоимость напольных покрытий в Перми.",
            path=path,
        ),
        seo_meta.faq_ld(items, path=path),
    )
    return render_template("public/pages/faq.html", items=items, json_ld=json_ld)


@pages_bp.route("/kontakty/")
def contacts():
    path = url_for("pages.contacts")
    org = seo_meta.organization_ld()
    org["@type"] = ["HomeGoodsStore", "LocalBusiness"]
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name="Контакты",
            description=(
                f"Контакты Ламинейшен в Перми: {get_setting('header.address', 'Агатовая улица, 28, Пермь')}, "
                f"{get_setting('header.phone', '+7 (909) 112-52-05')}."
            ),
            path=path,
            page_type="ContactPage",
        ),
        org,
    )
    return render_template("public/pages/contacts.html", json_ld=json_ld)


@pages_bp.route("/privacy/")
def privacy():
    title = "Политика конфиденциальности"
    description = "Как Ламинейшен собирает, использует и защищает данные посетителей сайта."
    path = url_for("pages.privacy")
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name=title,
            description=description,
            path=path,
            page_type="PrivacyPolicy",
        )
    )
    return render_template(
        "public/pages/privacy.html",
        title=title,
        description=description,
        breadcrumbs=_crumbs(title),
        json_ld=json_ld,
    )


@pages_bp.route("/personal-data-consent/")
def personal_data_consent():
    title = "Согласие на обработку персональных данных"
    description = "Условия согласия на обработку персональных данных для заявок и заказов на сайте Ламинейшен."
    path = url_for("pages.personal_data_consent")
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name=title,
            description=description,
            path=path,
            page_type="WebPage",
        )
    )
    return render_template(
        "public/pages/personal_data_consent.html",
        title=title,
        description=description,
        breadcrumbs=_crumbs(title),
        json_ld=json_ld,
    )
