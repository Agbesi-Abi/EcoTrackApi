"""Add activity categories and improve indexing

Revision ID: 003_activity_improvements
Revises: 002_user_preferences
Create Date: 2025-06-17 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_activity_improvements'
down_revision: Union[str, Sequence[str], None] = '002_user_preferences'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add activity categories table and improve activity indexing."""
    
    # Create activity_categories table
    op.create_table('activity_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),  # Hex color code
        sa.Column('points_multiplier', sa.Float(), nullable=True, default=1.0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_activity_categories_id'), 'activity_categories', ['id'], unique=False)
    op.create_index(op.f('ix_activity_categories_name'), 'activity_categories', ['name'], unique=True)
    
    # Add foreign key to activities table for category
    op.add_column('activities', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_activities_category_id', 
        'activities', 
        'activity_categories', 
        ['category_id'], 
        ['id']
    )
    
    # Add useful indexes for activities
    op.create_index('ix_activities_user_id', 'activities', ['user_id'])
    op.create_index('ix_activities_type', 'activities', ['type'])
    op.create_index('ix_activities_region', 'activities', ['region'])
    op.create_index('ix_activities_created_at', 'activities', ['created_at'])
    op.create_index('ix_activities_verified', 'activities', ['verified'])
    
    # Add indexes for users table
    op.create_index('ix_users_region', 'users', ['region'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_total_points', 'users', ['total_points'])
    
    # Add indexes for challenges
    op.create_index('ix_challenges_category', 'challenges', ['category'])
    op.create_index('ix_challenges_is_active', 'challenges', ['is_active'])
    op.create_index('ix_challenges_start_date', 'challenges', ['start_date'])
    op.create_index('ix_challenges_end_date', 'challenges', ['end_date'])
    
    # Add indexes for notifications
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    
    # Insert default activity categories
    op.execute("""
        INSERT INTO activity_categories (name, display_name, description, icon, color, points_multiplier, sort_order) VALUES
        ('trash', 'Waste Collection', 'Collecting and properly disposing of waste materials', 'trash-2', '#e74c3c', 1.0, 1),
        ('trees', 'Tree Planting', 'Planting trees and vegetation for environmental conservation', 'tree', '#27ae60', 1.2, 2),
        ('mobility', 'Sustainable Mobility', 'Using eco-friendly transportation methods', 'car', '#3498db', 0.8, 3),
        ('water', 'Water Conservation', 'Conserving and protecting water resources', 'droplets', '#2980b9', 1.0, 4),
        ('energy', 'Energy Conservation', 'Reducing energy consumption and using renewable sources', 'zap', '#f39c12', 1.1, 5),
        ('education', 'Environmental Education', 'Teaching and learning about environmental issues', 'book-open', '#9b59b6', 0.9, 6),
        ('cleanup', 'Community Cleanup', 'Organizing or participating in community cleanup events', 'users', '#e67e22', 1.3, 7),
        ('recycling', 'Recycling', 'Recycling materials and promoting circular economy', 'refresh-cw', '#1abc9c', 1.0, 8)
    """)


def downgrade() -> None:
    """Remove activity categories and indexes."""
    
    # Remove indexes for notifications
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    
    # Remove indexes for challenges
    op.drop_index('ix_challenges_end_date', table_name='challenges')
    op.drop_index('ix_challenges_start_date', table_name='challenges')
    op.drop_index('ix_challenges_is_active', table_name='challenges')
    op.drop_index('ix_challenges_category', table_name='challenges')
    
    # Remove indexes for users
    op.drop_index('ix_users_total_points', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_region', table_name='users')
    
    # Remove indexes for activities
    op.drop_index('ix_activities_verified', table_name='activities')
    op.drop_index('ix_activities_created_at', table_name='activities')
    op.drop_index('ix_activities_region', table_name='activities')
    op.drop_index('ix_activities_type', table_name='activities')
    op.drop_index('ix_activities_user_id', table_name='activities')
    
    # Remove foreign key and column from activities
    op.drop_constraint('fk_activities_category_id', 'activities', type_='foreignkey')
    op.drop_column('activities', 'category_id')
    
    # Remove activity_categories table
    op.drop_index(op.f('ix_activity_categories_name'), table_name='activity_categories')
    op.drop_index(op.f('ix_activity_categories_id'), table_name='activity_categories')
    op.drop_table('activity_categories')
