"""Add Partner.url for official manufacturer links

Revision ID: d4e5f6a7b8c9
Revises: c8a1f2b3d4e5
Create Date: 2026-09-12 19:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c8a1f2b3d4e5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("partners", schema=None) as batch_op:
        batch_op.add_column(sa.Column("url", sa.String(length=500), nullable=True))


def downgrade():
    with op.batch_alter_table("partners", schema=None) as batch_op:
        batch_op.drop_column("url")
