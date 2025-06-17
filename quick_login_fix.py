#!/usr/bin/env python3
"""
Quick fix for login issues - seed database if needed
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def quick_fix():
    """Quick fix for login issues"""
    print("🔧 Quick Login Fix")
    print("=" * 30)
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from database import User, Base, engine
        from auth.utils import get_password_hash
        
        print("1. Testing database connection...")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ Database connected")
        
        # Create tables if needed
        Base.metadata.create_all(bind=engine)
        print("   ✅ Tables ensured")
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check for users
        user_count = session.query(User).count()
        print(f"   📊 Found {user_count} users")
        
        # Create demo user if none exist
        demo_user = session.query(User).filter(User.email == "demo@mail.com").first()
        if not demo_user:
            print("   🆕 Creating demo user...")
            demo_user = User(
                email="demo@mail.com",
                name="Demo User",
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                is_verified=True,
                role="user"
            )
            session.add(demo_user)
            session.commit()
            print("   ✅ Demo user created")
        else:
            print("   ✅ Demo user exists")
        
        # Create admin user if none exist
        admin_user = session.query(User).filter(User.email == "admin@ecotrack.gh").first()
        if not admin_user:
            print("   🆕 Creating admin user...")
            admin_user = User(
                email="admin@ecotrack.gh",
                name="Admin User",
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                is_verified=True,
                role="admin"
            )
            session.add(admin_user)
            session.commit()
            print("   ✅ Admin user created")
        else:
            print("   ✅ Admin user exists")
        
        session.close()
        
        print("\n✅ Database is ready!")
        print("You can now login with:")
        print("- demo@mail.com / demo123")
        print("- admin@ecotrack.gh / demo123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if PostgreSQL database is accessible")
        print("2. Verify DATABASE_URL in .env.production")
        print("3. Ensure database credentials are correct")
        return False

if __name__ == "__main__":
    quick_fix()
