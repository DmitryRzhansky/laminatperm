from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path
from urllib.request import urlopen

from flask import current_app

from app.extensions import db
from app.models import (
    Case,
    CaseImage,
    FaqItem,
    News,
    Partner,
    Product,
    ProductAttribute,
    ProductCategory,
    ProductImage,
    ProductRedirect,
    Review,
    Service,
    SitePage,
    SiteSetting,
    TeamMember,
)
from app.services.product_descriptions import build_product_description_html, looks_like_spec_dump
from app.utils.files import save_upload
from app.utils.seo import apply_seo
from app.utils.settings import set_setting
from app.utils.slugs import unique_slug

BASE_DIR = Path(__file__).resolve().parent.parent

CATEGORIES = [
    ("Ламинат", "laminat", "Классические ламинированные покрытия.", "images/catalog/laminate.webp"),
    ("Линолеум", "linoleum", "Рулонные покрытия для квартир, домов и коммерции.", "images/catalog/linoleum.webp"),
    ("SPC", "spc", "Жёсткие виниловые покрытия с замком.", "images/catalog/spc.webp"),
    ("Аксессуары", "aksessuary", "Подложки, плинтусы, клей и комплектующие.", "images/catalog/accessories.webp"),
    ("Клеевой LVT", "kleevoy-lvt", "Клеевые виниловые покрытия.", "images/catalog/lvt.webp"),
]

TILDA_PARTS = {
    "494809029682": "laminat",
    "905543550762": "linoleum",
    "936724865742": "spc",
    "450631540262": "aksessuary",
    "818023025703": "kleevoy-lvt",
}

MANUAL_CATEGORY = {
    "211218110822": "laminat",
    "398409938673": "linoleum",
}


def register_cli(app):
    @app.cli.command("seed")
    def seed():
        _seed_settings()
        _seed_pages()
        _seed_team()
        _seed_services()
        _seed_partners()
        _seed_faq()
        _seed_news()
        _seed_cases()
        _seed_reviews()
        _seed_categories()
        db.session.commit()
        print("Seed complete")

    @app.cli.command("import-catalog")
    def import_catalog():
        _seed_categories()
        _import_tilda_products()
        for product in Product.query.order_by(Product.id).all():
            if not looks_like_spec_dump(product.description_html):
                continue
            html = build_product_description_html(product)
            product.description_html = html
            plain = re.sub(r"<[^>]+>", " ", html)
            plain = re.sub(r"\s+", " ", plain).strip()
            apply_seo(product, product.name, plain)
        db.session.commit()
        print("Catalog imported")

    @app.cli.command("fill-product-descriptions")
    def fill_product_descriptions():
        """Write marketing descriptions over Tilda spec dumps."""
        updated = 0
        for product in Product.query.order_by(Product.id).all():
            if not looks_like_spec_dump(product.description_html):
                continue
            html = build_product_description_html(product)
            product.description_html = html
            plain = re.sub(r"<[^>]+>", " ", html)
            plain = re.sub(r"\s+", " ", plain).strip()
            apply_seo(product, product.name, plain)
            updated += 1
        db.session.commit()
        print(f"Updated descriptions: {updated}")


def _seed_settings():
    defaults = {
        "seo.title": "Ламинейшен — подбор и укладка напольных покрытий в Перми",
        "seo.description": "Подбираем ламинат, SPC, кварцвинил и линолеум под помещение, привозим образцы, рассчитываем материал и выполняем укладку в Перми.",
        "header.phone": "+7 (909) 112-52-05",
        "header.address": "Агатовая улица, 28, Пермь",
        "header.hours": "7 дней в неделю: 09:00–20:00",
        "header.org": "Ламинейшен — подбор и укладка напольных покрытий",
        "hero.h1": "Пол, который начинается с правильного выбора",
        "contacts.email": "vip.shapen@mail.ru",
        "footer.ogrn": "ОГРН 1255900000000",
        "checkout.delivery": "Самовывоз из шоурума на Агатовой, 28. Доставка по Перми — согласуем при звонке.",
        "checkout.payment": "Наличные, карта при получении или перевод. Онлайн-оплату подключим при необходимости.",
        "documents.intro": "Сертификаты, гарантийные документы и материалы брендов. Добавляйте файлы в админке.",
    }
    for key, value in defaults.items():
        if SiteSetting.query.filter_by(key=key).first() is None:
            db.session.add(SiteSetting(key=key, value=value))


