from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Order, OrderItem, Product, ProductCategory
from app.services.cart import CartService
from app.services.catalog_filters import (
    SORT_OPTIONS,
    apply_product_filters,
    catalog_query,
    collect_filter_options,
    sort_products,
)
from app.utils.settings import get_setting

catalog_bp = Blueprint("catalog", __name__, url_prefix="/catalog")
cart = CartService()


@catalog_bp.route("/")
def index():
    categories = ProductCategory.query.order_by(ProductCategory.sort_order).all()
    return render_template(
        "public/pages/catalog.html",
        categories=categories,
        current_category=None,
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Каталог"},
        ],
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
    )


@catalog_bp.route("/<category_slug>/<product_slug>/")
def product(category_slug, product_slug):
    current = ProductCategory.query.filter_by(slug=category_slug).first_or_404()
    item = Product.query.filter_by(slug=product_slug, category_id=current.id, is_published=True).first_or_404()
    return render_template(
        "public/pages/product.html",
        item=item,
        delivery_text=get_setting("checkout.delivery", ""),
        payment_text=get_setting("checkout.payment", ""),
        breadcrumbs=[
            {"label": "Главная", "url": url_for("main.home")},
            {"label": "Каталог", "url": url_for("catalog.index")},
            {"label": current.name, "url": url_for("catalog.category", category_slug=current.slug)},
            {"label": item.name},
        ],
    )


@catalog_bp.route("/cart/")
def cart_view():
    return render_template("public/pages/cart.html", items=cart.detailed(), total=cart.total())


@catalog_bp.route("/cart/add/", methods=["POST"])
def cart_add():
    product_id = request.form.get("product_id", type=int)
    quantity = Decimal(request.form.get("quantity") or "1")
    product = Product.query.get_or_404(product_id)
    cart.add(product, quantity)
    flash("Товар добавлен в корзину", "success")
    return redirect(request.referrer or url_for("catalog.cart_view"))


@catalog_bp.route("/cart/update/", methods=["POST"])
def cart_update():
    product_id = request.form.get("product_id", type=int)
    quantity = Decimal(request.form.get("quantity") or "0")
    cart.update(product_id, quantity)
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
    return render_template("public/pages/checkout.html", items=items, total=cart.total())
