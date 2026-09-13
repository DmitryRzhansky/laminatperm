from decimal import Decimal

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Order, OrderItem, Product, ProductCategory, SitePage
from app.services import seo_meta
from app.services.cart import CartService
from app.services.catalog_filters import (
    SORT_OPTIONS,
    apply_product_filters,
    catalog_query,
    collect_filter_options,
    sort_products,
)
from app.services.product_descriptions import display_name, product_buybox_teaser
from app.services.related_products import products_same_brand
from app.utils.settings import get_setting


def _format_rub(value) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:,.0f}".replace(",", " ") + " ₽"

catalog_bp = Blueprint("catalog", __name__, url_prefix="/catalog")
cart = CartService()


@catalog_bp.route("/")
def index():
    categories = ProductCategory.query.order_by(ProductCategory.sort_order).all()
    path = url_for("catalog.index")
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name="Каталог напольных покрытий",
            description="Ламинат, SPC, кварцвинил, линолеум и ковролин в Перми.",
            path=path,
            page_type="CollectionPage",
        ),
        seo_meta.item_list_ld(
            name="Каталог напольных покрытий",
            path=path,
            description="Категории напольных покрытий в шоуруме Ламинейшен.",
            items=[
                {
                    "name": category.name,
                    "url": url_for("catalog.category", category_slug=category.slug),
                }
                for category in categories
            ],
        ),
    )
    return render_template(
        "public/pages/catalog.html",
        categories=categories,
        current_category=None,
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Каталог"},
        ],
        json_ld=json_ld,
    )


@catalog_bp.route("/<category_slug>/")
def category(category_slug):
    current = ProductCategory.query.filter_by(slug=category_slug).first_or_404()
    all_in_cat = (
        Product.query.filter_by(is_published=True, category_id=current.id)
        .order_by(Product.sort_order, Product.id)
        .all()
    )
    filter_groups = collect_filter_options(all_in_cat)
    products = sort_products(apply_product_filters(all_in_cat))
    current_sort = request.args.get("sort", "default")
    path = url_for("catalog.category", category_slug=current.slug)
    title = (current.seo_title or current.display_heading or current.name).strip()
    description = (current.seo_description or current.intro or current.name).strip()
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name=title,
            description=description,
            path=path,
            page_type="CollectionPage",
        ),
        seo_meta.item_list_ld(
            name=title,
            path=path,
            description=description,
            items=[
                {
                    "name": display_name(product),
                    "url": url_for(
                        "catalog.product",
                        category_slug=current.slug,
                        product_slug=product.slug,
                    ),
                }
                for product in products[:50]
            ],
        ),
    )
    return render_template(
        "public/pages/catalog_category.html",
        products=products,
        current_category=current,
        filter_groups=filter_groups,
        sort_options=SORT_OPTIONS,
        current_sort=current_sort,
        catalog_query=catalog_query,
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Каталог", "url": url_for("catalog.index")},
            {"label": current.name},
        ],
        json_ld=json_ld,
    )


@catalog_bp.route("/<category_slug>/<product_slug>/")
def product(category_slug, product_slug):
    current = ProductCategory.query.filter_by(slug=category_slug).first_or_404()
    item = (
        Product.query.options(joinedload(Product.images), joinedload(Product.faqs), joinedload(Product.attributes))
        .filter_by(slug=product_slug, category_id=current.id, is_published=True)
        .first_or_404()
    )
    warranty_page = SitePage.query.filter_by(slug="garantiya").first()
    warranty_text = ""
    if warranty_page:
        warranty_text = (warranty_page.body_md or warranty_page.summary or "").strip()
    if not warranty_text:
        warranty_text = (
            "Гарантия производителя действует согласно паспорту покрытия. "
            "На работы по укладке даём отдельную гарантию — условия уточняйте у менеджера."
        )
    title = display_name(item)
    related_products = products_same_brand(item)
    path = url_for("catalog.product", category_slug=current.slug, product_slug=item.slug)
    json_ld = seo_meta.collect_json_ld(
        seo_meta.product_ld(item, product_title=title, path=path),
        seo_meta.faq_ld(item.faqs, path=path),
    )
    return render_template(
        "public/pages/product.html",
        item=item,
        product_title=title,
        product_teaser=product_buybox_teaser(item),
        related_products=related_products,
        delivery_text=get_setting(
            "checkout.delivery",
            "Самовывоз из шоурума на Агатовой, 28. Доставка по Перми — согласуем при звонке.",
        ),
        payment_text=get_setting(
            "checkout.payment",
            "Наличные, карта при получении или перевод.",
        ),
        warranty_text=warranty_text,
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Каталог", "url": url_for("catalog.index")},
            {"label": current.name, "url": url_for("catalog.category", category_slug=current.slug)},
            {"label": title},
        ],
        json_ld=json_ld,
    )


