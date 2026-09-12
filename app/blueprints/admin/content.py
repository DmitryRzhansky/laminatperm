from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.blueprints.admin import admin_bp, _save_image
from app.extensions import db
from app.models import (
    Advantage,
    Case,
    CaseImage,
    FaqItem,
    News,
    Partner,
    ProcessVideo,
    Product,
    ProductAttribute,
    ProductCategory,
    ProductFaq,
    ProductImage,
    Review,
    ReviewPhoto,
    Service,
    ServiceFaq,
    SitePage,
)
from app.utils.files import ALLOWED_IMAGE_EXTENSIONS, save_upload
from app.utils.markdown import excerpt, render_markdown
from app.utils.seo import apply_seo
from app.utils.settings import get_setting, set_setting
from app.utils.slugs import unique_slug
from app.services.reviews_import import clean_review_text


def _commit(message="Сохранено"):
    db.session.commit()
    flash(message, "success")


def _delete(item, endpoint):
    db.session.delete(item)
    db.session.commit()
    flash("Убрано с сайта", "success")
    return redirect(url_for(endpoint))


@admin_bp.route("/news/")
@login_required
def news_list():
    return render_template("admin/cards.html", title="Новости", create_url=url_for("admin.news_edit"), items=[
        {"id": item.id, "title": item.title, "image": item.image, "edit": url_for("admin.news_edit", item_id=item.id), "preview": url_for("news.detail", slug=item.slug) if item.is_published else None}
        for item in News.query.order_by(News.published_at.desc()).all()
    ])


@admin_bp.route("/news/new/", methods=["GET", "POST"])
@admin_bp.route("/news/<int:item_id>/", methods=["GET", "POST"])
@login_required
def news_edit(item_id=None):
    item = News.query.get(item_id) if item_id else News(is_published=True)
    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        item.summary = request.form.get("summary", "").strip()
        item.body_md = request.form.get("body_md", "")
        item.is_published = bool(request.form.get("is_published"))
        image = _save_image("image", "news")
        if image:
            item.image = image
        if request.form.get("seo_title") or request.form.get("seo_description") or request.form.get("slug"):
            item.slug = (request.form.get("slug") or item.slug or unique_slug(News, item.title, item.id)).strip()
            item.seo_title = request.form.get("seo_title") or item.title
            item.seo_description = request.form.get("seo_description") or item.summary
        else:
            if not item.slug:
                item.slug = unique_slug(News, item.title, item.id)
            apply_seo(item, item.title, item.summary, News)
        if item.id is None:
            db.session.add(item)
        _commit("Новость сохранена")
        return redirect(url_for("admin.news_list"))
    return render_template("admin/news_form.html", item=item)


@admin_bp.route("/news/<int:item_id>/delete/", methods=["POST"])
@login_required
def news_delete(item_id):
    return _delete(News.query.get_or_404(item_id), "admin.news_list")


@admin_bp.route("/cases/")
@login_required
def cases_list():
    return render_template("admin/cards.html", title="Кейсы", create_url=url_for("admin.cases_edit"), items=[
        {"id": item.id, "title": item.title, "image": item.cover, "edit": url_for("admin.cases_edit", item_id=item.id), "preview": url_for("cases.detail", slug=item.slug)}
        for item in Case.query.order_by(Case.sort_order, Case.id).all()
    ])


@admin_bp.route("/cases/new/", methods=["GET", "POST"])
@admin_bp.route("/cases/<int:item_id>/", methods=["GET", "POST"])
@login_required
def cases_edit(item_id=None):
    item = Case.query.get(item_id) if item_id else Case(is_published=True, show_on_home=True)
    if request.method == "POST":
        heading = request.form.get("heading", "").strip()
        item.heading = heading
        item.title = heading
        item.lead = request.form.get("lead", "").strip()
        item.fact_material = request.form.get("fact_material", "").strip()
        item.fact_task = request.form.get("fact_task", "").strip()
        item.fact_result = request.form.get("fact_result", "").strip()
        item.fact_material_label = "Материал"
        item.fact_task_label = "Задача"
        item.fact_result_label = "Способ"
        item.tags = ""
        item.works = ""
        item.location = ""
        item.show_on_home = True
        item.is_published = True

        slug = (request.form.get("slug") or "").strip()
        if slug:
            item.slug = unique_slug(Case, slug, item.id)
        elif not item.slug:
            item.slug = unique_slug(Case, heading or "case", item.id)

        item.seo_title = (request.form.get("seo_title") or heading).strip()
        item.seo_description = (request.form.get("seo_description") or item.lead or heading).strip()[:500]

        if item.id is None:
            db.session.add(item)
            db.session.flush()

        delete_ids = {int(value) for value in request.form.getlist("delete_image") if value.isdigit()}
        for image in list(item.images):
            if image.id in delete_ids:
                db.session.delete(image)

        files = request.files.getlist("images")
        next_order = len([image for image in item.images if image.id not in delete_ids])
        for file in files:
            filename = save_upload(file, current_app.config["UPLOAD_FOLDER"] / "cases", ALLOWED_IMAGE_EXTENSIONS)
            if filename:
                db.session.add(
                    CaseImage(
                        case_id=item.id,
                        filename=filename,
                        alt=heading,
                        sort_order=next_order,
                    )
                )
                next_order += 1
        _commit("Кейс сохранён")
        return redirect(url_for("admin.cases_list"))
    return render_template("admin/case_form.html", item=item)


