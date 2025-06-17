#!/usr/bin/env python3
"""
Quick PostgreSQL database health check for EcoTrack Ghana
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('.env.production')

def quick_health_check():
    """Perform a quick database health check"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        # Create engine with minimal configuration
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as connection:
            # Simple health check query
            result = connection.execute(text("SELECT 1 as health_check"))
            health = result.scalar()
            
            if health == 1:
                print("✅ Database connection: HEALTHY")
                
                # Check if main tables exist
                tables_check = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """))
                
                tables = [row[0] for row in tables_check.fetchall()]
                print(f"📋 Tables found: {len(tables)}")
                
                expected_tables = ['users', 'regions', 'activities', 'challenges', 'notifications']
                missing_tables = [t for t in expected_tables if t not in tables]
                
                if missing_tables:
                    print(f"⚠️  Missing tables: {missing_tables}")
                else:
                    print("✅ All expected tables present")
                
                return True
            else:
                print("❌ Database health check failed")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏥 EcoTrack Ghana - Database Health Check")
    print("=" * 45)
    
    is_healthy = quick_health_check()
    
    if is_healthy:
        print("🎉 Database is ready!")
        sys.exit(0)
    else:
        print("💊 Database needs attention!")
        sys.exit(1)