@catalog_bp.route("/cart/")
def cart_view():
    path = url_for("catalog.cart_view")
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name="Корзина",
            description="Корзина заказа напольных покрытий в Ламинейшен.",
            path=path,
        )
    )
    return render_template(
        "public/pages/cart.html",
        items=cart.detailed(),
        total=cart.total(),
        json_ld=json_ld,
    )


@catalog_bp.route("/cart/add/", methods=["POST"])
def cart_add():
    product_id = request.form.get("product_id", type=int)
    raw_qty = request.form.get("quantity") or "1"
    try:
        quantity = Decimal(str(raw_qty).replace(",", "."))
    except Exception:
        quantity = Decimal("1")
    quantity = Decimal(max(1, int(CartService._as_int_qty(quantity))))
    product = Product.query.get_or_404(product_id)
    cart.add(product, quantity)

    wants_json = "application/json" in (request.headers.get("Accept") or "")
    if wants_json:
        return jsonify(
            {
                "ok": True,
                "message": "Товар добавлен в корзину",
                "product_id": product.id,
                "cart_count": cart.count(),
                "total": float(cart.total()),
                "total_formatted": _format_rub(cart.total()),
            }
        )

    flash("Товар добавлен в корзину", "success")
    return redirect(request.referrer or url_for("catalog.cart_view"))


@catalog_bp.route("/cart/update/", methods=["POST"])
def cart_update():
    product_id = request.form.get("product_id", type=int)
    quantity = CartService._as_int_qty(request.form.get("quantity") or "0")
    if quantity < 0:
        quantity = Decimal("0")
    cart.update(product_id, quantity)

    wants_json = "application/json" in (request.headers.get("Accept") or "")
    if wants_json:
        line_sum = Decimal("0")
        for item in cart.detailed():
            if item["product"].id == product_id:
                line_sum = item["sum"]
                break
        return jsonify(
            {
                "ok": True,
                "product_id": product_id,
                "quantity": int(quantity),
                "removed": quantity <= 0,
                "line_sum": float(line_sum),
                "line_sum_formatted": _format_rub(line_sum),
                "total": float(cart.total()),
                "total_formatted": _format_rub(cart.total()),
                "cart_count": cart.count(),
            }
        )

    return redirect(url_for("catalog.cart_view"))


@catalog_bp.route("/checkout/", methods=["GET", "POST"])
def checkout():
    items = cart.detailed()
    if request.method == "POST":
        if not items:
            flash("Корзина пуста", "error")
            return redirect(url_for("catalog.cart_view"))
        first_name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        if not first_name or not phone:
            flash("Укажите имя и телефон", "error")
            return redirect(url_for("catalog.checkout"))
        order = Order(
            first_name=first_name,
            phone=phone,
            email=(request.form.get("email") or "").strip(),
            delivery_method=request.form.get("delivery_method") or "pickup",
            address=(request.form.get("address") or "").strip(),
            payment_method=request.form.get("payment_method") or "cash",
            comment=(request.form.get("comment") or "").strip(),
            total=cart.total(),
        )
        db.session.add(order)
        db.session.flush()
        for item in items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item["product"].id,
                    name=item["product"].name,
                    unit=item["product"].unit,
                    quantity=item["quantity"],
                    price=item["product"].price or 0,
                )
            )
        db.session.commit()
        cart.clear()
        flash("Заказ оформлен. Мы свяжемся с вами, чтобы подтвердить детали.", "success")
        return redirect(url_for("catalog.index"))
    path = url_for("catalog.checkout")
    json_ld = seo_meta.collect_json_ld(
        seo_meta.webpage_ld(
            name="Оформление заказа",
            description="Оформление заказа напольных покрытий в Ламинейшен.",
            path=path,
        )
    )
    return render_template(
        "public/pages/checkout.html",
        items=items,
        total=cart.total(),
        json_ld=json_ld,
    )
