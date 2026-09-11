from flask import Blueprint, render_template

from app.models import Case

cases_bp = Blueprint("cases", __name__, url_prefix="/keysy")


@cases_bp.route("/")
def index():
    items = Case.query.filter_by(is_published=True).order_by(Case.sort_order, Case.id).all()
    return render_template("public/pages/cases_list.html", items=items)


@cases_bp.route("/<slug>/")
def detail(slug):
    item = Case.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("public/pages/case_detail.html", item=item)
