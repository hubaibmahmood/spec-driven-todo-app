"""add priority and due_date columns

Revision ID: 20251215_001
Revises:
Create Date: 2025-12-15 14:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251215_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add priority and due_date columns to tasks table."""
    # Create priority enum type
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE prioritylevel AS ENUM ('Low', 'Medium', 'High', 'Urgent');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Add priority column with default value
    op.execute("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS priority prioritylevel DEFAULT 'Medium' NOT NULL;
    """)

    # Add due_date column (nullable)
    op.execute("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE;
    """)


def downgrade() -> None:
    """Remove priority and due_date columns from tasks table."""
    # Drop columns
    op.execute("""
        ALTER TABLE tasks
        DROP COLUMN IF EXISTS priority,
        DROP COLUMN IF EXISTS due_date;
    """)

    # Drop enum type
    op.execute("""
        DROP TYPE IF EXISTS prioritylevel;
    """)