def _seed_pages():
    pages = [
        ("akciya", "Акция", "Скидка 10% на материал при заказе укладки под ключ. Подробности — по телефону или в шоуруме."),
        ("garantiya", "Гарантия", "Даём гарантию на укладку и помогаем с гарантийными обязательствами производителя покрытия."),
        ("oplata", "Оплата", "Наличные, карта при получении и перевод. Счёт для юридических лиц — по запросу."),
        ("dostavka", "Доставка", "Самовывоз с Агатовой, 28. Доставка по Перми и краю — рассчитаем при оформлении."),
    ]
    for slug, title, body in pages:
        if SitePage.query.filter_by(slug=slug).first():
            continue
        page = SitePage(slug=slug, title=title, summary=body, body_md=body, seo_title=title, seo_description=body)
        db.session.add(page)


def _seed_team():
    if TeamMember.query.first():
        return
    db.session.add(
        TeamMember(
            name="Сергей Аверьянов",
            role="Основатель и эксперт по напольным покрытиям",
            text="Подбирает покрытие под помещение, считает материал и контролирует укладку.",
            photo="images/advantages/averyanov.webp",
            sort_order=1,
        )
    )


def _seed_services():
    items = [
        (
            "Укладка ламината",
            "400 ₽/м²",
            "Замковая укладка ламината с подрезкой и оформлением примыканий.",
            "images/services/laminate.webp",
        ),
        (
            "Укладка SPC",
            "300 ₽/м²",
            "Жёсткий винил с замком для жилых и коммерческих помещений.",
            "images/services/spc.webp",
        ),
        (
            "Кварцвинил / LVT",
            "400 ₽/м²",
            "Замковые и клеевые покрытия.",
            "images/services/lvt.webp",
        ),
        (
            "Линолеум",
            "300 ₽/м²",
            "Раскрой и укладка рулонных покрытий.",
            "images/services/linoleum.webp",
        ),
        (
            "Ковролин",
            "300 ₽/м²",
            "Укладка ковролина в квартирах и офисах.",
            "images/services/carpet.webp",
        ),
        (
            "Демонтаж",
            "по расчёту",
            "Снятие старого покрытия и вывоз мусора.",
            "images/services/demolition.webp",
        ),
        (
            "Подготовка основания",
            "по расчёту",
            "Стяжка, выравнивание, подготовка под тёплый пол.",
            "images/services/subfloor.webp",
        ),
        (
            "Плинтус",
            "по расчёту",
            "Монтаж плинтуса, порогов и примыканий.",
            "images/services/skirting.webp",
        ),
    ]
    if Service.query.first():
        by_title = {item.title: item for item in Service.query.all()}
        for index, (title, price, text, image) in enumerate(items, start=1):
            service = by_title.get(title)
            if service is None:
                continue
            if not service.image:
                service.image = image
            service.sort_order = service.sort_order or index
        return

    for index, (title, price, text, image) in enumerate(items, start=1):
        db.session.add(
            Service(
                title=title,
                price=price,
                text=text,
                image=image,
                sort_order=index,
            )
        )


def _seed_partners():
    if Partner.query.first():
        return
    names = ["Tarkett", "Ideal", "Kastamonu", "Egger", "Swiss Krono", "La Moena", "Aberhof", "Solid"]
    for index, name in enumerate(names, start=1):
        slug = name.lower().replace(" ", "-")
        db.session.add(Partner(name=name, text=f"Официальные коллекции {name}.", image=f"images/partners/{slug}.webp", sort_order=index))


def _seed_faq():
    if FaqItem.query.first():
        return
    items = [
        ("Нужно ли выравнивать пол перед укладкой?", "Да. Без ровного основания покрытие будет скрипеть и расходиться на стыках."),
        ("Делаете ли вы замер и расчёт материала?", "Да, выезд мастера бесплатный. Считаем покрытие, подложку и запас."),
        ("Можно ли уложить ламинат на тёплый пол?", "Можно, если покрытие допускает это по паспорту и основание подготовлено."),
        ("Сколько сохнет стяжка?", "Зависит от слоя и состава. Точные сроки скажем после осмотра объекта."),
        ("Привозите ли образцы?", "Да, привезём образцы подходящих коллекций к вам домой или в офис."),
    ]
    for index, (question, answer) in enumerate(items, start=1):
        db.session.add(FaqItem(question=question, answer=answer, sort_order=index))


