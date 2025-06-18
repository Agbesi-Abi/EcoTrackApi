#!/usr/bin/env python3
"""
Seed database with 10 challenges for EcoTrack Ghana
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the current directory to the path so we can import database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, Challenge, engine, Base

def create_challenge_seeds():
    """Create 10 diverse challenges for the EcoTrack Ghana platform"""
    
    # Calculate dates
    now = datetime.now()
    start_date_1 = now + timedelta(days=1)  # Start tomorrow
    start_date_2 = now + timedelta(days=7)  # Start next week
    start_date_3 = now + timedelta(days=14) # Start in 2 weeks
    
    challenges = [
        # Trash Collection Challenges
        {
            "title": "Beach Cleanup Marathon",
            "description": "Join our coastal cleanup initiative! Collect at least 10kg of trash from Ghana's beautiful beaches. Help protect marine life and keep our shores pristine for future generations.",
            "category": "trash",
            "duration": "1 week",
            "points": 100,
            "difficulty": "medium",
            "is_active": True,
            "start_date": start_date_1,
            "end_date": start_date_1 + timedelta(days=7)
        },
        {
            "title": "Community Cleanup Hero",
            "description": "Become a cleanup champion in your neighborhood! Organize or participate in 3 community cleanup events. Document your efforts and inspire others to join the movement.",
            "category": "trash",
            "duration": "2 weeks",
            "points": 150,
            "difficulty": "hard",
            "is_active": True,
            "start_date": start_date_2,
            "end_date": start_date_2 + timedelta(days=14)
        },
        {
            "title": "Zero Waste Weekend",
            "description": "Challenge yourself to produce minimal waste for an entire weekend. Learn about waste reduction, proper sorting, and sustainable living practices.",
            "category": "trash",
            "duration": "3 days",
            "points": 75,
            "difficulty": "easy",
            "is_active": True,
            "start_date": start_date_1,
            "end_date": start_date_1 + timedelta(days=3)
        },
        
        # Tree Planting Challenges
        {
            "title": "Green Ghana Forest Initiative",
            "description": "Plant 5 trees in your community or participate in local reforestation projects. Help combat deforestation and contribute to Ghana's green cover restoration.",
            "category": "trees",
            "duration": "1 month",
            "points": 200,
            "difficulty": "medium",
            "is_active": True,
            "start_date": start_date_1,
            "end_date": start_date_1 + timedelta(days=30)
        },
        {
            "title": "School Garden Champion",
            "description": "Start or maintain a garden at your school or local educational institution. Plant vegetables, herbs, or flowers and share your knowledge with students.",
            "category": "trees",
            "duration": "2 weeks",
            "points": 120,
            "difficulty": "easy",
            "is_active": True,
            "start_date": start_date_2,
            "end_date": start_date_2 + timedelta(days=14)
        },
        {
            "title": "Urban Forest Creator",
            "description": "Transform urban spaces by planting 10 trees or creating small green spaces in cities. Focus on native species that can thrive in urban environments.",
            "category": "trees",
            "duration": "3 weeks",
            "points": 250,
            "difficulty": "hard",
            "is_active": True,
            "start_date": start_date_3,
            "end_date": start_date_3 + timedelta(days=21)
        },
        
        # Sustainable Mobility Challenges
        {
            "title": "Car-Free Week Challenge",
            "description": "Go car-free for 5 consecutive days! Use walking, cycling, public transport, or carpooling. Track your carbon footprint reduction and promote sustainable transportation.",
            "category": "mobility",
            "duration": "1 week",
            "points": 80,
            "difficulty": "medium",
            "is_active": True,
            "start_date": start_date_1,
            "end_date": start_date_1 + timedelta(days=7)
        },
        {
            "title": "Cycling Adventure Ghana",
            "description": "Cycle at least 50km over the challenge period while exploring Ghana's beautiful landscapes. Promote cycling as a healthy and eco-friendly transport option.",
            "category": "mobility",
            "duration": "2 weeks",
            "points": 90,
            "difficulty": "easy",
            "is_active": True,
            "start_date": start_date_2,
            "end_date": start_date_2 + timedelta(days=14)
        },
        
        # Water Conservation Challenges
        {
            "title": "Water Warrior Challenge",
            "description": "Implement 5 water conservation practices in your daily routine. Install water-saving devices, fix leaks, and educate others about water conservation.",
            "category": "water",
            "duration": "2 weeks",
            "points": 110,
            "difficulty": "medium",
            "is_active": True,
            "start_date": start_date_1,
            "end_date": start_date_1 + timedelta(days=14)
        },
        
        # Energy Conservation Challenges
        {
            "title": "Solar Energy Pioneer",
            "description": "Promote renewable energy in your community! Install solar lights, educate neighbors about solar power, or organize solar energy awareness events.",
            "category": "energy",
            "duration": "3 weeks",
            "points": 180,
            "difficulty": "hard",
            "is_active": True,
            "start_date": start_date_2,
            "end_date": start_date_2 + timedelta(days=21)
        }
    ]
    
    return challenges

def seed_challenges():
    """Insert challenge seeds into the database"""
    
    print("🌱 Starting Challenge Database Seeding...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if challenges already exist
        existing_challenges = db.query(Challenge).count()
        print(f"📊 Current challenges in database: {existing_challenges}")
        
        if existing_challenges >= 10:
            print("✅ Database already has sufficient challenges. Skipping seeding.")
            return
        
        # Create challenge data
        challenge_seeds = create_challenge_seeds()
        
        # Insert challenges
        added_count = 0
        for challenge_data in challenge_seeds:
            # Check if challenge with this title already exists
            existing = db.query(Challenge).filter(Challenge.title == challenge_data["title"]).first()
            
            if not existing:
                challenge = Challenge(**challenge_data)
                db.add(challenge)
                added_count += 1
                print(f"➕ Added challenge: {challenge_data['title']}")
            else:
                print(f"⏭️  Challenge already exists: {challenge_data['title']}")
        
        # Commit changes
        db.commit()
        
        # Verify results
        total_challenges = db.query(Challenge).count()
        print(f"\n✅ Challenge seeding completed!")
        print(f"📈 Added {added_count} new challenges")
        print(f"📊 Total challenges in database: {total_challenges}")
        
        # Display challenge summary
        print(f"\n🎯 Challenge Summary by Category:")
        categories = db.query(Challenge.category, db.func.count(Challenge.id)).group_by(Challenge.category).all()
        for category, count in categories:
            print(f"  • {category.title()}: {count} challenges")
        
        print(f"\n🏆 Challenge Summary by Difficulty:")
        difficulties = db.query(Challenge.difficulty, db.func.count(Challenge.id)).group_by(Challenge.difficulty).all()
        for difficulty, count in difficulties:
            print(f"  • {difficulty.title()}: {count} challenges")
            
    except Exception as e:
        print(f"❌ Error seeding challenges: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_challenges()
