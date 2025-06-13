"""
Seed script to populate EcoTrack Ghana database with initial data
"""

import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()
from database import SessionLocal, Challenge, User, init_db
from auth.utils import get_password_hash
from datetime import datetime, timedelta

def create_sample_challenges(db: Session):
    """Create sample challenges matching the React Native app"""
    
    challenges_data = [
        {
            "title": "No Plastic Wednesday",
            "description": "Avoid single-use plastics for the entire day. Use reusable bags and containers instead of plastic ones.",
            "category": "trash",
            "duration": "1 day",
            "points": 50,
            "difficulty": "easy",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "title": "Plant a Tree Challenge",
            "description": "Plant a native tree in your community. Document with photos and location for verification.",
            "category": "trees",
            "duration": "1 week",
            "points": 150,
            "difficulty": "medium",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=60)
        },
        {
            "title": "Carpool to Work Week",
            "description": "Share rides with colleagues or use public transport for a full week instead of driving alone.",
            "category": "mobility",
            "duration": "7 days",
            "points": 120,
            "difficulty": "medium",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=45)
        },
        {
            "title": "Beach Cleanup Marathon",
            "description": "Organize or join a beach cleanup in Accra, Cape Coast, or Elmina. Collect at least 5 bags of waste.",
            "category": "trash",
            "duration": "1 day",
            "points": 200,
            "difficulty": "hard",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "title": "Plastic-Free Shopping Month",
            "description": "Shop without using any plastic bags or containers for an entire month. Use cloth bags and glass containers.",
            "category": "trash",
            "duration": "30 days",
            "points": 300,
            "difficulty": "hard",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=90)
        },
        {
            "title": "Urban Garden Starter",
            "description": "Start a small urban garden with at least 3 different plants. Perfect for apartments and small spaces.",
            "category": "trees",
            "duration": "2 weeks",
            "points": 100,
            "difficulty": "easy",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=60)
        },
        {
            "title": "Walk to Work Week",
            "description": "Walk or cycle to work for 5 consecutive working days. Track your distance and CO2 savings.",
            "category": "mobility",
            "duration": "5 days",
            "points": 80,
            "difficulty": "easy",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "title": "Community Forest Initiative",
            "description": "Plant 10 trees in your community with friends or local groups. Organize a tree planting event.",
            "category": "trees",
            "duration": "1 month",
            "points": 500,
            "difficulty": "hard",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=120)
        },
        {
            "title": "Zero Waste Day",
            "description": "Spend an entire day producing zero waste. Reuse, recycle, and avoid all disposable items.",
            "category": "trash",
            "duration": "1 day",
            "points": 75,
            "difficulty": "medium",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "title": "Public Transport Champion",
            "description": "Use only public transportation for two weeks. Share your experience and encourage others.",
            "category": "mobility",
            "duration": "14 days",
            "points": 180,
            "difficulty": "medium",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=45)
        }
    ]
    
    for challenge_data in challenges_data:
        # Check if challenge already exists
        existing = db.query(Challenge).filter(Challenge.title == challenge_data["title"]).first()
        if not existing:
            challenge = Challenge(**challenge_data)
            db.add(challenge)
    
    db.commit()
    print(f"✅ Created {len(challenges_data)} sample challenges")

def create_demo_users(db: Session):
    """Create demo users for testing"""
    
    demo_users_data = [
        {
            "name": "Demo User",
            "email": "demo@ecotrack.com",
            "password": "demo123456",
            "location": "Accra, Ghana",
            "region": "Greater Accra",
            "total_points": 1250,
            "weekly_points": 125,
            "trees_planted": 5,
            "trash_collected": 15.5,
            "co2_saved": 45.3
        },
        {
            "name": "Eco Champion",
            "email": "eco@ghana.com",
            "password": "ecotrack123",
            "location": "Kumasi, Ghana",
            "region": "Ashanti",
            "total_points": 2380,
            "weekly_points": 245,
            "trees_planted": 12,
            "trash_collected": 28.7,
            "co2_saved": 89.2
        },
        {
            "name": "Test User",
            "email": "test@ecotrack.com",
            "password": "password123",
            "location": "Cape Coast, Ghana",
            "region": "Central",
            "total_points": 890,
            "weekly_points": 75,
            "trees_planted": 3,
            "trash_collected": 12.1,
            "co2_saved": 34.8
        },
        {
            "name": "Kwame Asante",
            "email": "kwame.asante@ecotrack.com",
            "password": "kwame123",
            "location": "Tamale, Ghana",
            "region": "Northern",
            "total_points": 3450,
            "weekly_points": 320,
            "trees_planted": 18,
            "trash_collected": 42.3,
            "co2_saved": 156.7,
            "is_verified": True
        },
        {
            "name": "Ama Osei",
            "email": "ama.osei@ecotrack.com",
            "password": "ama123",
            "location": "Sekondi-Takoradi, Ghana",
            "region": "Western",
            "total_points": 2850,
            "weekly_points": 280,
            "trees_planted": 15,
            "trash_collected": 35.8,
            "co2_saved": 112.4,
            "is_verified": True
        }
    ]
    
    for user_data in demo_users_data:
        # Check if user already exists
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            password = user_data.pop("password")
            hashed_password = get_password_hash(password)
            
            user = User(
                hashed_password=hashed_password,
                **user_data
            )
            db.add(user)
    
    db.commit()
    print(f"✅ Created {len(demo_users_data)} demo users")

def seed_database():
    """Main seeding function"""
    print("🌱 Seeding EcoTrack Ghana database...")
    
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed challenges
        create_sample_challenges(db)
        
        # Seed demo users
        create_demo_users(db)
        
        print("🎉 Database seeding completed successfully!")
        print("\n📋 Demo Accounts Created:")
        print("1. demo@ecotrack.com / demo123456")
        print("2. eco@ghana.com / ecotrack123")
        print("3. test@ecotrack.com / password123")
        print("4. kwame.asante@ecotrack.com / kwame123")
        print("5. ama.osei@ecotrack.com / ama123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