@admin_bp.route("/cases/<int:item_id>/delete/", methods=["POST"])
@login_required
def cases_delete(item_id):
    return _delete(Case.query.get_or_404(item_id), "admin.cases_list")


@admin_bp.route("/reviews/")
@login_required
def reviews_list():
    platform = request.args.get("platform") or "avito"
    if platform not in {"avito", "yandex", "vk"}:
        platform = "avito"

    items = (
        Review.query.filter_by(platform=platform)
        .order_by(Review.sort_order, Review.id)
        .all()
    )
    counts = {
        "avito": Review.query.filter_by(platform="avito").count(),
        "yandex": Review.query.filter_by(platform="yandex").count(),
        "vk": Review.query.filter_by(platform="vk").count(),
    }
    return render_template(
        "admin/reviews_list.html",
        items=items,
        counts=counts,
        current_platform=platform,
    )


@admin_bp.route("/reviews/new/", methods=["GET", "POST"])
@admin_bp.route("/reviews/<int:item_id>/", methods=["GET", "POST"])
@login_required
def reviews_edit(item_id=None):
    if item_id:
        item = Review.query.get_or_404(item_id)
    else:
        platform = request.args.get("platform") or "avito"
        if platform not in {"avito", "yandex", "vk"}:
            platform = "avito"
        item = Review(is_published=True, rating=5, platform=platform)
    if request.method == "POST":
        item.platform = request.form.get("platform") or "avito"
        if item.platform not in {"avito", "yandex", "vk"}:
            item.platform = "avito"
        item.author = request.form.get("author", "").strip()
        item.role = request.form.get("role", "").strip()
        item.text = clean_review_text(request.form.get("text", ""))
        item.item = request.form.get("item", "").strip()
        item.date_text = request.form.get("date_text", "").strip()
        item.rating = request.form.get("rating", type=int) or 5
        item.is_published = bool(request.form.get("is_published"))
        avatar = _save_image("avatar", "reviews")
        if avatar:
            item.avatar = avatar
        if item.id is None:
            db.session.add(item)
            db.session.flush()

        delete_ids = {int(value) for value in request.form.getlist("delete_photo") if value.isdigit()}
        if delete_ids:
            for photo in list(item.photos):
                if photo.id in delete_ids:
                    db.session.delete(photo)

        files = request.files.getlist("photos")
        next_order = len(item.photos)
        for file in files:
            filename = save_upload(
                file,
                current_app.config["UPLOAD_FOLDER"] / "reviews",
                ALLOWED_IMAGE_EXTENSIONS,
            )
            if filename:
                db.session.add(
                    ReviewPhoto(review_id=item.id, filename=filename, sort_order=next_order)
                )
                next_order += 1

        _commit("Отзыв сохранён")
        return redirect(url_for("admin.reviews_list", platform=item.platform))
    return render_template("admin/review_form.html", item=item)


@admin_bp.route("/reviews/<int:item_id>/delete/", methods=["POST"])
@login_required
def reviews_delete(item_id):
    item = Review.query.get_or_404(item_id)
    platform = item.platform or "avito"
    db.session.delete(item)
    _commit("Отзыв удалён")
    return redirect(url_for("admin.reviews_list", platform=platform))


def _collection_edit(model, form_template, list_endpoint, fields, image_field=None, folder="landing"):
    def view(item_id=None):
        item = model.query.get(item_id) if item_id else model()
        if request.method == "POST":
            for field in fields:
                if field in {"is_published"}:
                    setattr(item, field, bool(request.form.get(field)))
                else:
                    setattr(item, field, request.form.get(field, "").strip())
            if image_field:
                image = _save_image(image_field, folder)
                if image:
                    setattr(item, image_field, image)
            if item.id is None:
                db.session.add(item)
            _commit()
            return redirect(url_for(list_endpoint))
        return render_template(form_template, item=item)
    return view


