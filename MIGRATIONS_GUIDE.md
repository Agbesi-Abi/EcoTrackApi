# Database Migrations Guide - EcoTrack Ghana

## Overview

EcoTrack Ghana uses **Alembic** for database schema migrations. This allows us to:
- Version control database schema changes
- Apply schema updates safely in production
- Rollback changes if needed
- Collaborate on database changes across team members

## Migration Management

We've created a custom migration manager (`migrate.py`) that provides convenient commands for managing migrations.

### Quick Start

```bash
# Check current migration status
python migrate.py status

# Apply all pending migrations
python migrate.py upgrade

# Create a new migration
python migrate.py create "Add user preferences table"

# Check database connection
python migrate.py check-db
```

## Available Commands

### 1. **Status** - Check current migration state
```bash
python migrate.py status
```
Shows:
- Current migration revision
- Migration history
- Database connection status

### 2. **Create Migration** - Generate new migration file
```bash
# Auto-generate based on model changes
python migrate.py create "Add new table"

# Create empty migration for manual changes
python -m alembic revision -m "Manual migration"
```

### 3. **Upgrade Database** - Apply migrations
```bash
# Apply all pending migrations
python migrate.py upgrade

# Apply up to specific revision
python migrate.py upgrade abc123
```

### 4. **Downgrade Database** - Rollback migrations
```bash
# Rollback to specific revision
python migrate.py downgrade abc123

# Rollback one migration
python migrate.py downgrade -1
```

### 5. **Other Utilities**
```bash
# Show pending migrations
python migrate.py pending

# Validate migration files
python migrate.py validate

# Show database schema info
python migrate.py schema

# Seed initial data
python migrate.py seed

# Reset database (WARNING: Destroys data)
python migrate.py reset
```

## Migration Files Structure

```
migrations/
├── env.py                    # Alembic environment configuration
├── script.py.mako           # Migration file template
├── alembic.ini              # Alembic configuration
└── versions/                # Migration files
    ├── 001_initial_schema.py
    ├── 002_user_preferences.py
    └── 003_activity_improvements.py
```

## Current Migration Timeline

### 001_initial_schema
- **Purpose**: Create all core EcoTrack Ghana tables
- **Tables Created**:
  - `users` - User accounts and profiles
  - `regions` - Ghana regions data
  - `activities` - Environmental activities
  - `challenges` - Community challenges
  - `notifications` - User notifications
  - `challenge_participants` - Many-to-many relationship table

### 002_user_preferences
- **Purpose**: Add user settings and preferences
- **Tables Created**:
  - `user_preferences` - User notification and privacy settings

### 003_activity_improvements
- **Purpose**: Enhance activity categorization and database performance
- **Changes**:
  - Added `activity_categories` table
  - Added database indexes for better performance
  - Linked activities to categories

## Creating New Migrations

### Auto-generated Migrations

When you modify models in `database.py`, create auto-generated migrations:

```bash
# 1. Modify your models in database.py
# 2. Generate migration
python migrate.py create "Describe your changes"
# 3. Review the generated migration file
# 4. Apply the migration
python migrate.py upgrade
```

### Manual Migrations

For data migrations or complex changes:

```python
# Example migration file structure
def upgrade() -> None:
    """Apply migration changes."""
    # Create tables
    op.create_table('new_table', ...)
    
    # Add columns
    op.add_column('existing_table', sa.Column('new_column', sa.String()))
    
    # Create indexes
    op.create_index('ix_table_column', 'table', ['column'])
    
    # Data migrations
    op.execute("UPDATE users SET new_column = 'default_value'")

def downgrade() -> None:
    """Rollback migration changes."""
    # Reverse all operations in opposite order
    op.drop_index('ix_table_column', 'table')
    op.drop_column('existing_table', 'new_column')
    op.drop_table('new_table')
```

## Production Deployment

### Safe Migration Process

1. **Backup Database**
   ```bash
   # Create backup before migrations
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Test Migrations**
   ```bash
   # Test on staging environment first
   python migrate.py upgrade
   python migrate.py validate
   ```

3. **Apply to Production**
   ```bash
   # Apply migrations during maintenance window
   python migrate.py upgrade
   ```

4. **Verify**
   ```bash
   # Check status and run tests
   python migrate.py status
   python migrate.py schema
   ```

### Rollback Plan

If issues occur after migration:

```bash
# Rollback to previous revision
python migrate.py downgrade <previous_revision_id>

# Or restore from backup
psql $DATABASE_URL < backup_file.sql
```

## Environment Configuration

Migrations automatically load database configuration from `.env.production`:

```env
DATABASE_URL=postgresql://user:password@host:port/database
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

## Common Migration Operations

### Adding a New Table

```python
def upgrade() -> None:
    op.create_table('new_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_new_table_id', 'new_table', ['id'])
```

### Adding a Column

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))
```

### Creating an Index

```python
def upgrade() -> None:
    op.create_index('ix_users_email_region', 'users', ['email', 'region'])
```

### Data Migration

```python
def upgrade() -> None:
    # Add column first
    op.add_column('users', sa.Column('full_name', sa.String(200), nullable=True))
    
    # Populate data
    op.execute("""
        UPDATE users 
        SET full_name = CONCAT(first_name, ' ', last_name)
        WHERE first_name IS NOT NULL AND last_name IS NOT NULL
    """)
    
    # Make column not nullable
    op.alter_column('users', 'full_name', nullable=False)
```

## Troubleshooting

### Common Issues

1. **Migration Conflicts**
   ```bash
   # Show conflicting migrations
   python -m alembic branches
   
   # Merge branches
   python -m alembic merge -m "Merge conflicts" head1 head2
   ```

2. **Database Connection Issues**
   ```bash
   # Test connection
   python migrate.py check-db
   
   # Verify environment variables
   python -c "import os; from dotenv import load_dotenv; load_dotenv('.env.production'); print(os.getenv('DATABASE_URL')[:50])"
   ```

3. **Schema Mismatch**
   ```bash
   # Mark current schema as up-to-date
   python -m alembic stamp head
   
   # Or create migration from current state
   python migrate.py create "Sync with current schema"
   ```

## Best Practices

1. **Always Review** generated migrations before applying
2. **Test Locally** before deploying to production
3. **Backup First** before major schema changes
4. **Small Changes** - prefer multiple small migrations over large ones
5. **Descriptive Names** - use clear, descriptive migration messages
6. **Test Rollbacks** - ensure downgrade functions work correctly

## Support

For migration issues:
1. Check logs: `python migrate.py status`
2. Validate migrations: `python migrate.py validate`
3. Review migration files in `migrations/versions/`
4. Test on local database first

## Example Workflow

```bash
# 1. Make model changes in database.py
# 2. Create migration
python migrate.py create "Add user profile fields"

# 3. Review generated migration file
# Edit migrations/versions/xxx_add_user_profile_fields.py if needed

# 4. Test locally
python migrate.py upgrade

# 5. Verify changes
python migrate.py schema

# 6. Deploy to production
# (After testing on staging environment)
python migrate.py upgrade
```

This migration system ensures safe, version-controlled database schema changes for your EcoTrack Ghana application! 🚀
