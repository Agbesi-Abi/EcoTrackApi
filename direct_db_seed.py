#!/usr/bin/env python3
"""
Direct PostgreSQL check and seeding for EcoTrack Ghana
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('.env.production')

def check_and_seed():
    """Check database connection and seed if needed"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print("🌍 EcoTrack Ghana - Direct Database Check & Seed")
    print("=" * 55)
    print(f"🔗 Connecting to: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'Unknown'}")
    
    try:
        # Create engine
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True
        )
        
        with engine.connect() as connection:
            print("✅ Database connection successful!")
            
            # Check what tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Existing tables: {tables}")
            
            if not tables:
                print("🚨 No tables found! Creating schema...")
                create_schema(connection)
            
            # Check data in tables
            for table in ['users', 'regions', 'challenges', 'activities']:
                if table in tables:
                    count = connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"📊 {table}: {count} records")
                    
                    if count == 0 and table == 'regions':
                        print(f"🌱 Seeding {table}...")
                        seed_regions(connection)
                    elif count == 0 and table == 'users':
                        print(f"👥 Seeding {table}...")
                        seed_users(connection)
                    elif count == 0 and table == 'challenges':
                        print(f"🏆 Seeding {table}...")
                        seed_challenges(connection)
            
            connection.commit()
            
        print("🎉 Database check and seeding completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def create_schema(connection):
    """Create basic database schema"""
    print("📋 Creating database schema...")
    
    # Create regions table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS regions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            capital VARCHAR(100) NOT NULL,
            code VARCHAR(10) NOT NULL UNIQUE,
            population INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Create users table
    connection.execute(text("""
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
    
    # Create challenges table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS challenges (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            duration VARCHAR(50),
            points INTEGER DEFAULT 0,
            difficulty VARCHAR(20) DEFAULT 'easy',
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Create activities table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            type VARCHAR(50) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            points INTEGER DEFAULT 0,
            location VARCHAR(255),
            region VARCHAR(100),
            photos TEXT[] DEFAULT '{}',
            verified BOOLEAN DEFAULT false,
            impact_data JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    print("✅ Database schema created!")

def seed_regions(connection):
    """Seed Ghana regions"""
    regions_data = [
        ("Greater Accra", "Accra", "GA", 5455692),
        ("Ashanti", "Kumasi", "AS", 5440463),
        ("Western", "Sekondi-Takoradi", "WP", 2060585),
        ("Central", "Cape Coast", "CP", 2859821),
        ("Eastern", "Koforidua", "EP", 2106696),
        ("Volta", "Ho", "TV", 1635421),
        ("Northern", "Tamale", "NP", 1972757),
        ("Upper East", "Bolgatanga", "UE", 920089),
        ("Upper West", "Wa", "UW", 576583),
        ("Brong Ahafo", "Sunyani", "BA", 1815408),
        ("Western North", "Sefwi Wiawso", "WN", 678555),
        ("Ahafo", "Goaso", "AH", 563677),
        ("Bono", "Sunyani", "BO", 691983),
        ("Bono East", "Techiman", "BE", 1208649),
        ("Oti", "Dambai", "OT", 563677),
        ("North East", "Nalerigu", "NE", 466026),
        ("Savannah", "Damongo", "SV", 685801)
    ]
    
    for name, capital, code, population in regions_data:
        connection.execute(text("""
            INSERT INTO regions (name, capital, code, population) 
            VALUES (:name, :capital, :code, :population)
            ON CONFLICT (name) DO NOTHING
        """), {"name": name, "capital": capital, "code": code, "population": population})
    
    print("✅ Regions seeded!")

def seed_users(connection):
    """Seed test users"""
    from auth.utils import get_password_hash
    
    users_data = [
        ("admin@ecotrack.gh", "System Admin", "admin123", "Accra, Greater Accra", "Greater Accra", True, 2500, 150),
        ("kwame.test@gmail.com", "Kwame Asante", "password123", "Kumasi, Ashanti", "Ashanti", False, 1850, 120),
        ("ama.demo@gmail.com", "Ama Osei", "password123", "Cape Coast, Central", "Central", False, 2100, 180),
        ("kofi.test@yahoo.com", "Kofi Mensah", "password123", "Tamale, Northern", "Northern", False, 1650, 95),
    ]
    
    for email, name, password, location, region, is_admin, total_points, weekly_points in users_data:
        hashed_password = get_password_hash(password)
        connection.execute(text("""
            INSERT INTO users (email, name, hashed_password, location, region, is_admin, total_points, weekly_points)
            VALUES (:email, :name, :hashed_password, :location, :region, :is_admin, :total_points, :weekly_points)
            ON CONFLICT (email) DO NOTHING
        """), {
            "email": email, "name": name, "hashed_password": hashed_password,
            "location": location, "region": region, "is_admin": is_admin,
            "total_points": total_points, "weekly_points": weekly_points
        })
    
    print("✅ Test users seeded!")

def seed_challenges(connection):
    """Seed sample challenges"""
    from datetime import datetime, timedelta
    
    challenges_data = [
        ("No Plastic Wednesday", "Avoid single-use plastics for the entire day", "trash", "1 day", 50, "easy"),
        ("Plant a Tree Challenge", "Plant a native tree in your community", "trees", "1 week", 150, "medium"),
        ("Carpool to Work Week", "Share rides with colleagues for a week", "mobility", "7 days", 120, "medium"),
        ("Beach Cleanup Marathon", "Join a beach cleanup event", "trash", "1 day", 200, "hard"),
    ]
    
    for title, description, category, duration, points, difficulty in challenges_data:
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        connection.execute(text("""
            INSERT INTO challenges (title, description, category, duration, points, difficulty, start_date, end_date, is_active)
            VALUES (:title, :description, :category, :duration, :points, :difficulty, :start_date, :end_date, :is_active)
        """), {
            "title": title, "description": description, "category": category,
            "duration": duration, "points": points, "difficulty": difficulty,
            "start_date": start_date, "end_date": end_date, "is_active": True
        })
    
    print("✅ Challenges seeded!")

if __name__ == "__main__":
    # Add current directory to path for imports
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    success = check_and_seed()
    
    if success:
        print("\n🎉 Database is ready with demo data!")
        print("\n👤 Test Accounts:")
        print("📧 admin@ecotrack.gh (password: admin123)")
        print("📧 kwame.test@gmail.com (password: password123)")
        print("📧 ama.demo@gmail.com (password: password123)")
        print("📧 kofi.test@yahoo.com (password: password123)")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
