"""Add soft-delete timestamps for orders and leads

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-12 20:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f("ix_orders_deleted_at"), ["deleted_at"], unique=False)

    with op.batch_alter_table("leads", schema=None) as batch_op:
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f("ix_leads_deleted_at"), ["deleted_at"], unique=False)


def downgrade():
    with op.batch_alter_table("leads", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_leads_deleted_at"))
        batch_op.drop_column("deleted_at")

    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_orders_deleted_at"))
        batch_op.drop_column("deleted_at")
