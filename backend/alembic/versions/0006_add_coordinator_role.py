"""Add coordinator role to userrole enum.

Revision ID: 0006_add_coordinator_role
Revises: 0005_add_dioceses_table
Create Date: 2026-04-01
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0006_add_coordinator_role"
down_revision = "0005_add_dioceses_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add 'coordinator' to the userrole PostgreSQL enum."""
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'coordinator'")


def downgrade() -> None:
    """PostgreSQL does not support removing enum values directly.

    To fully downgrade, you would need to:
    1. Update any rows using 'coordinator' to another role.
    2. Recreate the enum type without the value.
    3. Recreate the column with the new enum.
    For safety, this downgrade is a no-op.
    """
    pass
