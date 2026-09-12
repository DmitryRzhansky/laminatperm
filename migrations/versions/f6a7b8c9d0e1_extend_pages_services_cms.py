"""Extend site pages and services for CMS editing

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-12 20:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


PAGE_DEFAULTS = {
    "akciya": {
        "h1": "Скидка 10% на материал",
        "points": (
            "Скидка действует при заказе укладки под ключ\n"
            "Материал подбираем под помещение и бюджет\n"
            "Точные условия уточним на замере или в шоуруме"
        ),
    },
    "garantiya": {
        "h1": "Гарантия на работы и покрытие",
        "points": (
            "На выполненные работы по укладке — отдельная гарантия исполнителя\n"
            "На материал действует гарантия производителя по паспорту покрытия\n"
            "Помогаем разобраться, если вопрос по качеству или монтажу"
        ),
    },
    "oplata": {
        "h1": "Оплата",
        "points": (
            "Наличные и карта при получении материала или после работ\n"
            "Перевод на карту / расчётный счёт\n"
            "Для юридических лиц подготовим счёт и закрывающие документы"
        ),
    },
    "dostavka": {
        "h1": "Доставка",
        "points": (
            "Самовывоз со склада / шоурума на Агатовой, 28\n"
            "Доставка по Перми и Пермскому краю\n"
            "Стоимость и сроки согласуем при оформлении заказа"
        ),
    },
}


def upgrade():
    with op.batch_alter_table("site_pages", schema=None) as batch_op:
        batch_op.add_column(sa.Column("h1", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("points", sa.Text(), nullable=True))

    with op.batch_alter_table("services", schema=None) as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("heading", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("intro", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("body_md", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("hero_image", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("icon", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("seo_title", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("seo_description", sa.String(length=500), nullable=True))
        batch_op.create_index(batch_op.f("ix_services_slug"), ["slug"], unique=True)

    op.create_table(
        "service_faqs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.String(length=500), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("service_faqs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_service_faqs_service_id"), ["service_id"], unique=False)

    conn = op.get_bind()
    pages = sa.table(
        "site_pages",
        sa.column("slug", sa.String),
        sa.column("h1", sa.String),
        sa.column("points", sa.Text),
        sa.column("title", sa.String),
    )
    for slug, data in PAGE_DEFAULTS.items():
        conn.execute(
            sa.update(pages)
            .where(pages.c.slug == slug)
            .values(h1=data["h1"], points=data["points"])
        )
        conn.execute(
            sa.update(pages)
            .where(pages.c.slug == slug)
            .where(sa.or_(pages.c.h1.is_(None), pages.c.h1 == ""))
            .values(h1=pages.c.title)
        )


def downgrade():
    with op.batch_alter_table("service_faqs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_service_faqs_service_id"))
    op.drop_table("service_faqs")

    with op.batch_alter_table("services", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_services_slug"))
        batch_op.drop_column("seo_description")
        batch_op.drop_column("seo_title")
        batch_op.drop_column("icon")
        batch_op.drop_column("hero_image")
        batch_op.drop_column("body_md")
        batch_op.drop_column("intro")
        batch_op.drop_column("heading")
        batch_op.drop_column("slug")

    with op.batch_alter_table("site_pages", schema=None) as batch_op:
        batch_op.drop_column("points")
        batch_op.drop_column("h1")
