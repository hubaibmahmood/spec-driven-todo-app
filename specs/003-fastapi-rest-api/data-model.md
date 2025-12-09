# Data Model: FastAPI REST API

**Feature**: 003-fastapi-rest-api
**Date**: 2025-12-10
**Database**: Neon PostgreSQL (shared with better-auth server)

## Overview

This document defines the data model for the FastAPI todo application. The application uses **two categories of tables**:

1. **Owned by FastAPI** (migrations managed by this service): `tasks`
2. **Owned by Auth Server** (migrations managed by better-auth): `users`, `user_sessions`

---

## Entity Relationship Diagram

```
┌─────────────────────────┐
│ users                   │ (Auth Server)
├─────────────────────────┤
│ id (UUID, PK)          │
│ email (VARCHAR)         │
│ name (VARCHAR)          │
│ created_at (TIMESTAMP)  │
└──────────┬──────────────┘
           │
           │ 1:N
           │
┌──────────┴──────────────┐
│ user_sessions           │ (Auth Server)
├─────────────────────────┤
│ id (UUID, PK)          │
│ user_id (UUID, FK)     │◄─── FK to users.id
│ token_hash (VARCHAR)    │
│ refresh_token_hash (...)│
│ expires_at (TIMESTAMP)  │
│ revoked (BOOLEAN)       │
│ ip_address (TEXT)       │
│ user_agent (TEXT)       │
│ created_at (TIMESTAMP)  │
│ last_activity_at (...)  │
└──────────┬──────────────┘
           │
           │ Referenced by
           │ (no FK constraint)
           │
┌──────────┴──────────────┐
│ tasks                   │ (FastAPI)
├─────────────────────────┤
│ id (INTEGER, PK)       │
│ user_id (UUID)         │◄─── Reference only (no FK)
│ title (VARCHAR 200)     │
│ description (TEXT)      │
│ completed (BOOLEAN)     │
│ created_at (TIMESTAMP)  │
│ updated_at (TIMESTAMP)  │
└─────────────────────────┘
```

**Design Decision**: No foreign key constraint from `tasks.user_id` to `users.id` because tables are owned by different services. Application-level validation ensures referential integrity.

---

## Table Definitions

### 1. tasks (Owned by FastAPI)

**Purpose**: Stores todo tasks for authenticated users

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `INTEGER` | `PRIMARY KEY, AUTO_INCREMENT` | Unique task identifier |
| `user_id` | `UUID` | `NOT NULL, INDEX` | Owner of the task (references users.id) |
| `title` | `VARCHAR(200)` | `NOT NULL` | Task title (1-200 characters) |
| `description` | `TEXT` | `NULL` | Task description (max 1000 characters, optional) |
| `completed` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE` | Completion status |
| `created_at` | `TIMESTAMP` | `NOT NULL, DEFAULT NOW()` | Task creation timestamp (UTC) |
| `updated_at` | `TIMESTAMP` | `NOT NULL, DEFAULT NOW()` | Last update timestamp (UTC) |

**Indexes**:
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_id_created_at ON tasks(user_id, created_at DESC);
```

