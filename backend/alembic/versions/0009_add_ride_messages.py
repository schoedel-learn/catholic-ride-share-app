"""Add ride_messages table.

Revision ID: 0009_add_ride_messages
Revises: 0008_add_ride_cancel_fields
Create Date: 2026-04-19
"""

import sqlalchemy as sa

from alembic import op

revision = "0009_add_ride_messages"
down_revision = "0008_add_ride_cancel_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ride_messages table."""
    op.create_table(
        "ride_messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "ride_id",
            sa.Integer(),
            sa.ForeignKey("rides.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "sender_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("is_deleted", sa.String(1), nullable=False, server_default="N"),
    )


def downgrade() -> None:
    """Drop ride_messages table."""
    op.drop_table("ride_messages")
