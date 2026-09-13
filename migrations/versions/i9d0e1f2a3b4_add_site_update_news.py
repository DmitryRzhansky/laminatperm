"""Add site update news item

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2a3
Create Date: 2026-09-13 00:00:00.000000

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision = "i9d0e1f2a3b4"
down_revision = "h8c9d0e1f2a3"
branch_labels = None
depends_on = None


SLUG = "obnovlenie-dizaina-saita-i-funkcionala"

NEWS_ITEM = {
    "title": "Обновление дизайна сайта и функционала",
    "slug": SLUG,
    "summary": (
        "Мы обновили сайт Ламинейшен: сделали современный дизайн, удобную "
        "навигацию, каталог товаров и страницы услуг, чтобы выбирать напольные "
        "покрытия стало проще."
    ),
    "body_md": """Мы обновили сайт Ламинейшен и сделали его заметно удобнее для тех, кто выбирает напольное покрытие, планирует укладку или хочет быстро разобраться в услугах.

Раньше сайт был скорее простой одностраничной витриной: на нём можно было найти основные контакты, цены и примеры работ, но информации стало слишком много для одного экрана. Поэтому мы пересобрали структуру и сделали полноценный сайт с понятными разделами.

## Как было раньше

![Старый сайт Ламинейшен](/static/uploads/news/site-update/old-home.png)

## Что изменилось

Теперь на сайте есть отдельные страницы для услуг, каталога, кейсов, отзывов, доставки, оплаты, гарантии и контактов. Навигация стала спокойнее, карточки товаров и материалов — нагляднее, а важные действия вроде заявки, звонка или перехода в мессенджер теперь всегда под рукой.

Мы также обновили визуальный стиль: больше воздуха, чище типографика, лучше адаптация под телефон и аккуратнее подача фотографий работ.

## Новый главный экран

![Новый дизайн главной страницы Ламинейшен](/static/uploads/news/site-update/new-home.png)

## Появился нормальный каталог

Самое заметное обновление — каталог. Теперь напольные покрытия и комплектующие можно смотреть по категориям, с фотографиями, ценами и карточками товаров. Это удобнее, чем искать всё в общем списке или уточнять каждую позицию вручную.

![Новый каталог напольных покрытий Ламинейшен](/static/uploads/news/site-update/new-catalog.png)

Мы продолжим наполнять каталог, добавлять товары, кейсы и полезные материалы. Если коротко: теперь у нас нормальный сайт — не только для связи, но и для выбора покрытия, сравнения вариантов и знакомства с нашей работой до обращения.
""",
    "image": "uploads/news/site-update/new-home.png",
    "seo_title": "Обновление дизайна сайта и функционала — Ламинейшен",
    "seo_description": (
        "У Ламинейшен обновился сайт: современный дизайн, удобный каталог, "
        "страницы услуг, кейсы и полезные разделы для выбора напольных покрытий."
    ),
    "is_published": True,
}


def upgrade():
    bind = op.get_bind()
    now = datetime.utcnow()

    existing = bind.execute(
        sa.text("SELECT id FROM news WHERE slug = :slug"),
        {"slug": SLUG},
    ).fetchone()

    if existing:
        bind.execute(
            sa.text(
                """
                UPDATE news
                SET title = :title,
                    summary = :summary,
                    body_md = :body_md,
                    image = :image,
                    seo_title = :seo_title,
                    seo_description = :seo_description,
                    is_published = :is_published,
                    updated_at = :updated_at
                WHERE slug = :slug
                """
            ),
            {**NEWS_ITEM, "updated_at": now},
        )
        return

    bind.execute(
        sa.text(
            """
            INSERT INTO news (
                title,
                slug,
                summary,
                body_md,
                image,
                seo_title,
                seo_description,
                is_published,
                published_at,
                created_at,
                updated_at
            )
            VALUES (
                :title,
                :slug,
                :summary,
                :body_md,
                :image,
                :seo_title,
                :seo_description,
                :is_published,
                :published_at,
                :created_at,
                :updated_at
            )
            """
        ),
        {
            **NEWS_ITEM,
            "published_at": now,
            "created_at": now,
            "updated_at": now,
        },
    )


def downgrade():
    op.execute(sa.text("DELETE FROM news WHERE slug = :slug").bindparams(slug=SLUG))
