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
    Lead,
    News,
    Order,
    OrderItem,
    Partner,
    Product,
    ProductAttribute,
    ProductCategory,
    ProductImage,
    ProductRedirect,
    Review,
    ReviewPhoto,
    Service,
    ServiceFaq,
    SitePage,
    SiteSetting,
)
from app.services.product_descriptions import build_product_description_html, looks_like_spec_dump
from app.services.reviews_import import load_reviews_source, parse_reviews_html, replace_reviews_from_html
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

    @app.cli.command("reimport-reviews")
    def reimport_reviews():
        """Replace DB reviews with cards from the homepage reviews section."""
        counts = replace_reviews_from_html()
        print(
            "Reviews reimported: "
            f"total={counts['total']} avito={counts['avito']} "
            f"yandex={counts['yandex']} vk={counts['vk']}"
        )

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

    @app.cli.command("seed-test-orders-leads")
    def seed_test_orders_leads():
        """Create 10 test cart orders and 10 test lead form submissions."""
        orders_count, leads_count = _seed_test_orders_and_leads()
        print(f"Created test orders: {orders_count}, test leads: {leads_count}")

    @app.cli.command("sync-service-pages")
    def sync_service_pages():
        """Import /uslugi/ content from service_pages.py into the services table."""
        count = _sync_service_pages_from_static()
        db.session.commit()
        print(f"Synced service pages: {count}")


def _seed_settings():
    defaults = {
        "seo.title": "Ламинейшен — подбор и укладка напольных покрытий в Перми",
        "seo.description": "Подбираем ламинат, SPC, кварцвинил и линолеум под помещение, привозим образцы, рассчитываем материал и выполняем укладку в Перми.",
        "header.phone": "+7 (909) 112-52-05",
        "header.address": "Агатовая улица, 28, Пермь",
        "header.hours": "7 дней в неделю: 09:00–20:00",
        "header.org": "Ламинейшен — подбор и укладка напольных покрытий",
        "hero.h1": "Пол, который начинается с правильного решения",
        "hero.text": (
            "Подбираем покрытие под помещение, привозим образцы, рассчитываем "
            "материал и при необходимости берём на себя подготовку основания и укладку."
        ),
        "hero.cta_primary": "Подобрать покрытие",
        "hero.cta_secondary": "Посмотреть каталог",
        "hero.video": "video/hero.mp4",
        "hero.poster": "video/hero-poster.webp",
        "about.label": "О компании",
        "about.title": "Напольные покрытия с подбором, доставкой и укладкой",
        "about.text": (
            "«Ламинейшен» помогает закрыть весь вопрос с полом в одном месте: "
            "подобрать покрытие, рассчитать нужное количество материала, "
            "привезти его на объект и выполнить укладку.\n\n"
            "Мастер может приехать к вам с образцами ламината, SPC, кварцвинила, "
            "линолеума и других покрытий, чтобы выбрать подходящий вариант прямо "
            "в интерьере. На месте проводится замер, рассчитываются материалы "
            "и стоимость работ. При необходимости выполняем демонтаж старого "
            "покрытия и подготовку основания."
        ),
        "contacts.email": "vip.shapen@mail.ru",
        "footer.ogrn": "ОГРН 1255900000000",
        "checkout.delivery": "Самовывоз из шоурума на Агатовой, 28. Доставка по Перми — согласуем при звонке.",
        "checkout.payment": "Наличные, карта при получении или перевод. Онлайн-оплату подключим при необходимости.",
    }
    for key, value in defaults.items():
        if SiteSetting.query.filter_by(key=key).first() is None:
            db.session.add(SiteSetting(key=key, value=value))


def _seed_pages():
    pages = [
        (
            "akciya",
            "Акция",
            "Скидка 10% на материал",
            "При заказе укладки под ключ — скидка на покрытие. Подробности по телефону или в шоуруме.",
            "Скидка действует при заказе укладки под ключ\nМатериал подбираем под помещение и бюджет\nТочные условия уточним на замере или в шоуруме",
        ),
        (
            "garantiya",
            "Гарантия",
            "Гарантия на работы и покрытие",
            "Даём гарантию на укладку и помогаем с гарантийными обязательствами производителя покрытия.",
            "На выполненные работы по укладке — отдельная гарантия исполнителя\nНа материал действует гарантия производителя по паспорту покрытия\nПомогаем разобраться, если вопрос по качеству или монтажу",
        ),
        (
            "oplata",
            "Оплата",
            "Оплата",
            "Наличные, карта при получении и перевод. Счёт для юридических лиц — по запросу.",
            "Наличные и карта при получении материала или после работ\nПеревод на карту / расчётный счёт\nДля юридических лиц подготовим счёт и закрывающие документы",
        ),
        (
            "dostavka",
            "Доставка",
            "Доставка",
            "Самовывоз с Агатовой, 28. Доставка по Перми и краю — рассчитаем при оформлении.",
            "Самовывоз со склада / шоурума на Агатовой, 28\nДоставка по Перми и Пермскому краю\nСтоимость и сроки согласуем при оформлении заказа",
        ),
    ]
    for slug, title, h1, summary, points in pages:
        page = SitePage.query.filter_by(slug=slug).first()
        if page is None:
            page = SitePage(
                slug=slug,
                title=title,
                h1=h1,
                summary=summary,
                points=points,
                body_md=summary,
                seo_title=title,
                seo_description=summary,
            )
            db.session.add(page)
            continue
        if not page.h1:
            page.h1 = h1
        if not page.points:
            page.points = points


