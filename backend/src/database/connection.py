"""Database connection and session management."""

import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.config import settings

# Configure engine based on database type
if "sqlite" in settings.DATABASE_URL:
    # SQLite doesn't support pool settings
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.SQLALCHEMY_ECHO,
        future=True,
    )
else:
    # Clean the database URL for asyncpg (remove sslmode query params)
    db_url = settings.DATABASE_URL
    if "?" in db_url:
        # Remove query parameters that asyncpg doesn't understand
        base_url = db_url.split("?")[0]
    else:
        base_url = db_url

    # Create SSL context for Neon
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # PostgreSQL with Neon-optimized settings
    engine = create_async_engine(
        base_url,
        echo=settings.SQLALCHEMY_ECHO,
        future=True,
        pool_pre_ping=True,  # Essential for Neon serverless
        pool_size=settings.SQLALCHEMY_POOL_SIZE,
        max_overflow=settings.SQLALCHEMY_POOL_OVERFLOW,
        pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT,
        pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
        connect_args={
            "ssl": ssl_context,
            "server_settings": {"application_name": "todo-app-fastapi"},
        },
    )

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,  # Manual control over flushing
    autocommit=False,  # Manual transaction control
)


async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI to get database session.

    Yields:
        AsyncSession: Database session for the request.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Commit transaction after successful endpoint execution
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()
