from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Lead, Order
from app.utils.files import ALLOWED_IMAGE_EXTENSIONS, save_upload
from app.utils.seo import apply_seo
from app.utils.settings import get_setting, set_setting
from app.utils.slugs import unique_slug

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _uploads(*parts):
    folder = current_app.config["UPLOAD_FOLDER"]
    for part in parts:
        folder = folder / part
    return folder


def _save_image(field_name, *parts):
    file = request.files.get(field_name)
    if not file or not file.filename:
        return None
    return save_upload(file, _uploads(*parts), ALLOWED_IMAGE_EXTENSIONS)


@admin_bp.before_request
def require_login():
    if request.endpoint in {"auth.login", "static"}:
        return None
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login", next=request.path))


@admin_bp.route("/")
@login_required
def dashboard():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    new_leads = Lead.query.filter_by(status="new").count()
    new_orders = Order.query.filter_by(status="new").count()
    return render_template(
        "admin/dashboard.html",
        leads=leads,
        orders=orders,
        new_leads=new_leads,
        new_orders=new_orders,
    )


@admin_bp.route("/leads/<int:item_id>/status/", methods=["POST"])
@login_required
def lead_status(item_id):
    lead = Lead.query.get_or_404(item_id)
    lead.status = request.form.get("status") or lead.status
    db.session.commit()
    flash("Статус заявки обновлён", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/orders/")
@login_required
def orders():
    items = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", items=items)


@admin_bp.route("/orders/<int:item_id>/status/", methods=["POST"])
@login_required
def order_status(item_id):
    order = Order.query.get_or_404(item_id)
    order.status = request.form.get("status") or order.status
    db.session.commit()
    flash("Статус заказа обновлён", "success")
    return redirect(url_for("admin.orders"))


from app.blueprints.admin import content  # noqa: E402,F401
