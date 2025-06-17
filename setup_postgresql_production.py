#!/usr/bin/env python3
"""
Initialize PostgreSQL database schema for EcoTrack Ghana
This script creates all necessary tables and seeds initial data
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, engine, SessionLocal, Base
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_production_database():
    """Initialize the production PostgreSQL database"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL not found in environment variables")
        return False
    
    if not DATABASE_URL.startswith("postgresql"):
        logger.error("❌ DATABASE_URL is not a PostgreSQL connection string")
        return False
    
    logger.info("🚀 Initializing EcoTrack Ghana Production Database")
    logger.info("=" * 60)
    
    try:
        # Test connection first
        logger.info("🔍 Testing database connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            logger.info(f"✅ Connected to PostgreSQL: {version[0]}")
        
        # Create all tables
        logger.info("📋 Creating database schema...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database schema created successfully")
        
        # Initialize database with seed data
        logger.info("🌱 Seeding initial data...")
        init_db()
        logger.info("✅ Database initialization completed")
        
        # Verify tables were created
        logger.info("🔍 Verifying database setup...")
        db = SessionLocal()
        try:
            # Check if tables exist by querying them
            tables_to_check = [
                ("users", "SELECT COUNT(*) FROM users"),
                ("regions", "SELECT COUNT(*) FROM regions"),
                ("activities", "SELECT COUNT(*) FROM activities"),
                ("challenges", "SELECT COUNT(*) FROM challenges"),
                ("notifications", "SELECT COUNT(*) FROM notifications")
            ]
            
            for table_name, query in tables_to_check:
                try:
                    result = db.execute(text(query))
                    count = result.scalar()
                    logger.info(f"✅ Table '{table_name}': {count} records")
                except Exception as e:
                    logger.warning(f"⚠️  Table '{table_name}': {str(e)}")
            
        finally:
            db.close()
        
        logger.info("🎉 Database setup completed successfully!")
        logger.info("🔗 Your EcoTrack Ghana API is ready to use with PostgreSQL")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return False

def show_database_info():
    """Show database connection information"""
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    # Parse database URL safely
    if DATABASE_URL.startswith("postgresql://"):
        # Extract host from URL
        url_parts = DATABASE_URL.replace("postgresql://", "").split("@")
        if len(url_parts) > 1:
            host_part = url_parts[1].split("/")[0]
            database_name = url_parts[1].split("/")[1].split("?")[0]
            
            logger.info("📊 Database Information:")
            logger.info(f"   Host: {host_part}")
            logger.info(f"   Database: {database_name}")
            logger.info(f"   SSL Mode: Required")
            logger.info(f"   Pool Size: {os.getenv('DB_POOL_SIZE', '10')}")
            logger.info(f"   Max Overflow: {os.getenv('DB_MAX_OVERFLOW', '20')}")

if __name__ == "__main__":
    print("\n🌍 EcoTrack Ghana - Production Database Setup")
    print("=" * 60)
    
    show_database_info()
    print("")
    
    success = initialize_production_database()
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("🚀 Your EcoTrack Ghana API is ready for production!")
        sys.exit(0)
    else:
        print("\n❌ Database setup failed!")
        print("🔧 Please check your database credentials and try again.")
        sys.exit(1)