**Validation Rules**:
- `title`: Required, 1-200 characters, non-empty after trim
- `description`: Optional, max 1000 characters
- `user_id`: Must reference valid user in users table (application-level check)
- `completed`: Boolean only (true/false)

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index('idx_tasks_user_id', 'user_id'),
        Index('idx_tasks_user_id_created_at', 'user_id', 'created_at'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Task(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
```

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from uuid import UUID

class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy ORM compatibility
```

---

### 2. users (Owned by Auth Server - Reference Only)

**Purpose**: User accounts managed by better-auth Node.js server

**Schema** (for reference, **do not migrate**):

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | `PRIMARY KEY` | Unique user identifier |
| `email` | `VARCHAR(255)` | `NOT NULL, UNIQUE` | User email address |
| `name` | `VARCHAR(255)` | `NULL` | User display name |
| `created_at` | `TIMESTAMP` | `NOT NULL` | Account creation timestamp |

**FastAPI Usage**: Read-only reference for user_id validation

**SQLAlchemy Model** (reference only, not in LocalBase):
```python
class User(Base):
    """Reference model for auth server's users table (read-only)."""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Don't create in migrations

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False)
```

---

### 3. user_sessions (Owned by Auth Server - Reference Only)

**Purpose**: Session tokens managed by better-auth Node.js server

**Schema** (for reference, **do not migrate**):

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | `PRIMARY KEY` | Unique session identifier |
| `user_id` | `UUID` | `NOT NULL, FK → users.id` | Session owner |
| `token_hash` | `VARCHAR(255)` | `NOT NULL, UNIQUE` | Hashed session token (HMAC-SHA256) |
| `refresh_token_hash` | `VARCHAR(255)` | `NULL` | Hashed refresh token |
| `expires_at` | `TIMESTAMP` | `NOT NULL` | Session expiration time |
| `revoked` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE` | Revocation status |
| `ip_address` | `TEXT` | `NULL` | Client IP address |
| `user_agent` | `TEXT` | `NULL` | Client user agent |
| `created_at` | `TIMESTAMP` | `NOT NULL` | Session creation time |
| `last_activity_at` | `TIMESTAMP` | `NOT NULL` | Last activity timestamp |

**FastAPI Usage**: Query for session validation

**SQLAlchemy Model** (reference only):
```python
class UserSession(Base):
    """Reference model for auth server's user_sessions table (read-only)."""
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    refresh_token_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    ip_address = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, nullable=False)
```

---

## Data Access Patterns

### Query Patterns

**1. Get all tasks for user** (most common):
```sql
SELECT * FROM tasks
WHERE user_id = $1
ORDER BY created_at DESC;
```

**2. Get single task by ID and user** (authorization check):
```sql
SELECT * FROM tasks
WHERE id = $1 AND user_id = $2;
```

**3. Validate session token** (authentication):
```sql
SELECT id, user_id, expires_at
FROM user_sessions
WHERE token_hash = $1
  AND expires_at > NOW()
  AND revoked = FALSE;
```

**4. Create task**:
```sql
INSERT INTO tasks (user_id, title, description, completed, created_at, updated_at)
VALUES ($1, $2, $3, FALSE, NOW(), NOW())
RETURNING *;
```

**5. Update task**:
```sql
UPDATE tasks
SET title = $1, description = $2, updated_at = NOW()
WHERE id = $3 AND user_id = $4
RETURNING *;
```

**6. Delete task**:
```sql
DELETE FROM tasks
WHERE id = $1 AND user_id = $2;
```

### Repository Pattern

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models.database import Task
from uuid import UUID
from typing import Optional

class TaskRepository:
    """Repository for task data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_by_user(self, user_id: UUID) -> list[Task]:
        """Get all tasks for a user."""
        stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, task_id: int, user_id: UUID) -> Optional[Task]:
        """Get task by ID with user authorization check."""
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_id: UUID, title: str, description: Optional[str]) -> Task:
        """Create new task."""
        task = Task(user_id=user_id, title=title, description=description)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update(self, task: Task) -> Task:
        """Update existing task."""
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: int, user_id: UUID) -> bool:
        """Delete task by ID (with authorization check)."""
        stmt = delete(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
```

---

## Migration Strategy

### Alembic Configuration

**Target Metadata**: Only `tasks` table (FastAPI-owned)

```python
# alembic/env.py
from src.models.database import Base

# ONLY include FastAPI tables
target_metadata = Base.metadata

# Exclude auth server tables from autogenerate
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in ["users", "user_sessions"]:
        return False
    return True

context.configure(
    connection=connection,
    target_metadata=target_metadata,
    include_object=include_object,
)
```

### Initial Migration

```python
# alembic/versions/001_create_tasks_table.py
"""Create tasks table

Revision ID: 001
Create Date: 2025-12-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_id_created_at', 'tasks', ['user_id', 'created_at'])

def downgrade():
    op.drop_index('idx_tasks_user_id_created_at', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')
```

---

## Data Constraints & Validation

### Application-Level Constraints

| Constraint | Enforcement | Rationale |
|------------|-------------|-----------|
| **Task title required** | Pydantic validation | Enforced before DB insert |
| **Title length 1-200** | Pydantic + DB schema | Both application and DB layer |
| **Description max 1000** | Pydantic validation | Application-level enforcement |
| **User exists** | Application check | No FK constraint (cross-service) |
| **User owns task** | Query WHERE clause | Authorization check on all operations |

### Database-Level Constraints

| Constraint | Type | Enforcement |
|------------|------|-------------|
| `id PRIMARY KEY` | DB | Uniqueness guaranteed |
| `user_id NOT NULL` | DB | Cannot create task without user |
| `title NOT NULL` | DB | Cannot create task without title |
| `completed DEFAULT FALSE` | DB | New tasks start incomplete |
| Indexes on user_id | DB | Query performance |

---

## Performance Considerations

### Expected Load

- **Users**: 1,000-10,000 concurrent users
- **Tasks per user**: Average 100, max 1,000
- **Read/write ratio**: 3:1 (100 reads/min vs 30 writes/min per user)

### Optimization Strategy

1. **Indexes**: `idx_tasks_user_id` and `idx_tasks_user_id_created_at` for common queries
2. **Connection pooling**: 10-30 connections (see research.md)
3. **Query optimization**: Always filter by `user_id` first (indexed)
4. **No N+1 queries**: Use repository pattern with proper selects

### Query Performance Targets

| Operation | Target | Expected |
|-----------|--------|----------|
| Get all tasks (user) | <300ms | 100-200ms |
| Get single task | <200ms | 50-100ms |
| Create task | <200ms | 100-150ms |
| Update task | <200ms | 100-150ms |
| Delete task | <200ms | 50-100ms |
| Validate session | <100ms | 20-50ms |

---

## Summary

**Tables Owned by FastAPI**: 1 (`tasks`)
**Tables Referenced**: 2 (`users`, `user_sessions` - auth server)
**Foreign Key Constraints**: 0 (application-level validation)
**Indexes**: 2 (user_id, user_id+created_at)
**Migrations**: Alembic with autogenerate for `tasks` only

**Next**: Generate API contracts (OpenAPI specification)
