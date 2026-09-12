"""Extend cases for homepage-parity CMS fields

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-12 21:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "g7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("cases", schema=None) as batch_op:
        batch_op.add_column(sa.Column("heading", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("fact_material_label", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("fact_task_label", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("fact_result_label", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("fact_material_icon", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("fact_task_icon", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("fact_result_icon", sa.String(length=255), nullable=True))

    with op.batch_alter_table("case_images", schema=None) as batch_op:
        batch_op.add_column(sa.Column("alt", sa.String(length=500), nullable=True))

    op.execute("UPDATE cases SET heading = title WHERE heading IS NULL OR heading = ''")
    op.execute("UPDATE cases SET fact_material_label = 'Материал' WHERE fact_material_label IS NULL OR fact_material_label = ''")
    op.execute("UPDATE cases SET fact_task_label = 'Задача' WHERE fact_task_label IS NULL OR fact_task_label = ''")
    op.execute("UPDATE cases SET fact_result_label = 'Результат' WHERE fact_result_label IS NULL OR fact_result_label = ''")
    op.execute("UPDATE cases SET fact_material_icon = 'icons/cases/stack.svg' WHERE fact_material_icon IS NULL OR fact_material_icon = ''")
    op.execute("UPDATE cases SET fact_task_icon = 'icons/cases/clipboard-text.svg' WHERE fact_task_icon IS NULL OR fact_task_icon = ''")
    op.execute("UPDATE cases SET fact_result_icon = 'icons/cases/shield-check.svg' WHERE fact_result_icon IS NULL OR fact_result_icon = ''")
    op.execute("UPDATE case_images SET alt = '' WHERE alt IS NULL")


def downgrade():
    with op.batch_alter_table("case_images", schema=None) as batch_op:
        batch_op.drop_column("alt")

    with op.batch_alter_table("cases", schema=None) as batch_op:
        batch_op.drop_column("fact_result_icon")
        batch_op.drop_column("fact_task_icon")
        batch_op.drop_column("fact_material_icon")
        batch_op.drop_column("fact_result_label")
        batch_op.drop_column("fact_task_label")
        batch_op.drop_column("fact_material_label")
        batch_op.drop_column("heading")
