"""Add notifications table and reminder_sent column to tasks

Revision ID: 20260305_003
Revises: 20251224_002
Create Date: 2026-03-05
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260305_003'
down_revision = '20251224_002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add reminder_sent to tasks and create notifications table."""
    # Add reminder_sent column to tasks table
    op.add_column(
        'tasks',
        sa.Column('reminder_sent', sa.Boolean(), server_default='false', nullable=False)
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('sent_email', sa.Boolean(), server_default='false', nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index(
        'idx_notifications_user_is_read', 'notifications', ['user_id', 'is_read']
    )


def downgrade() -> None:
    """Remove notifications table and reminder_sent column."""
    op.drop_index('idx_notifications_user_is_read', table_name='notifications')
    op.drop_index('idx_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
    op.drop_column('tasks', 'reminder_sent')