def _seed_services():
    _sync_service_pages_from_static()


def _sync_service_pages_from_static() -> int:
    from app.services.service_pages import SERVICE_PAGES

    known_slugs = {page.slug for page in SERVICE_PAGES}
    title_aliases = {
        "Кварцвинил / LVT": "ukladka-kvartsvinila-i-lvt",
        "Линолеум": "ukladka-linoleuma",
        "Ковролин": "ukladka-kovrolina",
        "Демонтаж": "demontazh-starogo-pokrytiya",
        "Плинтус": "montazh-plintusa",
        "Подготовка основания": "podgotovka-osnovaniya",
        "Укладка ламината": "ukladka-laminata",
        "Укладка SPC": "ukladka-spc",
    }

    count = 0
    for index, page in enumerate(SERVICE_PAGES, start=1):
        service = Service.query.filter_by(slug=page.slug).first()
        if service is None:
            service = Service.query.filter_by(title=page.title).first()
        if service is None:
            alias_slug = title_aliases.get(page.title)
            if alias_slug:
                service = Service.query.filter_by(slug=alias_slug).first()
            if service is None:
                for old_title, slug in title_aliases.items():
                    if slug == page.slug:
                        service = Service.query.filter_by(title=old_title).first()
                        if service is not None:
                            break
        if service is None:
            service = Service(is_published=True)
            db.session.add(service)

        service.slug = page.slug
        service.title = page.title
        service.heading = page.heading
        service.intro = page.intro
        service.body_md = "\n\n".join(page.body)
        service.text = page.intro
        service.price = page.price
        service.image = page.image
        service.hero_image = page.hero_image
        service.icon = page.icon
        service.seo_title = page.seo_title
        service.seo_description = page.seo_description
        service.sort_order = index
        service.is_published = True

        service.faqs.clear()
        db.session.flush()
        for faq_index, faq in enumerate(page.faqs):
            service.faqs.append(
                ServiceFaq(
                    question=faq.question,
                    answer=faq.answer,
                    sort_order=faq_index,
                )
            )
        count += 1

    # Remove leftover price-table stubs without a public URL.
    for orphan in Service.query.filter((Service.slug.is_(None)) | (Service.slug == "")).all():
        db.session.delete(orphan)

    # Remove duplicates that are not in the canonical service pages set.
    for extra in Service.query.filter(Service.slug.isnot(None), Service.slug != "").all():
        if extra.slug not in known_slugs:
            db.session.delete(extra)

    return count


def _seed_partners():
    if Partner.query.first():
        return
    items = [
        ("Tarkett", "https://www.tarkett.ru/"),
        ("Ideal", "https://laminat-ideal.com/"),
        ("Kastamonu", "https://kastamonusteps.ru/"),
        ("Egger", "https://www.egger.com/ru"),
        ("Swiss Krono", "https://www.swisskrono.com/ru-ru/"),
        ("La Moena", "https://www.lamoena.com/"),
        ("Aberhof", "https://bigfloor.pro/brands/aberhof/"),
        ("Solid", "https://www.solidfloor.com/"),
    ]
    for index, (name, url) in enumerate(items, start=1):
        slug = name.lower().replace(" ", "-")
        db.session.add(
            Partner(
                name=name,
                url=url,
                image=f"images/partners/{slug}.webp",
                sort_order=index,
            )
        )


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
    source = load_reviews_source()
    if not source:
        return
    for data in parse_reviews_html(source):
        photos = data.pop("photos")
        review = Review(**data)
        db.session.add(review)
        db.session.flush()
        for order, filename in enumerate(photos):
            if not filename:
                continue
            db.session.add(ReviewPhoto(review_id=review.id, filename=filename, sort_order=order))


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


