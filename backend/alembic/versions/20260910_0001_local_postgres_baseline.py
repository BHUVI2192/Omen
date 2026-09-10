"""Create the local PostgreSQL migration baseline.

Revision ID: 20260910_0001
Revises:
Create Date: 2026-09-10
"""

from alembic import op

revision = '20260910_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The application schema is introduced in the next migration phase.
    pass


def downgrade() -> None:
    pass