#!/usr/bin/env python3
"""
Create demo users for EcoTrack Ghana testing
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime

# Load environment variables
load_dotenv('.env.production')

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    except ImportError:
        # Fallback if passlib is not available
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

def create_demo_users():
    """Create demo users in the database"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        with engine.connect() as conn:
            print("🚀 Creating Demo Users for EcoTrack Ghana")
            print("=" * 50)
            
            # First, ensure users table exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    location VARCHAR(255),
                    region VARCHAR(100),
                    total_points INTEGER DEFAULT 0,
                    weekly_points INTEGER DEFAULT 0,
                    rank INTEGER DEFAULT 0,
                    avatar_url VARCHAR(500),
                    is_active BOOLEAN DEFAULT true,
                    is_admin BOOLEAN DEFAULT false,
                    co2_saved FLOAT DEFAULT 0.0,
                    trees_planted INTEGER DEFAULT 0,
                    waste_collected FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Demo users data
            demo_users = [
                {
                    "email": "admin@ecotrack.gh",
                    "name": "System Admin",
                    "password": "admin123",
                    "location": "Accra, Greater Accra",
                    "region": "Greater Accra",
                    "is_admin": True,
                    "total_points": 2500,
                    "weekly_points": 150
                },
                {
                    "email": "kwame.test@gmail.com",
                    "name": "Kwame Asante",
                    "password": "password123",
                    "location": "Kumasi, Ashanti",
                    "region": "Ashanti",
                    "is_admin": False,
                    "total_points": 1850,
                    "weekly_points": 120
                },
                {
                    "email": "ama.demo@gmail.com",
                    "name": "Ama Osei",
                    "password": "password123",
                    "location": "Cape Coast, Central",
                    "region": "Central",
                    "is_admin": False,
                    "total_points": 2100,
                    "weekly_points": 180
                },
                {
                    "email": "kofi.test@yahoo.com",
                    "name": "Kofi Mensah",
                    "password": "password123",
                    "location": "Tamale, Northern",
                    "region": "Northern",
                    "is_admin": False,
                    "total_points": 1650,
                    "weekly_points": 95
                },
                {
                    "email": "akosua.demo@gmail.com",
                    "name": "Akosua Frimpong",
                    "password": "password123",
                    "location": "Ho, Volta",
                    "region": "Volta",
                    "is_admin": False,
                    "total_points": 1950,
                    "weekly_points": 140
                },
                {
                    "email": "yaw.test@hotmail.com",
                    "name": "Yaw Boakye",
                    "password": "password123",
                    "location": "Sekondi-Takoradi, Western",
                    "region": "Western",
                    "is_admin": False,
                    "total_points": 1420,
                    "weekly_points": 85
                }
            ]
            
            created_count = 0
            updated_count = 0
            
            for user_data in demo_users:
                email = user_data["email"]
                
                # Check if user already exists
                existing = conn.execute(text("""
                    SELECT id FROM users WHERE email = :email
                """), {"email": email}).fetchone()
                
                hashed_password = hash_password(user_data["password"])
                
                if existing:
                    # Update existing user
                    conn.execute(text("""
                        UPDATE users SET 
                            name = :name,
                            hashed_password = :hashed_password,
                            location = :location,
                            region = :region,
                            is_admin = :is_admin,
                            total_points = :total_points,
                            weekly_points = :weekly_points,
                            is_active = true,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE email = :email
                    """), {
                        "email": email,
                        "name": user_data["name"],
                        "hashed_password": hashed_password,
                        "location": user_data["location"],
                        "region": user_data["region"],
                        "is_admin": user_data["is_admin"],
                        "total_points": user_data["total_points"],
                        "weekly_points": user_data["weekly_points"]
                    })
                    print(f"🔄 Updated: {email}")
                    updated_count += 1
                else:
                    # Create new user
                    conn.execute(text("""
                        INSERT INTO users (
                            email, name, hashed_password, location, region, 
                            is_admin, total_points, weekly_points, is_active,
                            created_at, updated_at
                        ) VALUES (
                            :email, :name, :hashed_password, :location, :region,
                            :is_admin, :total_points, :weekly_points, true,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """), {
                        "email": email,
                        "name": user_data["name"],
                        "hashed_password": hashed_password,
                        "location": user_data["location"],
                        "region": user_data["region"],
                        "is_admin": user_data["is_admin"],
                        "total_points": user_data["total_points"],
                        "weekly_points": user_data["weekly_points"]
                    })
                    print(f"✅ Created: {email}")
                    created_count += 1
            
            conn.commit()
            
            print(f"\n📊 Results:")
            print(f"   ✅ Created: {created_count} new users")
            print(f"   🔄 Updated: {updated_count} existing users")
            
            # Verify all users exist and are active
            print(f"\n👥 Verification:")
            for user_data in demo_users:
                result = conn.execute(text("""
                    SELECT name, is_active, is_admin FROM users WHERE email = :email
                """), {"email": user_data["email"]})
                
                user = result.fetchone()
                if user:
                    status = "✅ ACTIVE" if user[1] else "❌ INACTIVE"
                    role = " (ADMIN)" if user[2] else ""
                    print(f"   {status} {user_data['email']} - {user[0]}{role}")
                else:
                    print(f"   ❌ MISSING {user_data['email']}")
            
            print(f"\n🎉 Demo users are ready for testing!")
            print(f"\n🔑 Login Credentials:")
            print(f"   📧 admin@ecotrack.gh (password: admin123) - Admin")
            print(f"   📧 kwame.test@gmail.com (password: password123)")
            print(f"   📧 ama.demo@gmail.com (password: password123)")
            print(f"   📧 kofi.test@yahoo.com (password: password123)")
            print(f"   📧 akosua.demo@gmail.com (password: password123)")
            print(f"   📧 yaw.test@hotmail.com (password: password123)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_demo_users()
    
    if not success:
        print("\n❌ Failed to create demo users!")
        sys.exit(1)
    else:
        print("\n✅ Demo users created successfully!")
        print("You can now log in with any of the demo accounts listed above.")
