"""Migration script for user_api_keys table only.

This script safely creates the user_api_keys table without affecting existing tables.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from src.models.database import Base
from src.database.connection import engine

# Import the model to register it with Base.metadata
from src.models.user_api_key import UserApiKey


async def create_user_api_keys_table(engine_instance: AsyncEngine = engine) -> None:
    """
    Create user_api_keys table if it doesn't exist.

    This is safe to run multiple times - it will only create the table
    if it doesn't already exist (checkfirst=True).
    """
    async with engine_instance.begin() as conn:
        # Find the user_api_keys table in metadata
        user_api_keys_table = Base.metadata.tables.get('user_api_keys')

        if user_api_keys_table is not None:
            # Create only the user_api_keys table
            await conn.run_sync(
                lambda sync_conn: user_api_keys_table.create(sync_conn, checkfirst=True)
            )
            print("✓ Created table: user_api_keys")
        else:
            print("✗ Error: user_api_keys table not found in metadata")
            print("  Make sure UserApiKey model is properly imported")


async def drop_user_api_keys_table(engine_instance: AsyncEngine = engine) -> None:
    """
    Drop user_api_keys table if it exists.

    ⚠️  WARNING: This will DELETE ALL data in the user_api_keys table!
    Only use for testing or development reset.
    """
    async with engine_instance.begin() as conn:
        # Find the user_api_keys table in metadata
        user_api_keys_table = Base.metadata.tables.get('user_api_keys')

        if user_api_keys_table is not None:
            await conn.run_sync(
                lambda sync_conn: user_api_keys_table.drop(sync_conn, checkfirst=True)
            )
            print("✓ Dropped table: user_api_keys")
        else:
            print("ℹ  Table user_api_keys not found in metadata (may not exist)")


async def verify_table() -> None:
    """Verify that user_api_keys table was created successfully."""
    from sqlalchemy import text

    async with engine.begin() as conn:
        try:
            # Try to query the table
            result = await conn.execute(
                text("SELECT COUNT(*) FROM user_api_keys")
            )
            count = result.scalar()
            print(f"✓ Verification successful: user_api_keys table exists (rows: {count})")
        except Exception as e:
            print(f"✗ Verification failed: {e}")


async def main() -> None:
    """Run the migration."""
    print("=" * 60)
    print("Migration: Create user_api_keys table")
    print("=" * 60)
    print()

    print("Creating user_api_keys table...")
    await create_user_api_keys_table()
    print()

    print("Verifying table creation...")
    await verify_table()
    print()

    print("=" * 60)
    print("Migration complete!")
    print("=" * 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "create":
            asyncio.run(create_user_api_keys_table())
            asyncio.run(verify_table())
        elif command == "drop":
            print("⚠️  WARNING: This will DELETE ALL data in user_api_keys table!")
            confirm = input("Are you sure? Type 'yes' to confirm: ")
            if confirm.lower() == 'yes':
                asyncio.run(drop_user_api_keys_table())
            else:
                print("Aborted.")
        elif command == "verify":
            asyncio.run(verify_table())
        else:
            print("Usage:")
            print("  python -m src.database.migrate_user_api_keys         # Create table")
            print("  python -m src.database.migrate_user_api_keys create  # Create table")
            print("  python -m src.database.migrate_user_api_keys drop    # Drop table (with confirmation)")
            print("  python -m src.database.migrate_user_api_keys verify  # Verify table exists")
    else:
        # Default: create table
        asyncio.run(main())
