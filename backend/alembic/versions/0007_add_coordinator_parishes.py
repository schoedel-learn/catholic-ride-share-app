"""Add coordinator_parishes junction table.

Revision ID: 0007_add_coordinator_parishes
Revises: 0006_add_coordinator_role
Create Date: 2026-04-01
"""

import sqlalchemy as sa

from alembic import op

revision = "0007_add_coordinator_parishes"
down_revision = "0006_add_coordinator_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create coordinator_parishes junction table."""
    op.create_table(
        "coordinator_parishes",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("parish_id", sa.Integer(), sa.ForeignKey("parishes.id"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("coordinator_parishes")
