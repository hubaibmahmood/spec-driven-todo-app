# Alembic Migration Management

## Common Commands

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"

# Apply all migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision>

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision>

# Show current revision
alembic current

# Show migration history
alembic history

# Show SQL without running
alembic upgrade head --sql
```

## Migration File Structure

```python
"""Add users table

Revision ID: abc123
Revises:
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Apply migration."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

def downgrade() -> None:
    """Rollback migration."""
    op.drop_index('ix_users_username', 'users')
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
```

## Common Operations

### Add Column
```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```

### Modify Column
```python
def upgrade():
    op.alter_column('users', 'email',
        type_=sa.String(300),
        existing_type=sa.String(255),
        nullable=False
    )

def downgrade():
    op.alter_column('users', 'email',
        type_=sa.String(255),
        existing_type=sa.String(300)
    )
```

### Add Foreign Key
```python
def upgrade():
    op.create_foreign_key(
        'fk_posts_author_id',
        'posts', 'users',
        ['author_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    op.drop_constraint('fk_posts_author_id', 'posts', type_='foreignkey')
```

### Add Index
```python
def upgrade():
    op.create_index('ix_posts_created_at', 'posts', ['created_at'])

def downgrade():
    op.drop_index('ix_posts_created_at', 'posts')
```

### Data Migration
```python
from sqlalchemy import table, column

def upgrade():
    # Define table for data operations
    users = table('users',
        column('id', sa.Integer),
        column('is_active', sa.Boolean)
    )

    # Update data
    op.execute(
        users.update()
        .where(users.c.is_active == None)
        .values({'is_active': True})
    )

def downgrade():
    pass
```

## Best Practices

1. **Always test migrations**: Test both upgrade and downgrade
2. **Use autogenerate carefully**: Review generated migrations
3. **Write reversible migrations**: Ensure downgrade works
4. **Batch operations**: Group related changes
5. **Data safety**: Backup before destructive operations
6. **Version control**: Commit migrations with code changes
