from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Order, OrderItem, Product, ProductCategory
from app.services.cart import CartService
from app.utils.settings import get_setting

catalog_bp = Blueprint("catalog", __name__, url_prefix="/catalog")
cart = CartService()


def _filter_products(query):
    brand = request.args.get("brand", "").strip()
    thickness = request.args.get("thickness", "").strip()
    wear = request.args.get("wear", "").strip()
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    sort = request.args.get("sort", "default")

    if brand:
        query = query.filter(Product.brand == brand)
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)

    products = query.all()
    if thickness:
        products = [item for item in products if thickness in item.attr("Толщина")]
    if wear:
        products = [item for item in products if wear in item.attr("Класс износостойкости")]

    if sort == "price_asc":
        products.sort(key=lambda item: item.price or 0)
    elif sort == "price_desc":
        products.sort(key=lambda item: item.price or 0, reverse=True)
    elif sort == "name":
        products.sort(key=lambda item: item.name.lower())
    else:
        products.sort(key=lambda item: (item.sort_order, item.id))
    return products


def _filter_options(products):
    brands = sorted({item.brand for item in products if item.brand})
    thicknesses = sorted({item.attr("Толщина") for item in products if item.attr("Толщина")})
    wears = sorted({item.attr("Класс износостойкости") for item in products if item.attr("Класс износостойкости")})
    return brands, thicknesses, wears


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
    base_query = Product.query.filter_by(is_published=True, category_id=current.id)
    products = _filter_products(base_query)
    all_in_cat = Product.query.filter_by(is_published=True, category_id=current.id).all()
    brands, thicknesses, wears = _filter_options(all_in_cat)
    return render_template(
        "public/pages/catalog_category.html",
        products=products,
        current_category=current,
        brands=brands,
        thicknesses=thicknesses,
        wears=wears,
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
