"""
Example: Complete migration for users and posts tables

This shows a comprehensive migration including:
- Table creation
- Indexes
- Foreign keys
- Constraints
- Default values
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'create_users_posts_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create users and posts tables."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('length(username) >= 3', name='username_min_length')
    )

    # Create indexes for users
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # Create posts table
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('length(title) > 0', name='title_not_empty')
    )

    # Create indexes for posts
    op.create_index('ix_posts_id', 'posts', ['id'], unique=False)
    op.create_index('ix_posts_title', 'posts', ['title'], unique=False)
    op.create_index('ix_posts_author_id', 'posts', ['author_id'], unique=False)
    op.create_index('ix_posts_created_at', 'posts', ['created_at'], unique=False)

    # Create foreign key
    op.create_foreign_key(
        'fk_posts_author_id_users',
        'posts', 'users',
        ['author_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    """Drop posts and users tables."""

    # Drop foreign keys first
    op.drop_constraint('fk_posts_author_id_users', 'posts', type_='foreignkey')

    # Drop posts indexes
    op.drop_index('ix_posts_created_at', 'posts')
    op.drop_index('ix_posts_author_id', 'posts')
    op.drop_index('ix_posts_title', 'posts')
    op.drop_index('ix_posts_id', 'posts')

    # Drop posts table
    op.drop_table('posts')

    # Drop users indexes
    op.drop_index('ix_users_username', 'users')
    op.drop_index('ix_users_email', 'users')
    op.drop_index('ix_users_id', 'users')

    # Drop users table
    op.drop_table('users')
