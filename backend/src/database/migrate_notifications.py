"""Migration script for notifications table and reminder_sent column.

Adds:
- notifications table (in-app notification bell)
- reminder_sent column on tasks (prevents duplicate emails)
"""

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database.connection import engine
from src.models.database import Base

# Import models to register them with Base.metadata
from src.models.notification import Notification  # noqa: F401


async def upgrade(engine_instance: AsyncEngine = engine) -> None:
    """Apply migration: add reminder_sent to tasks, create notifications table."""
    async with engine_instance.begin() as conn:
        # 1. Add reminder_sent column to tasks (idempotent)
        await conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN NOT NULL DEFAULT false
        """))
        print("✓ Added column: tasks.reminder_sent")

        # 2. Create notifications table (idempotent)
        notifications_table = Base.metadata.tables.get("notifications")
        if notifications_table is not None:
            await conn.run_sync(
                lambda sync_conn: notifications_table.create(sync_conn, checkfirst=True)
            )
            print("✓ Created table: notifications")
        else:
            print("✗ Error: notifications table not found in metadata")
            return

        # 3. Create indexes (idempotent via IF NOT EXISTS)
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id
            ON notifications (user_id)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_is_read
            ON notifications (user_id, is_read)
        """))
        print("✓ Created indexes on notifications")


async def downgrade(engine_instance: AsyncEngine = engine) -> None:
    """Rollback: drop notifications table and reminder_sent column."""
    async with engine_instance.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS notifications"))
        print("✓ Dropped table: notifications")

        await conn.execute(text(
            "ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_sent"
        ))
        print("✓ Dropped column: tasks.reminder_sent")


async def verify(engine_instance: AsyncEngine = engine) -> None:
    """Verify migration was applied successfully."""
    async with engine_instance.begin() as conn:
        # Check reminder_sent column exists
        result = await conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'tasks' AND column_name = 'reminder_sent'
        """))
        if result.fetchone():
            print("✓ Verified: tasks.reminder_sent column exists")
        else:
            print("✗ Missing: tasks.reminder_sent column")

        # Check notifications table exists
        result = await conn.execute(text("""
            SELECT COUNT(*) FROM notifications
        """))
        count = result.scalar()
        print(f"✓ Verified: notifications table exists (rows: {count})")


async def main() -> None:
    """Run the migration."""
    print("=" * 60)
    print("Migration: notifications table + tasks.reminder_sent")
    print("=" * 60)
    print()

    print("Applying migration...")
    await upgrade()
    print()

    print("Verifying...")
    await verify()
    print()

    print("=" * 60)
    print("Migration complete!")
    print("=" * 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in ("upgrade", "create"):
            asyncio.run(upgrade())
            asyncio.run(verify())
        elif command == "downgrade":
            print("⚠️  WARNING: This will DROP the notifications table and reminder_sent column!")
            confirm = input("Are you sure? Type 'yes' to confirm: ")
            if confirm.lower() == "yes":
                asyncio.run(downgrade())
            else:
                print("Aborted.")
        elif command == "verify":
            asyncio.run(verify())
        else:
            print("Usage:")
            print("  python -m src.database.migrate_notifications           # Apply migration")
            print("  python -m src.database.migrate_notifications upgrade   # Apply migration")
            print("  python -m src.database.migrate_notifications downgrade # Rollback")
            print("  python -m src.database.migrate_notifications verify    # Verify")
    else:
        asyncio.run(main())
