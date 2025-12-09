---
name: database-integration
description: PostgreSQL database integration with SQLAlchemy 2.0 async ORM, Alembic migrations, connection pooling, and repository pattern. Use for database setup, model creation, migrations, async queries, and data access patterns.
allowed-tools: Read, Edit, Bash, Glob, Grep
---

# Database Integration with PostgreSQL & SQLAlchemy

## Overview

This skill provides comprehensive guidance for integrating PostgreSQL databases with FastAPI using SQLAlchemy 2.0 async ORM, Alembic for migrations, and implementing the repository pattern for clean data access.

## When to Use

- Setting up database connections
- Creating SQLAlchemy models
- Writing async database queries
- Managing database migrations with Alembic
- Implementing repository pattern
- Configuring connection pooling
- Transaction management
- Database testing strategies

## PostgreSQL with AsyncPG

### Database URL Format

```python
# Development
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# Neon Serverless
DATABASE_URL = "postgresql+asyncpg://user:password@endpoint.neon.tech/dbname"

# Environment variable
import os
DATABASE_URL = os.getenv("DATABASE_URL")
```

### Installing Dependencies

```bash
pip install sqlalchemy[asyncio] asyncpg alembic
```

## SQLAlchemy 2.0 Async Setup

### Database Engine and Session

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,           # Log SQL queries
    future=True,                      # Use SQLAlchemy 2.0 API
    pool_pre_ping=True,               # Verify connections before use
    pool_size=settings.DB_POOL_SIZE,  # Connection pool size
    max_overflow=settings.DB_MAX_OVERFLOW  # Max overflow connections
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,          # Manual control over flushing
    autocommit=False          # Manual transaction control
)

# Dependency for FastAPI
async def get_db() -> AsyncSession:
    """Get database session for dependency injection."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# Base class for models
Base = declarative_base()
```

### Database Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    class Config:
        env_file = ".env"

settings = Settings()
```

## Creating Models

### Basic Model

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

### Model with Relationships

```python
# app/models/post.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign key
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Relationship
    author = relationship("User", back_populates="posts")

# app/models/user.py (add to User model)
class User(Base):
    # ... existing fields ...
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
```

## Async Queries

### Basic CRUD Operations

```python
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_data: dict) -> User:
        """Create new user."""
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, user_data: dict) -> User | None:
        """Update existing user."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**user_data)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
```

### Filtering and Ordering

```python
from sqlalchemy import or_, and_

async def search_users(
    self,
    search_term: str = None,
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100
) -> list[User]:
    """Search users with filters."""
    stmt = select(User)

    # Apply filters
    filters = []
    if search_term:
        filters.append(
            or_(
                User.email.ilike(f"%{search_term}%"),
                User.username.ilike(f"%{search_term}%")
            )
        )
    if is_active is not None:
        filters.append(User.is_active == is_active)

    if filters:
        stmt = stmt.where(and_(*filters))

    # Apply ordering and pagination
    stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)

    result = await self.db.execute(stmt)
    return list(result.scalars().all())
```

### Relationships and Joins

```python
from sqlalchemy.orm import selectinload, joinedload

async def get_user_with_posts(self, user_id: int) -> User | None:
    """Get user with all their posts (N+1 prevention)."""
    stmt = (
        select(User)
        .options(selectinload(User.posts))  # Eager load posts
        .where(User.id == user_id)
    )
    result = await self.db.execute(stmt)
    return result.scalar_one_or_none()

async def get_posts_with_authors(self, skip: int = 0, limit: int = 100) -> list[Post]:
    """Get posts with author information."""
    stmt = (
        select(Post)
        .options(joinedload(Post.author))  # Eager load author
        .offset(skip)
        .limit(limit)
        .order_by(Post.created_at.desc())
    )
    result = await self.db.execute(stmt)
    return list(result.unique().scalars().all())
```

## Transaction Management

### Manual Transaction Control

```python
async def transfer_operation(self, from_id: int, to_id: int, amount: float):
    """Execute multiple operations in a transaction."""
    async with self.db.begin():
        # All operations in this block are part of same transaction
        await self.debit_account(from_id, amount)
        await self.credit_account(to_id, amount)
        await self.log_transaction(from_id, to_id, amount)
        # Automatically commits if no exception
        # Automatically rolls back if exception occurs
```

### Explicit Transaction

```python
from sqlalchemy.exc import IntegrityError

async def create_user_with_rollback(self, user_data: dict) -> User | None:
    """Create user with explicit transaction control."""
    try:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    except IntegrityError:
        await self.db.rollback()
        return None
    except Exception:
        await self.db.rollback()
        raise
```

## Alembic Migrations

### Initial Setup

```bash
# Initialize Alembic
alembic init alembic

# Configure alembic.ini
# Set: sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/dbname
```

### Configuration for Async

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.db.session import Base
from app.models import user, post  # Import all models

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    import asyncio
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Create users table"

# Create empty migration
alembic revision -m "Add custom index"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

## Repository Pattern

### Base Repository

```python
# app/repositories/base_repository.py
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: int) -> Optional[ModelType]:
        """Get by ID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_data: dict) -> ModelType:
        """Create new object."""
        obj = self.model(**obj_data)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: int, obj_data: dict) -> Optional[ModelType]:
        """Update existing object."""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_data)
            .returning(self.model)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: int) -> bool:
        """Delete object."""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
```

### Specific Repository

```python
# app/repositories/user_repository.py
from app.repositories.base_repository import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    """User-specific repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        stmt = select(User).where(User.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
```

## Best Practices

### 1. Use Async Everywhere

```python
# ✅ Good: Async operations
async def get_user(self, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = await self.db.execute(stmt)
    return result.scalar_one_or_none()

# ❌ Bad: Sync operations in async context
def get_user(self, user_id: int):
    return self.db.query(User).filter(User.id == user_id).first()
```

### 2. Prevent N+1 Queries

```python
# ✅ Good: Eager loading
stmt = select(User).options(selectinload(User.posts))

# ❌ Bad: N+1 queries
users = await get_users()
for user in users:
    posts = await get_user_posts(user.id)  # N queries!
```

### 3. Use Repository Pattern

```python
# ✅ Good: Repository pattern
repository = UserRepository(db)
user = await repository.get_by_email(email)

# ❌ Bad: Direct queries in service
stmt = select(User).where(User.email == email)
user = await db.execute(stmt)
```

## Reference

For detailed information, see:
- [SQLALCHEMY.md](SQLALCHEMY.md) - SQLAlchemy patterns and queries
- [ALEMBIC.md](ALEMBIC.md) - Migration management guide
- [examples/migration-example.py](examples/migration-example.py) - Sample migration

## Quick Checklist

- [ ] Async engine configured with connection pooling
- [ ] Models use proper types and constraints
- [ ] Relationships configured with lazy loading options
- [ ] Repository pattern implemented
- [ ] Migrations set up with Alembic
- [ ] Transaction management for multi-step operations
- [ ] Eager loading used to prevent N+1 queries
- [ ] Database session properly managed with dependency injection
