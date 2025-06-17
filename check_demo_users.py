#!/usr/bin/env python3
"""
Check if demo users exist in the database
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('.env.production')

def check_demo_users():
    """Check if demo users exist in database"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        with engine.connect() as conn:
            print("🔍 Checking Demo User Accounts")
            print("=" * 40)
            
            # Check if users table exists
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'users'
            """)).fetchall()
            
            if not tables:
                print("❌ Users table does not exist!")
                return False
            
            # Check for demo users
            demo_emails = [
                'admin@ecotrack.gh',
                'kwame.test@gmail.com',
                'ama.demo@gmail.com',
                'kofi.test@yahoo.com',
                'akosua.demo@gmail.com',
                'yaw.test@hotmail.com'
            ]
            
            print("👥 Demo User Status:")
            total_users = 0
            demo_users_found = 0
            
            for email in demo_emails:
                result = conn.execute(text("""
                    SELECT email, name, is_active, is_admin 
                    FROM users 
                    WHERE email = :email
                """), {"email": email})
                
                user = result.fetchone()
                if user:
                    admin_status = " (ADMIN)" if user[3] else ""
                    active_status = "✅" if user[2] else "❌"
                    print(f"  {active_status} {user[0]} - {user[1]}{admin_status}")
                    demo_users_found += 1
                else:
                    print(f"  ❌ {email} - NOT FOUND")
            
            # Check total users
            total_result = conn.execute(text("SELECT COUNT(*) FROM users"))
            total_users = total_result.scalar()
            
            print(f"\n📊 Summary:")
            print(f"   Total users in database: {total_users}")
            print(f"   Demo users found: {demo_users_found}/{len(demo_emails)}")
            
            if demo_users_found == 0:
                print("\n🚨 No demo users found! Database needs seeding.")
                return False
            elif demo_users_found < len(demo_emails):
                print(f"\n⚠️  Only {demo_users_found} demo users found. Some are missing.")
                return False
            else:
                print("\n✅ All demo users are present!")
                return True
                
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return False

if __name__ == "__main__":
    check_demo_users()