def _seed_test_orders_and_leads(orders_n: int = 10, leads_n: int = 10) -> tuple[int, int]:
    products = (
        Product.query.filter_by(is_published=True)
        .order_by(Product.id)
        .limit(24)
        .all()
    )
    if not products:
        raise RuntimeError("Нет опубликованных товаров для тестовых заказов")

    customers = [
        ("Анна", "+7 (912) 100-10-01", "anna.test@example.com"),
        ("Игорь", "+7 (912) 100-10-02", "igor.test@example.com"),
        ("Мария", "+7 (912) 100-10-03", "maria.test@example.com"),
        ("Сергей", "+7 (912) 100-10-04", "sergey.test@example.com"),
        ("Елена", "+7 (912) 100-10-05", "elena.test@example.com"),
        ("Дмитрий", "+7 (912) 100-10-06", "dmitry.test@example.com"),
        ("Ольга", "+7 (912) 100-10-07", "olga.test@example.com"),
        ("Павел", "+7 (912) 100-10-08", "pavel.test@example.com"),
        ("Наталья", "+7 (912) 100-10-09", "natalya.test@example.com"),
        ("Алексей", "+7 (912) 100-10-10", "alexey.test@example.com"),
    ]
    delivery_options = [
        ("pickup", ""),
        ("delivery", "Пермь, ул. Ленина, 45, кв. 12"),
        ("delivery", "Пермь, ул. Мира, 10"),
        ("pickup", ""),
        ("delivery", "Пермь, ул. Куйбышева, 88"),
    ]
    payment_options = ["cash", "card", "transfer"]

    created_orders = 0
    for index in range(orders_n):
        first_name, phone, email = customers[index % len(customers)]
        delivery_method, address = delivery_options[index % len(delivery_options)]
        payment_method = payment_options[index % len(payment_options)]
        line_products = [
            products[(index + offset) % len(products)]
            for offset in range(1 + (index % 3))
        ]
        quantities = [Decimal("12.5"), Decimal("18"), Decimal("1"), Decimal("24.3"), Decimal("8")]
        total = Decimal("0")
        order = Order(
            first_name=first_name,
            phone=phone,
            email=email,
            delivery_method=delivery_method,
            address=address,
            payment_method=payment_method,
            comment=f"Тестовый заказ #{index + 1}",
            status="new",
            total=0,
        )
        db.session.add(order)
        db.session.flush()
        for line_index, product in enumerate(line_products):
            quantity = quantities[(index + line_index) % len(quantities)]
            if product.unit != "m2":
                quantity = Decimal(str(1 + ((index + line_index) % 4)))
            price = Decimal(product.price or 0)
            total += quantity * price
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    name=product.name,
                    unit=product.unit or "m2",
                    quantity=quantity,
                    price=price,
                )
            )
        order.total = total
        created_orders += 1

    db.session.commit()

    service_options = [
        ("ukladka-laminata", "Нужна укладка ламината в комнате 18 м²"),
        ("ukladka-spc", "Интересует укладка SPC на кухне"),
        ("ukladka-kvartsvinila-lvt", "Кварцвинил в коридор, нужен замер"),
        ("ukladka-linoleuma", "Линолеум в офис около 40 м²"),
        ("ukladka-kovrolina", "Ковролин в детскую"),
        ("demontazh-pokrytiya", "Демонтаж старого ламината"),
        ("podgotovka-osnovaniya", "Нужно выровнять основание"),
        ("montazh-plintusa", "Монтаж плинтуса по периметру"),
        ("podbor-pokrytiya", "Подбор покрытия и выезд с образцами"),
        ("ukladka-laminata", "Укладка под ключ, 2 комнаты"),
    ]
    sources = [
        "consultation",
        "contacts",
        "services",
        "delivery",
        "warranty",
        "payment",
        "promo",
        "consultation",
        "contacts",
        "services",
    ]
    lead_names = [
        ("Ирина", "Соколова"),
        ("Артём", "Белов"),
        ("Виктория", "Кузнецова"),
        ("Никита", "Орлов"),
        ("Светлана", "Морозова"),
        ("Роман", "Васильев"),
        ("Дарья", "Новикова"),
        ("Кирилл", "Фёдоров"),
        ("Юлия", "Смирнова"),
        ("Максим", "Попов"),
    ]

    leads_before = Lead.query.count()
    csrf_was_enabled = current_app.config.get("WTF_CSRF_ENABLED", True)
    current_app.config["WTF_CSRF_ENABLED"] = False
    try:
        client = current_app.test_client()
        for index in range(leads_n):
            first_name, last_name = lead_names[index % len(lead_names)]
            product_slug, details = service_options[index % len(service_options)]
            response = client.post(
                "/zayavka/",
                data={
                    "name": first_name,
                    "lastname": last_name,
                    "phone": f"+7 (909) 200-2{index:02d}-{10 + index:02d}",
                    "email": f"lead.test{index + 1}@example.com",
                    "product": product_slug,
                    "details": details,
                    "source": sources[index % len(sources)],
                    "consent": "on",
                    "website": "",
                },
                follow_redirects=True,
            )
            if response.status_code >= 400:
                raise RuntimeError(f"Не удалось отправить тестовую заявку #{index + 1}")
    finally:
        current_app.config["WTF_CSRF_ENABLED"] = csrf_was_enabled

    created_leads = Lead.query.count() - leads_before
    return created_orders, created_leads
