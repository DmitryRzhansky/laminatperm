from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.blueprints.admin import admin_bp, _save_image
from app.extensions import db
from app.models import (
    Advantage,
    Case,
    CaseImage,
    Document,
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
    Service,
    SitePage,
    TeamMember,
)
from app.utils.files import ALLOWED_DOCUMENT_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS, save_upload
from app.utils.markdown import excerpt, render_markdown
from app.utils.seo import apply_seo
from app.utils.settings import get_setting, set_setting
from app.utils.slugs import unique_slug


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
        item.title = request.form.get("title", "").strip()
        item.location = request.form.get("location", "").strip()
        item.lead = request.form.get("lead", "").strip()
        item.tags = request.form.get("tags", "").strip()
        item.fact_material = request.form.get("fact_material", "").strip()
        item.fact_task = request.form.get("fact_task", "").strip()
        item.fact_result = request.form.get("fact_result", "").strip()
        item.works = request.form.get("works", "")
        item.show_on_home = bool(request.form.get("show_on_home"))
        item.is_published = bool(request.form.get("is_published"))
        if not item.slug:
            item.slug = unique_slug(Case, item.title, item.id)
        apply_seo(item, item.title, item.lead, Case)
        if item.id is None:
            db.session.add(item)
            db.session.flush()
        files = request.files.getlist("images")
        for file in files:
            filename = save_upload(file, current_app.config["UPLOAD_FOLDER"] / "cases", ALLOWED_IMAGE_EXTENSIONS)
            if filename:
                db.session.add(CaseImage(case_id=item.id, filename=filename, sort_order=len(item.images)))
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
    return render_template("admin/simple_list.html", title="Отзывы", create_url=url_for("admin.reviews_edit"), rows=[
        {"title": f"{item.author} · {item.platform}", "edit": url_for("admin.reviews_edit", item_id=item.id), "delete": url_for("admin.reviews_delete", item_id=item.id)}
        for item in Review.query.order_by(Review.sort_order, Review.id).all()
    ])


@admin_bp.route("/reviews/new/", methods=["GET", "POST"])
@admin_bp.route("/reviews/<int:item_id>/", methods=["GET", "POST"])
@login_required
def reviews_edit(item_id=None):
    item = Review.query.get(item_id) if item_id else Review(is_published=True)
    if request.method == "POST":
        item.platform = request.form.get("platform") or "avito"
        item.author = request.form.get("author", "").strip()
        item.role = request.form.get("role", "").strip()
        item.text = request.form.get("text", "").strip()
        item.item = request.form.get("item", "").strip()
        item.date_text = request.form.get("date_text", "").strip()
        item.rating = request.form.get("rating", type=int) or 5
        item.is_published = bool(request.form.get("is_published"))
        avatar = _save_image("avatar", "reviews")
        if avatar:
            item.avatar = avatar
        if item.id is None:
            db.session.add(item)
        _commit("Отзыв сохранён")
        return redirect(url_for("admin.reviews_list"))
    return render_template("admin/review_form.html", item=item)


@admin_bp.route("/reviews/<int:item_id>/delete/", methods=["POST"])
@login_required
def reviews_delete(item_id):
    return _delete(Review.query.get_or_404(item_id), "admin.reviews_list")


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
    return render_template("admin/simple_list.html", title="Цены и услуги", create_url=url_for("admin.services_edit"), rows=[
        {"title": f"{item.title} — {item.price}", "edit": url_for("admin.services_edit", item_id=item.id), "delete": url_for("admin.services_delete", item_id=item.id)}
        for item in Service.query.order_by(Service.sort_order, Service.id).all()
    ])


@admin_bp.route("/services/new/", methods=["GET", "POST"])
@admin_bp.route("/services/<int:item_id>/", methods=["GET", "POST"])
@login_required
def services_edit(item_id=None):
    item = Service.query.get(item_id) if item_id else Service(is_published=True)
    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        item.text = request.form.get("text", "").strip()
        item.price = request.form.get("price", "").strip()
        item.is_published = bool(request.form.get("is_published"))
        image = _save_image("image", "services")
        if image:
            item.image = image
        if item.id is None:
            db.session.add(item)
        _commit("Услуга сохранена")
        return redirect(url_for("admin.services_list"))
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


