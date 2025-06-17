"""Initial database schema for EcoTrack Ghana

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-06-17 16:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema for EcoTrack Ghana."""
    
    # Create regions table
    op.create_table('regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('capital', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('area_km2', sa.Float(), nullable=True),
        sa.Column('total_users', sa.Integer(), nullable=True, default=0),
        sa.Column('total_activities', sa.Integer(), nullable=True, default=0),
        sa.Column('total_points', sa.Integer(), nullable=True, default=0),
        sa.Column('trash_collected', sa.Float(), nullable=True, default=0.0),
        sa.Column('trees_planted', sa.Integer(), nullable=True, default=0),
        sa.Column('co2_saved', sa.Float(), nullable=True, default=0.0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_regions_id'), 'regions', ['id'], unique=False)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('total_points', sa.Integer(), nullable=True, default=0),
        sa.Column('weekly_points', sa.Integer(), nullable=True, default=0),
        sa.Column('rank', sa.Integer(), nullable=True, default=0),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('role', sa.String(), nullable=True, default='user'),
        sa.Column('permissions', sa.String(), nullable=True, default='basic'),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('trash_collected', sa.Float(), nullable=True, default=0.0),
        sa.Column('trees_planted', sa.Integer(), nullable=True, default=0),
        sa.Column('co2_saved', sa.Float(), nullable=True, default=0.0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create challenges table
    op.create_table('challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('duration', sa.String(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenges_id'), 'challenges', ['id'], unique=False)
    
    # Create activities table
    op.create_table('activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('photos', sa.Text(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('impact_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_id'), 'activities', ['id'], unique=False)
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False),
        sa.Column('priority', sa.String(), nullable=True, default='normal'),
        sa.Column('action_url', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    
    # Create challenge_participants table (many-to-many relationship)
    op.create_table('challenge_participants',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('progress', sa.Float(), nullable=True, default=0.0),
        sa.Column('completed', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'challenge_id')
    )


def downgrade() -> None:
    """Drop all tables in reverse order to handle foreign key constraints."""
    op.drop_table('challenge_participants')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_activities_id'), table_name='activities')
    op.drop_table('activities')
    op.drop_index(op.f('ix_challenges_id'), table_name='challenges')
    op.drop_table('challenges')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_regions_id'), table_name='regions')
    op.drop_table('regions')
