"""Add dioceses table and parish diocese FK.

Revision ID: 0005_add_dioceses_table
Revises: 0004_add_driver_training_fields
Create Date: 2026-04-01
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0005_add_dioceses_table"
down_revision = "0004_add_driver_training_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create dioceses table and add diocese_id FK to parishes."""
    op.create_table(
        "dioceses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.add_column(
        "parishes",
        sa.Column("diocese_id", sa.Integer(), sa.ForeignKey("dioceses.id"), nullable=True),
    )


def downgrade() -> None:
    """Remove diocese_id FK from parishes and drop dioceses table."""
    op.drop_column("parishes", "diocese_id")
    op.drop_table("dioceses")
