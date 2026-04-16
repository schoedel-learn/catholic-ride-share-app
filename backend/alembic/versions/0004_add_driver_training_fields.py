"""Add driver training fields.

Revision ID: 0004_add_driver_training_fields
Revises: 0003_add_donation_system
Create Date: 2026-04-01
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0004_add_driver_training_fields"
down_revision = "0003_add_donation_system"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add driver training status fields."""
    op.add_column(
        "driver_profiles",
        sa.Column("training_completed_date", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "driver_profiles",
        sa.Column("training_expiration_date", sa.DateTime(), nullable=True),
    )
    op.add_column("driver_profiles", sa.Column("admin_notes", sa.String(), nullable=True))


def downgrade() -> None:
    """Remove driver training status fields."""
    op.drop_column("driver_profiles", "admin_notes")
    op.drop_column("driver_profiles", "training_expiration_date")
    op.drop_column("driver_profiles", "training_completed_date")
