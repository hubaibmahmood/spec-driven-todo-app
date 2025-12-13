"""Migration to add priority and due_date columns to tasks table."""

import asyncio
from sqlalchemy import text
from src.database.connection import engine


async def upgrade() -> None:
    """Add priority and due_date columns to tasks table."""
    print("Running migration: add priority and due_date columns...")

    async with engine.begin() as conn:
        # Create priority enum type if it doesn't exist
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE prioritylevel AS ENUM ('Low', 'Medium', 'High', 'Urgent');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))

        # Add priority column with default value
        await conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS priority prioritylevel DEFAULT 'Medium' NOT NULL;
        """))

        # Add due_date column (nullable)
        await conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE;
        """))

    print("Migration completed successfully!")


async def downgrade() -> None:
    """Remove priority and due_date columns from tasks table."""
    print("Rolling back migration: removing priority and due_date columns...")

    async with engine.begin() as conn:
        # Drop columns
        await conn.execute(text("""
            ALTER TABLE tasks
            DROP COLUMN IF EXISTS priority,
            DROP COLUMN IF EXISTS due_date;
        """))

        # Drop enum type (only if no other tables use it)
        await conn.execute(text("""
            DROP TYPE IF EXISTS prioritylevel;
        """))

    print("Migration rollback completed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())
