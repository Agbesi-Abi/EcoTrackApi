#!/usr/bin/env python3
"""
Database migration to add admin columns to existing user table
"""

import sqlite3
import os
from database import DATABASE_URL

def migrate_admin_columns():
    """Add role, permissions, and last_login columns to users table"""
    
    # Extract database path from URL
    db_path = DATABASE_URL.replace("sqlite:///./", "").replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'role' not in columns:
            migrations_needed.append("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            
        if 'permissions' not in columns:
            migrations_needed.append("ALTER TABLE users ADD COLUMN permissions TEXT DEFAULT 'basic'")
            
        if 'last_login' not in columns:
            migrations_needed.append("ALTER TABLE users ADD COLUMN last_login DATETIME")
        
        if not migrations_needed:
            print("✅ All admin columns already exist")
            return True
            
        # Apply migrations
        for migration in migrations_needed:
            print(f"🔧 Running: {migration}")
            cursor.execute(migration)
            
        # Set default super admin role for first user (if any)
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            cursor.execute("SELECT id FROM users ORDER BY id LIMIT 1")
            first_user_id = cursor.fetchone()[0]
            
            cursor.execute(
                "UPDATE users SET role = 'super_admin', permissions = 'full' WHERE id = ?",
                (first_user_id,)
            )
            print(f"✅ Set first user (ID: {first_user_id}) as super admin")
        
        conn.commit()
        print("✅ Database migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Running Admin Columns Migration")
    print("=" * 50)
    migrate_admin_columns()
