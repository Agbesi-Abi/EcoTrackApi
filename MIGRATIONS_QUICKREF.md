# 🗄️ EcoTrack Ghana - Database Migrations Quick Reference

## Quick Commands

```bash
# Check Status
python migrate.py status              # Show current migration state
python migrate.py pending             # Show pending migrations  
python migrate.py check-db             # Test database connection

# Apply Migrations
python migrate.py upgrade             # Apply all pending migrations
python migrate.py upgrade abc123      # Apply up to specific revision

# Create New Migration
python migrate.py create "Add user preferences"  # Auto-generate migration
python -m alembic revision -m "Manual changes"   # Create empty migration

# Rollback
python migrate.py downgrade abc123    # Rollback to specific revision
python migrate.py downgrade -1        # Rollback one migration

# Utilities
python migrate.py schema              # Show database schema
python migrate.py validate            # Validate migration files
python migrate.py seed                # Seed initial data
```

## PowerShell Shortcuts

```powershell
.\db-migrate.ps1 status               # Check migration status
.\db-migrate.ps1 create "Add table"   # Create new migration
.\db-migrate.ps1 upgrade              # Apply migrations
.\db-migrate.ps1 check-db              # Test connection
```

## Migration Files Created

### 📁 Core Migrations
- **001_initial_schema.py** - All core EcoTrack tables
- **002_user_preferences.py** - User settings and preferences  
- **003_activity_improvements.py** - Activity categories and indexing

### 📁 Management Files
- **migrate.py** - Python migration manager
- **db-migrate.ps1** - PowerShell migration wrapper
- **MIGRATIONS_GUIDE.md** - Complete documentation

## Production Workflow

```bash
# 1. Create Migration
python migrate.py create "Your change description"

# 2. Review Generated File
# Edit migrations/versions/xxx_your_change.py

# 3. Test Locally
python migrate.py upgrade
python migrate.py validate

# 4. Deploy to Production
python migrate.py upgrade
```

## Environment Setup

The migration system automatically:
- ✅ Loads `.env.production` for database URL
- ✅ Imports all models from `database.py`
- ✅ Configures PostgreSQL connection
- ✅ Handles SSL and connection pooling

## Common Operations

### Add New Table
```python
def upgrade():
    op.create_table('new_table',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False)
    )
```

### Add Column
```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20)))
```

### Create Index
```python
def upgrade():
    op.create_index('ix_users_email', 'users', ['email'])
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection Error | `python migrate.py check-db` |
| Migration Conflicts | `python -m alembic merge heads` |
| Schema Mismatch | `python -m alembic stamp head` |
| Validation Errors | `python migrate.py validate` |

## 🚀 Ready to Use!

Your PostgreSQL database now has a complete migration system:
- ✅ Version-controlled schema changes
- ✅ Safe production deployments  
- ✅ Easy rollback capabilities
- ✅ Automated management tools

Start creating migrations with: `python migrate.py create "Your first change"`