def _seed_news():
    if News.query.first():
        return
    items = [
        ("Как выбрать ламинат для квартиры", "laminate-selection.webp", "Разбираем класс нагрузки, толщину, замки и защиту от влаги."),
        ("Нужна ли стяжка перед укладкой", "screed-need.webp", "Когда можно класть сразу и когда основание нужно готовить."),
        ("Винил vs ламинат", "vinyl-vs-laminate.webp", "Сравниваем комфорт, влагу и цену."),
        ("Плавающая укладка", "floating-install.webp", "Как работает замок и зачем нужен зазор у стен."),
        ("Какой плинтус выбрать", "skirting-selection.webp", "Дюрополимер, МДФ и теневой профиль."),
        ("Ламинат на тёплый пол", "underfloor-heating.webp", "Какие покрытия совместимы с водяным и электрическим тёплым полом."),
        ("Стоимость укладки под ключ в Перми", "installation-cost.webp", "Из чего складывается смета: материал, подготовка и работа."),
    ]
    for title, image, summary in items:
        news = News(title=title, summary=summary, body_md=summary, image=f"images/blog/{image}", is_published=True)
        news.slug = unique_slug(News, title)
        apply_seo(news, title, summary, News)
        db.session.add(news)
        db.session.flush()


def _seed_cases():
    if Case.query.first():
        return
    items = [
        {
            "title": "Полный цикл: от старого пола до Ideal Form",
            "location": "Пермь · Стахановская, 44",
            "lead": "Сняли старое покрытие, подготовили основание полусухой стяжкой и уложили ламинат Ideal Form.",
            "tags": "Под ключ, Демонтаж, Стяжка, Ламинат",
            "material": "Ламинат Ideal Form ID78",
            "task": "Демонтаж, выравнивание и новая укладка",
            "result": "Ровное основание и готовый пол",
            "works": "Полный демонтаж старого покрытия и вывоз мусора\nПолусухая стяжка с контролем уровня\nПоставка и укладка Ideal Form",
            "images": ["images/cases/stakhanovskaya.webp", "images/cases/screed.webp", "images/cases/ideal-form-aqua.webp"],
        },
        {
            "title": "Art Floor в жилой комнате",
            "location": "Пермь",
            "lead": "Аккуратная укладка винилового покрытия с подрезкой и плинтусом.",
            "tags": "LVT, Укладка",
            "material": "Art Floor",
            "task": "Замена покрытия без капитального ремонта",
            "result": "Готовый пол за один заход",
            "works": "Подготовка основания\nУкладка покрытия\nМонтаж плинтуса",
            "images": ["images/cases/art-floor.webp"],
        },
    ]
    for index, data in enumerate(items, start=1):
        case = Case(
            title=data["title"],
            location=data["location"],
            lead=data["lead"],
            tags=data["tags"],
            fact_material=data["material"],
            fact_task=data["task"],
            fact_result=data["result"],
            works=data["works"],
            show_on_home=True,
            sort_order=index,
        )
        case.slug = unique_slug(Case, data["title"])
        apply_seo(case, data["title"], data["lead"], Case)
        db.session.add(case)
        db.session.flush()
        for order, filename in enumerate(data["images"]):
            db.session.add(CaseImage(case_id=case.id, filename=filename, sort_order=order))


def _seed_reviews():
    if Review.query.first():
        return
    html_path = BASE_DIR / "index.html"
    if not html_path.exists():
        return
    html = html_path.read_text(encoding="utf-8")
    cards = re.findall(
        r'<article class="reviews__card"(.*?)</article>',
        html,
        flags=re.DOTALL,
    )
    for index, card in enumerate(cards, start=1):
        match_platform = re.search(r'data-reviews-slide="(\w+)"', card)
        platform = match_platform.group(1) if match_platform else "avito"
        avatar_match = re.search(r'src="([^"]+)"', card)
        author_match = re.search(r'reviews__name">([^<]+)', card)
        role_match = re.search(r'reviews__meta">([^<]+)', card)
        date_match = re.search(r'reviews__date">([^<]+)', card)
        item_match = re.search(r'reviews__item">([^<]+)', card)
        text_match = re.search(r'reviews__text">\s*(.*?)\s*</p>', card, flags=re.DOTALL)
        avatar = (avatar_match.group(1) if avatar_match else "").replace("assets/", "")
        db.session.add(
            Review(
                platform=platform,
                author=(author_match.group(1).strip() if author_match else "Клиент"),
                role=(role_match.group(1).strip() if role_match else ""),
                date_text=(date_match.group(1).strip() if date_match else ""),
                item=(item_match.group(1).strip() if item_match else ""),
                text=re.sub(r"\s+", " ", text_match.group(1)).strip() if text_match else "",
                avatar=avatar,
                sort_order=index,
            )
        )


