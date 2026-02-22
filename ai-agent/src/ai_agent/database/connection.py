"""Database connection configuration for AI Agent service."""

import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Clean URL for asyncpg (remove unsupported parameters)
# asyncpg doesn't support 'sslmode' or 'channel_binding' URL parameters
# SSL is configured via connect_args instead
clean_url = DATABASE_URL.replace("?sslmode=require&channel_binding=require", "")
clean_url = clean_url.replace("?sslmode=require", "")
clean_url = clean_url.replace("&channel_binding=require", "")

# SSL configuration for asyncpg
connect_args = {}
if "sslmode=require" in DATABASE_URL or DATABASE_URL.startswith("postgresql+asyncpg://"):
    # For Neon and other cloud databases that require SSL
    connect_args["ssl"] = "require"

# Create async engine with connection pooling for production readiness
engine = create_async_engine(
    clean_url,
    echo=False,  # Set to True for SQL query logging
    future=True,
    pool_size=5,  # Number of persistent connections
    max_overflow=10,  # Additional connections that can be created when pool is exhausted
    pool_timeout=30,  # Timeout for getting connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args=connect_args,
)

# Session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables (for development only)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