@admin_bp.route("/services/")
@login_required
def services_list():
    return render_template("admin/simple_list.html", title="Услуги", create_url=url_for("admin.services_edit"), rows=[
        {
            "title": f"{item.title} — /uslugi/{item.slug}/" if item.slug else item.title,
            "edit": url_for("admin.services_edit", item_id=item.id),
            "delete": url_for("admin.services_delete", item_id=item.id),
        }
        for item in Service.query.order_by(Service.sort_order, Service.id).all()
    ])


@admin_bp.route("/services/new/", methods=["GET", "POST"])
@admin_bp.route("/services/<int:item_id>/", methods=["GET", "POST"])
@login_required
def services_edit(item_id=None):
    item = Service.query.get(item_id) if item_id else Service(is_published=True)
    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        slug_source = request.form.get("slug", "").strip() or item.title
        item.slug = unique_slug(Service, slug_source, current_id=item.id)
        item.heading = request.form.get("heading", "").strip()
        item.intro = request.form.get("intro", "").strip()
        item.body_md = request.form.get("body_md", "").strip()
        item.text = request.form.get("text", "").strip()
        item.price = request.form.get("price", "").strip()
        item.seo_title = request.form.get("seo_title", "").strip()
        item.seo_description = request.form.get("seo_description", "").strip()
        item.icon = request.form.get("icon", "").strip()
        item.sort_order = request.form.get("sort_order", type=int) or 0
        item.is_published = bool(request.form.get("is_published"))

        image = _save_image("image", "services")
        if image:
            item.image = image
        hero_image = _save_image("hero_image", "services", "hero")
        if hero_image:
            item.hero_image = hero_image

        if item.id is None:
            db.session.add(item)
            db.session.flush()

        item.faqs.clear()
        questions = request.form.getlist("faq_question")
        answers = request.form.getlist("faq_answer")
        order = 0
        for question, answer in zip(questions, answers):
            question = (question or "").strip()
            answer = (answer or "").strip()
            if not question:
                continue
            item.faqs.append(
                ServiceFaq(question=question, answer=answer, sort_order=order)
            )
            order += 1

        if not item.seo_title:
            item.seo_title = item.heading or item.title
        if not item.seo_description:
            from app.utils.markdown import excerpt

            item.seo_description = excerpt(item.intro or item.text or item.title, 160)
        _commit("Услуга сохранена")
        return redirect(url_for("admin.services_edit", item_id=item.id))
    return render_template("admin/service_form.html", item=item)


@admin_bp.route("/services/<int:item_id>/delete/", methods=["POST"])
@login_required
def services_delete(item_id):
    return _delete(Service.query.get_or_404(item_id), "admin.services_list")


@admin_bp.route("/partners/")
@login_required
def partners_list():
    return render_template("admin/simple_list.html", title="Партнёры", create_url=url_for("admin.partners_edit"), rows=[
        {"title": item.name, "edit": url_for("admin.partners_edit", item_id=item.id), "delete": url_for("admin.partners_delete", item_id=item.id)}
        for item in Partner.query.order_by(Partner.sort_order, Partner.id).all()
    ])


@admin_bp.route("/partners/new/", methods=["GET", "POST"])
@admin_bp.route("/partners/<int:item_id>/", methods=["GET", "POST"])
@login_required
def partners_edit(item_id=None):
    item = Partner.query.get(item_id) if item_id else Partner(is_published=True)
    if request.method == "POST":
        item.name = request.form.get("name", "").strip()
        item.text = request.form.get("text", "").strip()
        item.url = request.form.get("url", "").strip()
        item.is_published = bool(request.form.get("is_published"))
        image = _save_image("image", "partners")
        if image:
            item.image = image
        if item.id is None:
            db.session.add(item)
        _commit("Партнёр сохранён")
        return redirect(url_for("admin.partners_list"))
    return render_template("admin/partner_form.html", item=item)


@admin_bp.route("/partners/<int:item_id>/delete/", methods=["POST"])
@login_required
def partners_delete(item_id):
    return _delete(Partner.query.get_or_404(item_id), "admin.partners_list")


@admin_bp.route("/faq/")
@login_required
def faq_list():
    return render_template("admin/simple_list.html", title="Ответы на вопросы", create_url=url_for("admin.faq_edit"), rows=[
        {"title": item.question, "edit": url_for("admin.faq_edit", item_id=item.id), "delete": url_for("admin.faq_delete", item_id=item.id)}
        for item in FaqItem.query.order_by(FaqItem.sort_order, FaqItem.id).all()
    ])


