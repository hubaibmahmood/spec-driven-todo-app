#!/usr/bin/env python3
"""
SAFE cleanup script - only deletes tasks/sessions for specific user IDs.

This script requires you to provide the user IDs of load test users.
It will NOT delete everything blindly.

Usage:
    # Step 1: Get load test user IDs from auth-server database
    # Run this SQL on your Neon database:
    # SELECT id FROM "user" WHERE email LIKE 'loadtest_user_%@example.com';

    # Step 2: Pass those IDs to this script
    cd backend
    uv run python tests/load/cleanup_load_test_data_safe.py --user-ids "user1,user2,user3"

    # Or use --all-tasks to delete ALL tasks (use with caution!)
    uv run python tests/load/cleanup_load_test_data_safe.py --all-tasks --confirm
"""

import asyncio
import sys
import ssl
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import settings


def get_db_url():
    """Get database URL with proper SSL configuration."""
    db_url = settings.DATABASE_URL
    if "?" in db_url:
        db_url = db_url.split("?")[0]
    return db_url


def get_ssl_context():
    """Get SSL context for Neon connection."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context


async def cleanup_for_user_ids(user_ids: List[str], dry_run: bool = False):
    """Delete tasks and sessions for specific user IDs only."""

    engine = create_async_engine(
        get_db_url(),
        echo=False,
        connect_args={
            "ssl": get_ssl_context(),
            "server_settings": {"application_name": "cleanup-safe"},
        }
    )

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            from src.models.database import Task, UserSession
            from sqlalchemy import func

            print(f"🧹 Cleanup for {len(user_ids)} user IDs")
            print("=" * 60)

            # Count what will be deleted
            tasks_count_stmt = select(func.count()).select_from(Task).where(
                Task.user_id.in_(user_ids)
            )
            tasks_count = await session.scalar(tasks_count_stmt)

            sessions_count_stmt = select(func.count()).select_from(UserSession).where(
                UserSession.user_id.in_(user_ids)
            )
            sessions_count = await session.scalar(sessions_count_stmt)

            print(f"Will delete:")
            print(f"  - {tasks_count} tasks")
            print(f"  - {sessions_count} sessions")
            print(f"  - For user IDs: {', '.join(user_ids[:3])}{'...' if len(user_ids) > 3 else ''}")

            if dry_run:
                print("\n✓ DRY RUN - No data deleted")
                return

            print("\n⚠️  Proceed with deletion? (yes/no): ", end="")
            confirm = input().strip().lower()

            if confirm != "yes":
                print("❌ Cancelled")
                return

            # Delete tasks
            delete_tasks = delete(Task).where(Task.user_id.in_(user_ids))
            await session.execute(delete_tasks)

            # Delete sessions
            delete_sessions = delete(UserSession).where(UserSession.user_id.in_(user_ids))
            await session.execute(delete_sessions)

            await session.commit()

            print("=" * 60)
            print("✓ Cleanup complete!")
            print(f"  Deleted {tasks_count} tasks")
            print(f"  Deleted {sessions_count} sessions")

        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def show_all_stats():
    """Show statistics for ALL data in database."""

    engine = create_async_engine(
        get_db_url(),
        echo=False,
        connect_args={
            "ssl": get_ssl_context(),
            "server_settings": {"application_name": "cleanup-stats"},
        }
    )

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            from src.models.database import Task, UserSession
            from sqlalchemy import func, distinct

            print("📊 Backend Database Statistics")
            print("=" * 60)

            # Total tasks
            total_tasks = await session.scalar(select(func.count()).select_from(Task))
            print(f"Total tasks: {total_tasks}")

            # Unique users with tasks
            unique_task_users = await session.scalar(
                select(func.count(distinct(Task.user_id))).select_from(Task)
            )
            print(f"Unique users with tasks: {unique_task_users}")

            # Total sessions
            total_sessions = await session.scalar(
                select(func.count()).select_from(UserSession)
            )
            print(f"Total sessions: {total_sessions}")

            # Unique users with sessions
            unique_session_users = await session.scalar(
                select(func.count(distinct(UserSession.user_id))).select_from(UserSession)
            )
            print(f"Unique users with sessions: {unique_session_users}")

            print("=" * 60)
            print("\n⚠️  To clean up load test data:")
            print("1. Query auth-server DB for load test user IDs:")
            print("   SELECT id FROM \"user\" WHERE email LIKE 'loadtest_user_%@example.com';")
            print("\n2. Pass those IDs to this script:")
            print("   uv run python tests/load/cleanup_load_test_data_safe.py --user-ids 'id1,id2,id3'")

        except Exception as e:
            print(f"❌ Error: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Safe cleanup of load test data")
    parser.add_argument(
        "--user-ids",
        type=str,
        help="Comma-separated user IDs to delete data for"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics"
    )

    args = parser.parse_args()

    if args.stats:
        asyncio.run(show_all_stats())
    elif args.user_ids:
        user_ids = [uid.strip() for uid in args.user_ids.split(",")]
        asyncio.run(cleanup_for_user_ids(user_ids, dry_run=args.dry_run))
    else:
        print("Usage:")
        print("  --stats              Show database statistics")
        print("  --user-ids 'id1,id2' Delete data for specific user IDs")
        print("  --dry-run            Preview deletions without deleting")
        print("\nExample:")
        print("  uv run python tests/load/cleanup_load_test_data_safe.py --stats")
        print("  uv run python tests/load/cleanup_load_test_data_safe.py --user-ids 'user1,user2' --dry-run")
