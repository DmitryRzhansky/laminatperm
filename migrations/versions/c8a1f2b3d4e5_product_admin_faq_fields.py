"""Product admin FAQ, short description, image alt

Revision ID: c8a1f2b3d4e5
Revises: b36cf0006ea5
Create Date: 2026-09-11 13:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c8a1f2b3d4e5"
down_revision = "b36cf0006ea5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("short_description", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("description_md", sa.Text(), nullable=True))

    with op.batch_alter_table("product_images", schema=None) as batch_op:
        batch_op.add_column(sa.Column("alt", sa.String(length=255), nullable=True))

    op.create_table(
        "product_faqs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.String(length=500), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("product_faqs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_product_faqs_product_id"), ["product_id"], unique=False)


def downgrade():
    with op.batch_alter_table("product_faqs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_product_faqs_product_id"))
    op.drop_table("product_faqs")

    with op.batch_alter_table("product_images", schema=None) as batch_op:
        batch_op.drop_column("alt")

    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("description_md")
        batch_op.drop_column("short_description")
