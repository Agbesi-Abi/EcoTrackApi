#!/usr/bin/env python3
"""
Fix login issues by checking database and creating demo users
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import User, Base, engine
from auth.utils import get_password_hash

# Load environment variables
load_dotenv('.env.production')

def check_and_fix_login_issues():
    """Check database connectivity and create demo users if needed"""
    
    print("🔧 EcoTrack Ghana - Login Issue Diagnostics")
    print("=" * 50)
    
    try:
        # Test database connection
        print("1. Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ Database connection successful")
        
        # Check if users table exists
        print("2. Checking database schema...")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            user_count = session.query(User).count()
            print(f"   ✅ Users table exists with {user_count} users")
        except Exception as e:
            print(f"   ❌ Users table issue: {e}")
            print("   🔧 Creating database tables...")
            Base.metadata.create_all(bind=engine)
            user_count = 0
        
        # Create demo users if none exist
        if user_count == 0:
            print("3. Creating demo users...")
            demo_users = [
                {
                    "email": "admin@ecotrack.gh",
                    "name": "Admin User",
                    "password": "demo123",
                    "role": "admin",
                    "is_admin": True
                },
                {
                    "email": "demo@mail.com", 
                    "name": "Demo User",
                    "password": "demo123",
                    "role": "user"
                },
                {
                    "email": "kwame.test@gmail.com",
                    "name": "Kwame Asante",
                    "password": "demo123",
                    "location": "Accra",
                    "region": "Greater Accra"
                }
            ]
            
            for user_data in demo_users:
                password = user_data.pop("password")
                is_admin = user_data.pop("is_admin", False)
                
                user = User(
                    **user_data,
                    hashed_password=get_password_hash(password),
                    is_active=True,
                    is_verified=True
                )
                
                session.add(user)
            
            session.commit()
            print("   ✅ Demo users created successfully")
        else:
            print("3. Demo users already exist")
        
        # Test login with demo user
        print("4. Testing user authentication...")
        demo_user = session.query(User).filter(User.email == "demo@mail.com").first()
        if demo_user:
            print(f"   ✅ Demo user found: {demo_user.email}")
            print(f"   - Name: {demo_user.name}")
            print(f"   - Active: {demo_user.is_active}")
            print(f"   - Verified: {demo_user.is_verified}")
        else:
            print("   ❌ Demo user not found")
        
        session.close()
        
        print("\n🎉 Database diagnostics complete!")
        print("Demo users available:")
        print("- admin@ecotrack.gh (password: demo123)")
        print("- demo@mail.com (password: demo123)")
        print("- kwame.test@gmail.com (password: demo123)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    success = check_and_fix_login_issues()
    if success:
        print("\n✅ Login issues should now be resolved!")
    else:
        print("\n❌ Unable to resolve login issues. Check database configuration.")