@admin_bp.route("/team/")
@login_required
def team_list():
    return render_template("admin/simple_list.html", title="Команда", create_url=url_for("admin.team_edit"), rows=[
        {"title": item.name, "edit": url_for("admin.team_edit", item_id=item.id), "delete": url_for("admin.team_delete", item_id=item.id)}
        for item in TeamMember.query.order_by(TeamMember.sort_order, TeamMember.id).all()
    ])


@admin_bp.route("/team/new/", methods=["GET", "POST"])
@admin_bp.route("/team/<int:item_id>/", methods=["GET", "POST"])
@login_required
def team_edit(item_id=None):
    item = TeamMember.query.get(item_id) if item_id else TeamMember(is_published=True)
    if request.method == "POST":
        item.name = request.form.get("name", "").strip()
        item.role = request.form.get("role", "").strip()
        item.text = request.form.get("text", "").strip()
        item.is_published = bool(request.form.get("is_published"))
        photo = _save_image("photo", "team")
        if photo:
            item.photo = photo
        if item.id is None:
            db.session.add(item)
        _commit("Сотрудник сохранён")
        return redirect(url_for("admin.team_list"))
    return render_template("admin/team_form.html", item=item)


@admin_bp.route("/team/<int:item_id>/delete/", methods=["POST"])
@login_required
def team_delete(item_id):
    return _delete(TeamMember.query.get_or_404(item_id), "admin.team_list")


@admin_bp.route("/documents/")
@login_required
def documents_list():
    return render_template("admin/simple_list.html", title="Лицензии и документы", create_url=url_for("admin.documents_edit"), rows=[
        {"title": item.title, "edit": url_for("admin.documents_edit", item_id=item.id), "delete": url_for("admin.documents_delete", item_id=item.id)}
        for item in Document.query.order_by(Document.sort_order, Document.id).all()
    ])


@admin_bp.route("/documents/new/", methods=["GET", "POST"])
@admin_bp.route("/documents/<int:item_id>/", methods=["GET", "POST"])
@login_required
def documents_edit(item_id=None):
    item = Document.query.get(item_id) if item_id else Document()
    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        file = request.files.get("file")
        if file and file.filename:
            filename = save_upload(file, current_app.config["UPLOAD_FOLDER"] / "documents", ALLOWED_DOCUMENT_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS)
            if filename:
                item.filename = filename
        if not item.filename:
            flash("Добавьте файл документа", "error")
            return render_template("admin/document_form.html", item=item)
        if item.id is None:
            db.session.add(item)
        _commit("Документ сохранён")
        return redirect(url_for("admin.documents_list"))
    return render_template("admin/document_form.html", item=item)


@admin_bp.route("/documents/<int:item_id>/delete/", methods=["POST"])
@login_required
def documents_delete(item_id):
    return _delete(Document.query.get_or_404(item_id), "admin.documents_list")


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
        item.summary = request.form.get("summary", "").strip()
        item.body_md = request.form.get("body_md", "")
        image = _save_image("image", "pages")
        if image:
            item.image = image
        apply_seo(item, item.title, item.summary)
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
        ("header.phone", "Телефон в шапке"),
        ("header.address", "Адрес"),
        ("header.hours", "Время работы"),
        ("header.org", "Короткое описание компании"),
    ],
    "hero": [
        ("hero.h1", "Главный заголовок на первом экране"),
        ("hero.text", "Текст под заголовком"),
        ("hero.video", "Видео (путь к файлу)"),
    ],
    "about": [
        ("about.title", "Заголовок блока «О компании»"),
        ("about.text", "Текст о компании"),
        ("about.video", "Ссылка на видео"),
    ],
    "contacts": [
        ("contacts.email", "Почта"),
        ("contacts.map", "Код карты"),
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
