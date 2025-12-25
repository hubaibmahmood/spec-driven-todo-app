"""Create user_api_keys table for encrypted API key storage

Revision ID: 20251224_002
Revises: 20251215_001_add_priority_and_due_date
Create Date: 2025-12-24
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251224_002'
down_revision = '20251215_001_add_priority_and_due_date'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_api_keys table for storing encrypted Gemini API keys."""
    op.create_table(
        'user_api_keys',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('encrypted_key', sa.String(length=500), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='gemini'),
        sa.Column('validation_status', sa.String(length=50), nullable=True),
        sa.Column('last_validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'provider', name='uq_user_provider_key')
    )
    op.create_index('idx_user_api_keys_user_id', 'user_api_keys', ['user_id'])


def downgrade() -> None:
    """Drop user_api_keys table."""
    op.drop_index('idx_user_api_keys_user_id', table_name='user_api_keys')
    op.drop_table('user_api_keys')
