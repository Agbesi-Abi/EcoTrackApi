#!/usr/bin/env python3
"""
Quick verification script for PostgreSQL seeding
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('.env.production')

def quick_verify():
    """Quick verification of database seeding"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Check if tables exist
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)).fetchall()
            
            table_names = [row[0] for row in tables]
            print(f"📋 Tables found: {table_names}")
            
            # Quick count queries
            if 'users' in table_names:
                count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                print(f"👥 Users: {count}")
            
            if 'challenges' in table_names:
                count = conn.execute(text("SELECT COUNT(*) FROM challenges")).scalar()
                print(f"🏆 Challenges: {count}")
            
            if 'activities' in table_names:
                count = conn.execute(text("SELECT COUNT(*) FROM activities")).scalar()
                print(f"📝 Activities: {count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Quick Database Verification")
    print("=" * 35)
    quick_verify()
