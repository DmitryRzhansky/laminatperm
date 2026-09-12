from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Lead, Order, OrderItem, Product
from app.models.settings import utcnow
from app.utils.files import ALLOWED_IMAGE_EXTENSIONS, save_upload
from app.utils.seo import apply_seo
from app.utils.settings import get_setting, set_setting
from app.utils.slugs import unique_slug

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ORDERS_PER_PAGE = 5
LEADS_PER_PAGE = 10


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


def _page_number(name: str = "page") -> int:
    try:
        value = int(request.args.get(name, 1))
    except (TypeError, ValueError):
        return 1
    return max(1, value)


def _orders_query(*, trashed: bool = False):
    query = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.images),
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.category),
    )
    if trashed:
        return query.filter(Order.deleted_at.isnot(None)).order_by(Order.deleted_at.desc())
    return query.filter(Order.deleted_at.is_(None)).order_by(Order.created_at.desc())


def _leads_query(*, trashed: bool = False):
    query = Lead.query
    if trashed:
        return query.filter(Lead.deleted_at.isnot(None)).order_by(Lead.deleted_at.desc())
    return query.filter(Lead.deleted_at.is_(None)).order_by(Lead.created_at.desc())


def _redirect_back(default_endpoint: str, **values):
    target = request.form.get("next") or request.referrer
    if target and target.startswith(request.host_url):
        return redirect(target)
    return redirect(url_for(default_endpoint, **values))


def _trash_count() -> int:
    return (
        Lead.query.filter(Lead.deleted_at.isnot(None)).count()
        + Order.query.filter(Order.deleted_at.isnot(None)).count()
    )


@admin_bp.context_processor
def inject_admin_globals():
    if not current_user.is_authenticated:
        return {"admin_trash_count": 0}
    return {"admin_trash_count": _trash_count()}


@admin_bp.before_request
def require_login():
    if request.endpoint in {"auth.login", "static"}:
        return None
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login", next=request.path))


@admin_bp.route("/")
@login_required
def dashboard():
    page = _page_number()
    pagination = _leads_query().paginate(page=page, per_page=LEADS_PER_PAGE, error_out=False)
    return render_template(
        "admin/dashboard.html",
        leads=pagination.items,
        pagination=pagination,
    )


@admin_bp.route("/leads/<int:item_id>/trash/", methods=["POST"])
@login_required
def lead_trash(item_id):
    lead = Lead.query.filter_by(id=item_id, deleted_at=None).first_or_404()
    lead.deleted_at = utcnow()
    db.session.commit()
    flash("Заявка перемещена в корзину", "success")
    return _redirect_back("admin.dashboard")


@admin_bp.route("/leads/<int:item_id>/restore/", methods=["POST"])
@login_required
def lead_restore(item_id):
    lead = Lead.query.filter(Lead.id == item_id, Lead.deleted_at.isnot(None)).first_or_404()
    lead.deleted_at = None
    db.session.commit()
    flash("Заявка восстановлена", "success")
    return _redirect_back("admin.trash")


@admin_bp.route("/orders/")
@login_required
def orders():
    page = _page_number()
    pagination = _orders_query().paginate(page=page, per_page=ORDERS_PER_PAGE, error_out=False)
    return render_template(
        "admin/orders.html",
        items=pagination.items,
        pagination=pagination,
    )


@admin_bp.route("/orders/<int:item_id>/trash/", methods=["POST"])
@login_required
def order_trash(item_id):
    order = Order.query.filter_by(id=item_id, deleted_at=None).first_or_404()
    order.deleted_at = utcnow()
    db.session.commit()
    flash("Заказ перемещён в корзину", "success")
    return _redirect_back("admin.orders")


@admin_bp.route("/orders/<int:item_id>/restore/", methods=["POST"])
@login_required
def order_restore(item_id):
    order = Order.query.filter(Order.id == item_id, Order.deleted_at.isnot(None)).first_or_404()
    order.deleted_at = None
    db.session.commit()
    flash("Заказ восстановлен", "success")
    return _redirect_back("admin.trash")


@admin_bp.route("/trash/")
@login_required
def trash():
    leads = _leads_query(trashed=True).all()
    orders_list = _orders_query(trashed=True).all()
    return render_template(
        "admin/trash.html",
        leads=leads,
        orders=orders_list,
        trash_count=len(leads) + len(orders_list),
    )


@admin_bp.route("/trash/empty/", methods=["POST"])
@login_required
def trash_empty():
    deleted_leads = Lead.query.filter(Lead.deleted_at.isnot(None)).delete(synchronize_session=False)
    trashed_orders = Order.query.filter(Order.deleted_at.isnot(None)).all()
    deleted_orders = len(trashed_orders)
    for order in trashed_orders:
        db.session.delete(order)
    db.session.commit()
    flash(
        f"Корзина очищена: удалено заявок — {deleted_leads}, заказов — {deleted_orders}",
        "success",
    )
    return redirect(url_for("admin.trash"))


from app.blueprints.admin import content  # noqa: E402,F401
