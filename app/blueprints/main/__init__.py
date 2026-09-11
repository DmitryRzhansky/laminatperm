from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Lead
from app.utils.settings import settings_map

main_bp = Blueprint("main", __name__)


def _home_context():
    from app.models import (
        Advantage,
        Case,
        FaqItem,
        News,
        Partner,
        ProcessVideo,
        ProductCategory,
        Review,
        Service,
    )

    return {
        "settings": settings_map(),
        "advantages": Advantage.query.order_by(Advantage.sort_order, Advantage.id).all(),
        "services": Service.query.filter_by(is_published=True).order_by(Service.sort_order, Service.id).all(),
        "categories": ProductCategory.query.order_by(ProductCategory.sort_order, ProductCategory.id).all(),
        "partners": Partner.query.filter_by(is_published=True).order_by(Partner.sort_order, Partner.id).all(),
        "reviews": Review.query.filter_by(is_published=True).order_by(Review.sort_order, Review.id).all(),
        "home_cases": Case.query.filter_by(is_published=True, show_on_home=True).order_by(Case.sort_order, Case.id).all(),
        "process_videos": ProcessVideo.query.order_by(ProcessVideo.sort_order, ProcessVideo.id).all(),
        "news_preview": News.query.filter_by(is_published=True).order_by(News.published_at.desc()).limit(7).all(),
        "faq_items": FaqItem.query.filter_by(is_published=True).order_by(FaqItem.sort_order, FaqItem.id).all(),
    }


@main_bp.route("/")
def home():
    return render_template("public/pages/home.html", **_home_context())


@main_bp.route("/zayavka/", methods=["POST"])
def submit_lead():
    if (request.form.get("website") or "").strip():
        return redirect(request.referrer or url_for("main.home"))

    first_name = (request.form.get("name") or "").strip()
    last_name = (request.form.get("lastname") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    email = (request.form.get("email") or "").strip()
    product = (request.form.get("product") or "").strip()
    details = (request.form.get("details") or "").strip()
    consent = request.form.get("consent")

    if not first_name or not phone or not consent:
        flash("Проверьте поля заявки", "error")
        return redirect(request.referrer or url_for("main.home") + "#consultation")

    product_id = request.form.get("product_id", type=int)
    lead = Lead(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        product=product,
        details=details,
        source=request.form.get("source") or "consultation",
        product_id=product_id,
    )
    db.session.add(lead)
    db.session.commit()
    flash("Заявка принята. Мы свяжемся с вами в ближайшее время.", "success")
    return redirect(request.referrer or url_for("main.home") + "#consultation")


@main_bp.route("/praice/")
@main_bp.route("/praice")
def praice_redirect():
    return redirect(url_for("catalog.index"), code=301)


@main_bp.route("/praice/tproduct/<path:rest>")
def praice_product_redirect(rest):
    from app.models import Product, ProductRedirect

    uid = rest.split("-", 1)[0]
    mapping = ProductRedirect.query.filter_by(tilda_uid=uid).first()
    product = mapping.product if mapping else Product.query.filter_by(tilda_uid=uid).first()
    if not product:
        return redirect(url_for("catalog.index"), code=301)
    return redirect(
        url_for("catalog.product", category_slug=product.category.slug, product_slug=product.slug),
        code=301,
    )
