#!/usr/bin/env python3
"""
Database Migration Management for EcoTrack Ghana
Provides convenient commands for managing database migrations
"""

import os
import sys
import subprocess
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('.env.production')

class MigrationManager:
    """Database migration management utilities"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.base_dir)
    
    def run_alembic_command(self, command: str):
        """Run an alembic command and return the result"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "alembic"] + command.split(),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout, result.stderr, True
        except subprocess.CalledProcessError as e:
            return e.stdout, e.stderr, False
    
    def check_database_connection(self):
        """Check if database connection is working"""
        print("🔍 Checking database connection...")
        try:
            from database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def current_revision(self):
        """Show current migration revision"""
        print("📋 Current Migration Status:")
        print("=" * 40)
        
        stdout, stderr, success = self.run_alembic_command("current")
        if success:
            if stdout.strip():
                print(f"Current revision: {stdout.strip()}")
            else:
                print("No current revision (database not initialized)")
        else:
            print(f"Error: {stderr}")
        
        # Show migration history
        stdout, stderr, success = self.run_alembic_command("history")
        if success and stdout.strip():
            print(f"\nMigration History:")
            print(stdout)
    
    def create_migration(self, message: str, autogenerate: bool = True):
        """Create a new migration"""
        if not message:
            message = f"Migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"📝 Creating migration: {message}")
        
        if autogenerate:
            command = f"revision --autogenerate -m \"{message}\""
        else:
            command = f"revision -m \"{message}\""
        
        stdout, stderr, success = self.run_alembic_command(command)
        
        if success:
            print("✅ Migration created successfully!")
            print(stdout)
        else:
            print(f"❌ Failed to create migration: {stderr}")
    
    def upgrade_database(self, revision: str = "head"):
        """Apply migrations to database"""
        print(f"⬆️  Upgrading database to revision: {revision}")
        
        stdout, stderr, success = self.run_alembic_command(f"upgrade {revision}")
        
        if success:
            print("✅ Database upgrade successful!")
            print(stdout)
        else:
            print(f"❌ Database upgrade failed: {stderr}")
    
    def downgrade_database(self, revision: str):
        """Downgrade database to a specific revision"""
        print(f"⬇️  Downgrading database to revision: {revision}")
        
        stdout, stderr, success = self.run_alembic_command(f"downgrade {revision}")
        
        if success:
            print("✅ Database downgrade successful!")
            print(stdout)
        else:
            print(f"❌ Database downgrade failed: {stderr}")
    
    def show_pending_migrations(self):
        """Show pending migrations that haven't been applied"""
        print("⏳ Checking for pending migrations...")
        
        # Get current revision
        stdout, stderr, success = self.run_alembic_command("current")
        current = stdout.strip() if success else ""
        
        # Get head revision
        stdout, stderr, success = self.run_alembic_command("heads")
        head = stdout.strip() if success else ""
        
        if current == head:
            print("✅ Database is up to date!")
        else:
            print(f"📋 Current revision: {current or 'None'}")
            print(f"📋 Latest revision: {head}")
            print("⚠️  Database needs to be upgraded!")
    
    def validate_migrations(self):
        """Validate migration files and database state"""
        print("🔍 Validating migrations...")
        
        # Check if migration files are valid
        stdout, stderr, success = self.run_alembic_command("check")
        
        if success:
            print("✅ All migrations are valid!")
        else:
            print(f"❌ Migration validation failed: {stderr}")
    
    def reset_database(self):
        """Reset database to clean state (WARNING: Destroys all data)"""
        response = input("⚠️  WARNING: This will destroy all data! Type 'RESET' to confirm: ")
        if response != "RESET":
            print("❌ Reset cancelled.")
            return
        
        print("🗑️  Resetting database...")
        
        # Downgrade to base
        self.downgrade_database("base")
        
        # Upgrade to head
        self.upgrade_database("head")
        
        print("✅ Database reset complete!")
    
    def seed_initial_data(self):
        """Seed database with initial Ghana regions data"""
        print("🌱 Seeding initial data...")
        
        try:
            from database import init_db
            init_db()
            print("✅ Initial data seeded successfully!")
        except Exception as e:
            print(f"❌ Failed to seed initial data: {e}")
    
    def show_schema_info(self):
        """Show current database schema information"""
        print("📊 Database Schema Information:")
        print("=" * 40)
        
        try:
            from database import engine
            from sqlalchemy import inspect
            
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"📋 Tables ({len(tables)}):")
            for table in sorted(tables):
                columns = inspector.get_columns(table)
                print(f"  • {table} ({len(columns)} columns)")
                for col in columns[:3]:  # Show first 3 columns
                    print(f"    - {col['name']} ({col['type']})")
                if len(columns) > 3:
                    print(f"    ... and {len(columns) - 3} more columns")
                
        except Exception as e:
            print(f"❌ Failed to get schema info: {e}")


def main():
    """Main CLI interface for migration management"""
    manager = MigrationManager()
    
    if len(sys.argv) < 2:
        print("🗄️  EcoTrack Ghana - Database Migration Manager")
        print("=" * 50)
        print("Available commands:")
        print("  status           - Show current migration status")
        print("  create <message> - Create new migration")
        print("  upgrade          - Apply all pending migrations")
        print("  downgrade <rev>  - Downgrade to specific revision")
        print("  pending          - Show pending migrations")
        print("  validate         - Validate migration files")
        print("  reset            - Reset database (destroys all data)")
        print("  seed             - Seed initial data")
        print("  schema           - Show database schema info")
        print("  check-db         - Check database connection")
        print("\nExample usage:")
        print("  python migrate.py status")
        print("  python migrate.py create 'Add user preferences table'")
        print("  python migrate.py upgrade")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        manager.current_revision()
    
    elif command == "create":
        message = sys.argv[2] if len(sys.argv) > 2 else ""
        manager.create_migration(message)
    
    elif command == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        manager.upgrade_database(revision)
    
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("❌ Please specify revision to downgrade to")
            return
        manager.downgrade_database(sys.argv[2])
    
    elif command == "pending":
        manager.show_pending_migrations()
    
    elif command == "validate":
        manager.validate_migrations()
    
    elif command == "reset":
        manager.reset_database()
    
    elif command == "seed":
        manager.seed_initial_data()
    
    elif command == "schema":
        manager.show_schema_info()
    
    elif command == "check-db":
        manager.check_database_connection()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python migrate.py' for help")


if __name__ == "__main__":
    main()
