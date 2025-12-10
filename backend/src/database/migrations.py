"""Custom database migration functions."""

import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from src.models.database import Base
from src.database.connection import engine


async def create_tables(engine_instance: AsyncEngine = engine) -> None:
    """
    Create all tables defined in Base metadata.
    
    Only creates tables that don't already exist.
    Excludes tables owned by auth server (users, user_sessions).
    """
    # Filter metadata to only include FastAPI-owned tables
    from sqlalchemy.schema import CreateTable
    
    async with engine_instance.begin() as conn:
        # Only create tasks table (exclude users and user_sessions)
        for table in Base.metadata.sorted_tables:
            if table.name == "tasks":
                await conn.run_sync(lambda sync_conn: table.create(sync_conn, checkfirst=True))
                print(f"Created table: {table.name}")


async def drop_tables(engine_instance: AsyncEngine = engine) -> None:
    """
    Drop all FastAPI-owned tables.
    
    WARNING: This will delete all data in the tasks table.
    Only use for testing or development reset.
    """
    async with engine_instance.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name == "tasks":
                await conn.run_sync(lambda sync_conn: table.drop(sync_conn, checkfirst=True))
                print(f"Dropped table: {table.name}")


async def init_db() -> None:
    """Initialize database with all tables."""
    print("Initializing database...")
    await create_tables()
    print("Database initialization complete!")


async def reset_db() -> None:
    """Reset database (drop and recreate all tables)."""
    print("Resetting database...")
    await drop_tables()
    await create_tables()
    print("Database reset complete!")


if __name__ == "__main__":
    # Run migration from command line
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "init":
            asyncio.run(init_db())
        elif command == "reset":
            asyncio.run(reset_db())
        else:
            print("Usage: python -m src.database.migrations [init|reset]")
    else:
        asyncio.run(init_db())
