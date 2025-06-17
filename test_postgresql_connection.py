#!/usr/bin/env python3
"""
Test PostgreSQL database connection for EcoTrack Ghana
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def test_database_connection():
    """Test the PostgreSQL database connection"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔍 Testing database connection...")
    print(f"🔗 Database URL: {DATABASE_URL.split('@')[0]}@***")
    
    try:
        # Create engine
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False
        )
        
        # Test connection
        with engine.connect() as connection:
            # Test basic query
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"✅ Database connection successful!")
            print(f"📊 PostgreSQL version: {version[0]}")
            
            # Test creating a simple table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_message VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert test data
            connection.execute(text("""
                INSERT INTO connection_test (test_message) 
                VALUES ('Connection test successful')
            """))
            
            # Query test data
            result = connection.execute(text("""
                SELECT test_message, created_at 
                FROM connection_test 
                ORDER BY created_at DESC 
                LIMIT 1
            """))
            test_row = result.fetchone()
            print(f"✅ Database write/read test successful!")
            print(f"📝 Test message: {test_row[0]}")
            print(f"🕒 Created at: {test_row[1]}")
            
            # Clean up test table
            connection.execute(text("DROP TABLE IF EXISTS connection_test"))
            connection.commit()
            print("🧹 Cleaned up test data")
            
        print("🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 EcoTrack Ghana - Database Connection Test")
    print("=" * 50)
    
    success = test_database_connection()
    
    if success:
        print("\n✅ Database is ready for production!")
        sys.exit(0)
    else:
        print("\n❌ Database connection issues detected!")
        sys.exit(1)