@admin_bp.route("/faq/new/", methods=["GET", "POST"])
@admin_bp.route("/faq/<int:item_id>/", methods=["GET", "POST"])
@login_required
def faq_edit(item_id=None):
    item = FaqItem.query.get(item_id) if item_id else FaqItem(is_published=True)
    if request.method == "POST":
        item.question = request.form.get("question", "").strip()
        item.answer = request.form.get("answer", "").strip()
        item.is_published = bool(request.form.get("is_published"))
        if item.id is None:
            db.session.add(item)
        _commit("Вопрос сохранён")
        return redirect(url_for("admin.faq_list"))
    return render_template("admin/faq_form.html", item=item)


@admin_bp.route("/faq/<int:item_id>/delete/", methods=["POST"])
@login_required
def faq_delete(item_id):
    return _delete(FaqItem.query.get_or_404(item_id), "admin.faq_list")


@admin_bp.route("/pages/<slug>/", methods=["GET", "POST"])
@login_required
def page_edit(slug):
    item = SitePage.query.filter_by(slug=slug).first_or_404()
    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        item.h1 = request.form.get("h1", "").strip()
        item.summary = request.form.get("summary", "").strip()
        item.points = request.form.get("points", "").strip()
        item.body_md = request.form.get("body_md", "")
        item.seo_title = item.title
        item.seo_description = request.form.get("seo_description", "").strip()
        image = _save_image("image", "pages")
        if image:
            item.image = image
        if not item.seo_description:
            from app.utils.markdown import excerpt

            item.seo_description = excerpt(item.summary or item.h1 or item.title, 160)
        _commit("Страница сохранена")
        return redirect(url_for("admin.page_edit", slug=slug))
    labels = {
        "akciya": "Акция",
        "garantiya": "Гарантия",
        "oplata": "Оплата",
        "dostavka": "Доставка",
    }
    return render_template("admin/page_form.html", item=item, heading=labels.get(slug, item.title))


SECTION_FIELDS = {
    "header": [
        ("header.phone", "Телефон"),
        ("header.address", "Адрес"),
        ("header.hours", "Время работы"),
        ("header.org", "Подпись компании в шапке"),
        ("header.email", "Email (если отличается от контактов)"),
    ],
    "hero": [
        ("hero.h1", "H1 на первом экране"),
        ("hero.text", "Текст под H1"),
        ("hero.cta_primary", "Текст основной кнопки"),
        ("hero.cta_secondary", "Текст второй кнопки"),
        ("hero.video", "Видео (путь, например video/hero.mp4)"),
        ("hero.poster", "Постер видео (путь)"),
    ],
    "about": [
        ("about.label", "Надзаголовок"),
        ("about.title", "Заголовок блока «О компании»"),
        ("about.text", "Текст о компании (абзацы через пустую строку)"),
        ("about.video", "Ссылка или путь к видео"),
    ],
    "contacts": [
        ("contacts.email", "Почта"),
        ("contacts.map", "Код или ссылка карты"),
        ("footer.ogrn", "ОГРН / реквизиты"),
        ("checkout.delivery", "Как доставляем (для каталога)"),
        ("checkout.payment", "Как оплачивают (для каталога)"),
    ],
}


@admin_bp.route("/section/<name>/", methods=["GET", "POST"])
@login_required
def section_edit(name):
    fields = SECTION_FIELDS.get(name)
    if not fields:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        for key, _label in fields:
            set_setting(key, request.form.get(key, ""))
        db.session.commit()
        flash("Сохранено", "success")
        return redirect(url_for("admin.section_edit", name=name))
    values = {key: get_setting(key) for key, _label in fields}
    titles = {"header": "Шапка и контакты", "hero": "Первый экран", "about": "О компании", "contacts": "Контакты и подвал"}
    return render_template("admin/section_form.html", title=titles[name], fields=fields, values=values)


@admin_bp.route("/products/")
@login_required
def products_list():
    category_id = request.args.get("category", type=int)
    if not category_id:
        return redirect(url_for("admin.categories_list"))
    category = ProductCategory.query.get_or_404(category_id)
    items = (
        Product.query.filter_by(category_id=category.id)
        .order_by(Product.sort_order, Product.id)
        .all()
    )
    return render_template("admin/products.html", items=items, category=category)


