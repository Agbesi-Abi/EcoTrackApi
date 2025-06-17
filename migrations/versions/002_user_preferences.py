"""Add user preferences table

Revision ID: 002_user_preferences
Revises: 001_initial_schema
Create Date: 2025-06-17 16:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_user_preferences'
down_revision: Union[str, Sequence[str], None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user preferences table for storing user settings."""
    
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_email', sa.Boolean(), nullable=True, default=True),
        sa.Column('notification_push', sa.Boolean(), nullable=True, default=True),
        sa.Column('notification_challenges', sa.Boolean(), nullable=True, default=True),
        sa.Column('notification_achievements', sa.Boolean(), nullable=True, default=True),
        sa.Column('privacy_profile_public', sa.Boolean(), nullable=True, default=True),
        sa.Column('privacy_show_in_leaderboard', sa.Boolean(), nullable=True, default=True),
        sa.Column('language', sa.String(5), nullable=True, default='en'),
        sa.Column('theme', sa.String(20), nullable=True, default='light'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_preferences_id'), 'user_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=True)


def downgrade() -> None:
    """Remove user preferences table."""
    op.drop_index(op.f('ix_user_preferences_user_id'), table_name='user_preferences')
    op.drop_index(op.f('ix_user_preferences_id'), table_name='user_preferences')
    op.drop_table('user_preferences')
