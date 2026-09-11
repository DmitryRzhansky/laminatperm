from flask import Blueprint, abort, render_template

from app.models import News
from app.utils.markdown import render_markdown

news_bp = Blueprint("news", __name__, url_prefix="/novosti")


@news_bp.route("/")
def index():
    items = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).all()
    return render_template("public/pages/news_list.html", items=items)


@news_bp.route("/<slug>/")
def detail(slug):
    item = News.query.filter_by(slug=slug, is_published=True).first_or_404()
    body = render_markdown(item.body_md)
    return render_template("public/pages/news_detail.html", item=item, body=body)
