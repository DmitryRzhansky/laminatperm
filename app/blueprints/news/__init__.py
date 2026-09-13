from flask import Blueprint, render_template, url_for

from app.models import News
from app.services import seo_meta
from app.utils.markdown import render_markdown

news_bp = Blueprint("news", __name__, url_prefix="/novosti")


@news_bp.route("/")
def index():
    items = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).all()
    path = url_for("news.index")
    title = "Новости"
    description = "Полезные материалы про выбор и укладку напольных покрытий."
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
                    "name": item.title,
                    "url": url_for("news.detail", slug=item.slug),
                }
                for item in items
            ],
        ),
    )
    return render_template("public/pages/news_list.html", items=items, json_ld=json_ld)


@news_bp.route("/<slug>/")
def detail(slug):
    item = News.query.filter_by(slug=slug, is_published=True).first_or_404()
    body = render_markdown(item.body_md)
    path = url_for("news.detail", slug=item.slug)
    json_ld = seo_meta.collect_json_ld(seo_meta.news_article_ld(item, path=path))
    return render_template(
        "public/pages/news_detail.html",
        item=item,
        body=body,
        json_ld=json_ld,
    )
