"""Add ride cancel fields.

Revision ID: 0008_add_ride_cancel_fields
Revises: 0007_add_coordinator_parishes
Create Date: 2026-04-15
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0008_add_ride_cancel_fields"
down_revision = "0007_add_coordinator_parishes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add cancel_reason and cancelled_at columns to rides table."""
    op.add_column("rides", sa.Column("cancel_reason", sa.String(), nullable=True))
    op.add_column("rides", sa.Column("cancelled_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove cancel fields from rides table."""
    op.drop_column("rides", "cancelled_at")
    op.drop_column("rides", "cancel_reason")
