from flask import Blueprint, render_template, url_for

from app.models import Case
from app.services import seo_meta

cases_bp = Blueprint("cases", __name__, url_prefix="/keysy")


@cases_bp.route("/")
def index():
    items = Case.query.filter_by(is_published=True).order_by(Case.sort_order, Case.id).all()
    path = url_for("cases.index")
    title = "Наши выполненные объекты"
    description = "Реальные объекты: подготовка основания, укладка и результат."
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
                    "name": item.page_heading,
                    "url": url_for("cases.detail", slug=item.slug),
                }
                for item in items
            ],
        ),
    )
    return render_template("public/pages/cases_list.html", items=items, json_ld=json_ld)


@cases_bp.route("/<slug>/")
def detail(slug):
    item = Case.query.filter_by(slug=slug, is_published=True).first_or_404()
    path = url_for("cases.detail", slug=item.slug)
    json_ld = seo_meta.collect_json_ld(seo_meta.case_ld(item, path=path))
    return render_template("public/pages/case_detail.html", item=item, json_ld=json_ld)