def _seed_categories():
    for index, (name, slug, intro, cover) in enumerate(CATEGORIES, start=1):
        if ProductCategory.query.filter_by(slug=slug).first():
            continue
        db.session.add(ProductCategory(name=name, slug=slug, intro=intro, cover=cover, sort_order=index, seo_title=name, seo_description=intro))
    db.session.flush()


def _import_tilda_products():
    products = []
    for slice_no in (1, 2):
        url = f"https://store.tildaapi.com/api/getproductslist/?storepartuid=396077792202&slice={slice_no}"
        with urlopen(url, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        products.extend(payload.get("products", []))

    categories = {item.slug: item for item in ProductCategory.query.all()}
    upload_dir = current_app.config["UPLOAD_FOLDER"] / "catalog"
    upload_dir.mkdir(parents=True, exist_ok=True)

    for raw in products:
        uid = str(raw.get("uid"))
        if Product.query.filter_by(tilda_uid=uid).first():
            continue
        partuids = re.findall(r"\d+", raw.get("partuids") or "")
        slug_cat = None
        for part in partuids:
            slug_cat = TILDA_PARTS.get(part)
            if slug_cat:
                break
        slug_cat = slug_cat or MANUAL_CATEGORY.get(uid) or "aksessuary"
        category = categories[slug_cat]
        title = raw.get("title") or "Товар"
        product = Product(
            name=title,
            slug=unique_slug(Product, title),
            category_id=category.id,
            brand=_brand_from_title(title),
            price=Decimal(str(raw.get("price") or "0")),
            unit="m2" if (raw.get("unit") or "").upper() == "MTK" or "подлож" not in title.lower() and "плинт" not in title.lower() and "клей" not in title.lower() else "pcs",
            description_html=raw.get("descr") or "",
            tilda_uid=uid,
            sort_order=int(raw.get("sort") or 0),
            is_published=True,
        )
        if "подлож" in title.lower() or "плинт" in title.lower() or "клей" in title.lower():
            product.unit = "pcs"
        apply_seo(product, title, re.sub("<[^<]+?>", " ", raw.get("descr") or ""))
        db.session.add(product)
        db.session.flush()
        db.session.add(ProductRedirect(tilda_uid=uid, product_id=product.id))
        _attrs_from_descr(product, raw.get("descr") or "")
        gallery = raw.get("gallery") or "[]"
        try:
            photos = json.loads(gallery) if isinstance(gallery, str) else gallery
        except json.JSONDecodeError:
            photos = []
        for order, photo in enumerate(photos):
            src = photo.get("img") if isinstance(photo, dict) else None
            if not src:
                continue
            local = _download_image(src, upload_dir)
            if local:
                db.session.add(ProductImage(product_id=product.id, filename=local, sort_order=order))


def _brand_from_title(title: str) -> str:
    first = title.split()[0]
    mapping = {
        "ABERHOF": "Aberhof",
        "ELEGANTE": "Elegante",
        "IDEAL": "Ideal",
        "IIDEAL": "Ideal",
        "NOVENTIS": "Noventis",
        "TARKETT": "Tarkett",
        "SWISS": "Swiss Krono",
        "ЛИНОЛЕУМ": "Tarkett",
    }
    return mapping.get(first.upper(), first.title())


def _attrs_from_descr(product: Product, descr: str) -> None:
    text = descr.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    text = re.sub(r"<[^>]+>", "\n", text)
    order = 0
    for line in text.split("\n"):
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        name, value = name.strip(), value.strip()
        if not name or not value:
            continue
        db.session.add(ProductAttribute(product_id=product.id, name=name, value=value, sort_order=order))
        order += 1


def _download_image(url: str, folder: Path) -> str | None:
    try:
        with urlopen(url, timeout=30) as response:
            data = response.read()
        name = Path(url.split("?")[0]).name or "image.webp"
        target = folder / name
        counter = 2
        while target.exists():
            target = folder / f"{target.stem}-{counter}{target.suffix}"
            counter += 1
        target.write_bytes(data)
        return f"uploads/catalog/{target.name}"
    except Exception as error:
        print("image download failed", url, error)
        return None