@admin_bp.route("/products/new/", methods=["GET", "POST"])
@admin_bp.route("/products/<int:item_id>/", methods=["GET", "POST"])
@login_required
def products_edit(item_id=None):
    item = Product.query.get(item_id) if item_id else None
    categories = ProductCategory.query.order_by(ProductCategory.sort_order).all()
    default_category_id = request.args.get("category", type=int)
    if item is None:
        item = Product(is_published=True, unit="m2", category_id=default_category_id)

    if request.method == "POST":
        had_md = bool((item.description_md or "").strip())
        item.name = request.form.get("name", "").strip()
        item.category_id = request.form.get("category_id", type=int) or item.category_id
        item.brand = request.form.get("brand", "").strip()
        item.price = request.form.get("price") or 0
        item.unit = request.form.get("unit") or "m2"
        item.short_description = request.form.get("short_description", "").strip()
        item.seo_title = request.form.get("seo_title", "").strip()
        item.seo_description = request.form.get("seo_description", "").strip()
        item.is_published = bool(request.form.get("is_published"))

        slug = request.form.get("slug", "").strip()
        if slug:
            item.slug = unique_slug(Product, slug, item.id)
        elif not item.slug:
            item.slug = unique_slug(Product, item.name, item.id)

        if not item.seo_title:
            item.seo_title = item.name
        if not item.seo_description:
            fallback = item.short_description or item.brand or item.name
            item.seo_description = excerpt(render_markdown(fallback), 160)

        description_md = request.form.get("description_md", "")
        item.description_md = description_md
        if description_md.strip() or had_md or not (item.description_html or "").strip():
            item.description_html = render_markdown(description_md)

        if item.id is None:
            db.session.add(item)
            db.session.flush()

        delete_ids = {int(value) for value in request.form.getlist("delete_image") if value.isdigit()}
        for image in list(item.images):
            if image.id in delete_ids:
                db.session.delete(image)
                continue
            image.alt = request.form.get(f"image_alt_{image.id}", "").strip()

        names = request.form.getlist("attr_name")
        values = request.form.getlist("attr_value")
        ProductAttribute.query.filter_by(product_id=item.id).delete()
        for index, (name, value) in enumerate(zip(names, values)):
            if name.strip():
                db.session.add(
                    ProductAttribute(
                        product_id=item.id,
                        name=name.strip(),
                        value=value.strip(),
                        sort_order=index,
                    )
                )

        questions = request.form.getlist("faq_question")
        answers = request.form.getlist("faq_answer")
        ProductFaq.query.filter_by(product_id=item.id).delete()
        faq_index = 0
        for question, answer in zip(questions, answers):
            if faq_index >= 10:
                break
            if not question.strip():
                continue
            db.session.add(
                ProductFaq(
                    product_id=item.id,
                    question=question.strip(),
                    answer=answer.strip(),
                    sort_order=faq_index,
                )
            )
            faq_index += 1

        remaining_images = [image for image in item.images if image.id not in delete_ids]
        next_sort = len(remaining_images)
        files = request.files.getlist("images")
        for file in files:
            filename = save_upload(file, current_app.config["UPLOAD_FOLDER"] / "catalog", ALLOWED_IMAGE_EXTENSIONS)
            if filename:
                db.session.add(ProductImage(product_id=item.id, filename=filename, alt="", sort_order=next_sort))
                next_sort += 1

        _commit("Товар сохранён")
        return redirect(url_for("admin.products_list", category=item.category_id))

    return render_template("admin/product_form.html", item=item, categories=categories)


@admin_bp.route("/products/<int:item_id>/delete/", methods=["POST"])
@login_required
def products_delete(item_id):
    item = Product.query.get_or_404(item_id)
    category_id = item.category_id
    db.session.delete(item)
    db.session.commit()
    flash("Убрано с сайта", "success")
    return redirect(url_for("admin.products_list", category=category_id))


@admin_bp.route("/categories/")
@login_required
def categories_list():
    items = ProductCategory.query.order_by(ProductCategory.sort_order).all()
    return render_template("admin/categories.html", items=items)


@admin_bp.route("/categories/<int:item_id>/", methods=["GET", "POST"])
@login_required
def categories_edit(item_id):
    item = ProductCategory.query.get_or_404(item_id)
    if request.method == "POST":
        item.name = request.form.get("name", "").strip()
        item.intro = request.form.get("intro", "").strip()
        cover = _save_image("cover", "catalog")
        if cover:
            item.cover = cover
        apply_seo(item, item.name, item.intro)
        _commit("Категория сохранена")
        return redirect(url_for("admin.categories_list"))
    return render_template("admin/category_form.html", item=item)
