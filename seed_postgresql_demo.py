#!/usr/bin/env python3
"""
PostgreSQL Database Seeding Script for EcoTrack Ghana
Creates comprehensive test data for development and testing
"""

import os
import sys
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import text

# Load environment variables
load_dotenv('.env.production')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    SessionLocal, engine, init_db, Base,
    User, Region, Activity, Challenge, Notification, challenge_participants
)
from auth.utils import get_password_hash

class PostgreSQLSeeder:
    def __init__(self):
        self.db = SessionLocal()
        self.ghana_regions = [
            {"name": "Greater Accra", "capital": "Accra", "code": "GA", "population": 5455692},
            {"name": "Ashanti", "capital": "Kumasi", "code": "AS", "population": 5440463},
            {"name": "Western", "capital": "Sekondi-Takoradi", "code": "WP", "population": 2060585},
            {"name": "Central", "capital": "Cape Coast", "code": "CP", "population": 2859821},
            {"name": "Eastern", "capital": "Koforidua", "code": "EP", "population": 2106696},
            {"name": "Volta", "capital": "Ho", "code": "TV", "population": 1635421},
            {"name": "Northern", "capital": "Tamale", "code": "NP", "population": 1972757},
            {"name": "Upper East", "capital": "Bolgatanga", "code": "UE", "population": 920089},
            {"name": "Upper West", "capital": "Wa", "code": "UW", "population": 576583},
            {"name": "Brong Ahafo", "capital": "Sunyani", "code": "BA", "population": 1815408},
            {"name": "Western North", "capital": "Sefwi Wiawso", "code": "WN", "population": 678555},
            {"name": "Ahafo", "capital": "Goaso", "code": "AH", "population": 563677},
            {"name": "Bono", "capital": "Sunyani", "code": "BO", "population": 691983},
            {"name": "Bono East", "capital": "Techiman", "code": "BE", "population": 1208649},
            {"name": "Oti", "capital": "Dambai", "code": "OT", "population": 563677},
            {"name": "North East", "capital": "Nalerigu", "code": "NE", "population": 466026},
            {"name": "Savannah", "capital": "Damongo", "code": "SV", "population": 685801}
        ]

    def seed_all(self):
        """Seed all tables with comprehensive test data"""
        try:
            print("🚀 Starting PostgreSQL Database Seeding for EcoTrack Ghana")
            print("=" * 60)
            
            # Initialize database schema
            print("📋 Initializing database schema...")
            init_db()
            print("✅ Database schema initialized")
            
            # Clear existing data (for fresh testing)
            print("🧹 Clearing existing test data...")
            self.clear_test_data()
            
            # Seed in order due to foreign key constraints
            self.seed_regions()
            self.seed_users()
            self.seed_challenges()
            self.seed_activities()
            self.seed_challenge_participants()
            self.seed_notifications()
            
            print("\n🎉 Database seeding completed successfully!")
            print("📊 Database is ready for testing with comprehensive demo data")
            
        except Exception as e:
            print(f"❌ Seeding failed: {str(e)}")
            self.db.rollback()
        finally:
            self.db.close()

    def clear_test_data(self):
        """Clear existing test data for fresh seeding"""
        try:
            # Delete in reverse order to respect foreign keys
            self.db.execute(text("DELETE FROM challenge_participants"))
            self.db.execute(text("DELETE FROM notifications"))
            self.db.execute(text("DELETE FROM activities"))
            self.db.execute(text("DELETE FROM challenges"))
            self.db.execute(text("DELETE FROM users WHERE email LIKE '%test%' OR email LIKE '%demo%'"))
            self.db.commit()
            print("✅ Test data cleared")
        except Exception as e:
            print(f"⚠️  Warning: Could not clear test data: {e}")
            self.db.rollback()

    def seed_regions(self):
        """Seed Ghana regions"""
        print("🏘️  Seeding Ghana regions...")
        
        # Check if regions already exist
        existing_count = self.db.query(Region).count()
        if existing_count > 0:
            print(f"✅ Regions already exist ({existing_count} regions)")
            return
        
        for region_data in self.ghana_regions:
            region = Region(**region_data)
            self.db.add(region)
        
        self.db.commit()
        print(f"✅ Seeded {len(self.ghana_regions)} Ghana regions")

    def seed_users(self):
        """Seed test users with diverse profiles"""
        print("👥 Seeding test users...")
        
        test_users = [
            {
                "email": "admin@ecotrack.gh",
                "name": "System Admin",
                "password": "admin123",
                "location": "Accra, Greater Accra",
                "region": "Greater Accra",
                "total_points": 2500,
                "weekly_points": 150,
                "is_admin": True
            },
            {
                "email": "kwame.test@gmail.com",
                "name": "Kwame Asante",
                "password": "password123",
                "location": "Kumasi, Ashanti",
                "region": "Ashanti",
                "total_points": 1850,
                "weekly_points": 120
            },
            {
                "email": "ama.demo@gmail.com",
                "name": "Ama Osei",
                "password": "password123",
                "location": "Cape Coast, Central",
                "region": "Central",
                "total_points": 2100,
                "weekly_points": 180
            },
            {
                "email": "kofi.test@yahoo.com",
                "name": "Kofi Mensah",
                "password": "password123",
                "location": "Tamale, Northern",
                "region": "Northern",
                "total_points": 1650,
                "weekly_points": 95
            },
            {
                "email": "akosua.demo@gmail.com",
                "name": "Akosua Frimpong",
                "password": "password123",
                "location": "Ho, Volta",
                "region": "Volta",
                "total_points": 1950,
                "weekly_points": 140
            },
            {
                "email": "yaw.test@hotmail.com",
                "name": "Yaw Boakye",
                "password": "password123",
                "location": "Sekondi-Takoradi, Western",
                "region": "Western",
                "total_points": 1420,
                "weekly_points": 85
            }
        ]
        
        for user_data in test_users:
            password = user_data.pop("password")
            user = User(
                **user_data,
                hashed_password=get_password_hash(password),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(user)
        
        self.db.commit()
        print(f"✅ Seeded {len(test_users)} test users")

    def seed_challenges(self):
        """Seed environmental challenges"""
        print("🏆 Seeding environmental challenges...")
        
        challenges_data = [
            {
                "title": "No Plastic Wednesday",
                "description": "Avoid single-use plastics for the entire day. Use reusable bags, containers, and water bottles.",
                "category": "trash",
                "duration": "1 day",
                "points": 50,
                "difficulty": "easy",
                "start_date": datetime.utcnow() - timedelta(days=5),
                "end_date": datetime.utcnow() + timedelta(days=25),
                "is_active": True
            },
            {
                "title": "Plant a Tree Challenge",
                "description": "Plant a native tree in your community. Document with photos and GPS location for verification.",
                "category": "trees",
                "duration": "1 week",
                "points": 150,
                "difficulty": "medium",
                "start_date": datetime.utcnow() - timedelta(days=10),
                "end_date": datetime.utcnow() + timedelta(days=50),
                "is_active": True
            },
            {
                "title": "Carpool to Work Week",
                "description": "Share rides with colleagues or use public transport for a full week instead of driving alone.",
                "category": "mobility",
                "duration": "7 days",
                "points": 120,
                "difficulty": "medium",
                "start_date": datetime.utcnow() - timedelta(days=3),
                "end_date": datetime.utcnow() + timedelta(days=37),
                "is_active": True
            },
            {
                "title": "Beach Cleanup Marathon",
                "description": "Organize or join a beach cleanup in coastal regions. Collect at least 5 bags of waste.",
                "category": "trash",
                "duration": "1 day",
                "points": 200,
                "difficulty": "hard",
                "start_date": datetime.utcnow() - timedelta(days=15),
                "end_date": datetime.utcnow() + timedelta(days=45),
                "is_active": True
            },
            {
                "title": "Zero Waste Weekend",
                "description": "Complete a weekend producing absolutely no waste. Compost, reuse, and recycle everything.",
                "category": "trash",
                "duration": "2 days",
                "points": 180,
                "difficulty": "hard",
                "start_date": datetime.utcnow() - timedelta(days=7),
                "end_date": datetime.utcnow() + timedelta(days=33),
                "is_active": True
            },
            {
                "title": "Bike to Work Month",
                "description": "Use a bicycle for your daily commute for an entire month. Track distance and CO2 saved.",
                "category": "mobility",
                "duration": "30 days",
                "points": 300,
                "difficulty": "hard",
                "start_date": datetime.utcnow() - timedelta(days=20),
                "end_date": datetime.utcnow() + timedelta(days=40),
                "is_active": True
            }
        ]
        
        for challenge_data in challenges_data:
            challenge = Challenge(**challenge_data)
            self.db.add(challenge)
        
        self.db.commit()
        print(f"✅ Seeded {len(challenges_data)} environmental challenges")

    def seed_activities(self):
        """Seed user activities"""
        print("📝 Seeding user activities...")
        
        users = self.db.query(User).all()
        activity_types = ["trash_pickup", "tree_planting", "recycling", "carpooling", "composting"]
        locations = [
            "Accra Beach", "Kumasi Central Market", "Cape Coast Castle Area",
            "Tamale Sports Stadium", "Ho Municipal Park", "Takoradi Harbor",
            "University of Ghana Campus", "Achimota Forest Reserve",
            "Labadi Beach", "Kaneshie Market"
        ]
        
        activities_data = []
        for i in range(50):  # Create 50 sample activities
            user = random.choice(users)
            activity_type = random.choice(activity_types)
            location = random.choice(locations)
            
            # Generate realistic impact data based on activity type
            impact_data = self.generate_impact_data(activity_type)
            
            activity = {
                "user_id": user.id,
                "type": activity_type,
                "title": f"{activity_type.replace('_', ' ').title()} Activity",
                "description": f"Completed {activity_type.replace('_', ' ')} at {location}. Making Ghana greener!",
                "points": random.randint(20, 150),
                "location": location,
                "region": user.region,
                "photos": [f"photo_{i}_1.jpg", f"photo_{i}_2.jpg"],
                "verified": random.choice([True, True, True, False]),  # 75% verified
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                "impact_data": impact_data
            }
            activities_data.append(Activity(**activity))
        
        self.db.add_all(activities_data)
        self.db.commit()
        print(f"✅ Seeded {len(activities_data)} user activities")

    def generate_impact_data(self, activity_type):
        """Generate realistic impact data for activities"""
        impact_data = {}
        
        if activity_type == "trash_pickup":
            impact_data = {
                "waste_collected_kg": round(random.uniform(1.5, 25.0), 2),
                "plastic_bottles": random.randint(5, 50),
                "plastic_bags": random.randint(10, 100),
                "area_cleaned_sqm": random.randint(50, 500)
            }
        elif activity_type == "tree_planting":
            impact_data = {
                "trees_planted": random.randint(1, 10),
                "tree_species": random.choice(["Mahogany", "Teak", "Coconut Palm", "Baobab", "Neem"]),
                "estimated_co2_absorption_kg_year": round(random.uniform(20, 150), 2)
            }
        elif activity_type == "recycling":
            impact_data = {
                "materials_recycled_kg": round(random.uniform(2, 15), 2),
                "plastic_recycled_kg": round(random.uniform(0.5, 8), 2),
                "paper_recycled_kg": round(random.uniform(1, 5), 2)
            }
        elif activity_type == "carpooling":
            impact_data = {
                "distance_km": round(random.uniform(10, 100), 2),
                "co2_saved_kg": round(random.uniform(2.5, 25), 2),
                "passengers": random.randint(2, 5),
                "fuel_saved_liters": round(random.uniform(1, 8), 2)
            }
        elif activity_type == "composting":
            impact_data = {
                "organic_waste_kg": round(random.uniform(2, 20), 2),
                "compost_produced_kg": round(random.uniform(1, 10), 2),
                "weeks_composting": random.randint(2, 12)
            }
        
        return impact_data

    def seed_challenge_participants(self):
        """Seed challenge participation data"""
        print("🤝 Seeding challenge participants...")
        
        users = self.db.query(User).all()
        challenges = self.db.query(Challenge).all()
        
        # Each user participates in 2-4 random challenges
        for user in users:
            participating_challenges = random.sample(challenges, random.randint(2, min(4, len(challenges))))
            
            for challenge in participating_challenges:
                # Insert into association table
                participation_data = {
                    'user_id': user.id,
                    'challenge_id': challenge.id,
                    'joined_at': datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                    'progress': round(random.uniform(0.1, 1.0), 2),
                    'completed': random.choice([True, False])
                }
                
                stmt = challenge_participants.insert().values(**participation_data)
                self.db.execute(stmt)
        
        self.db.commit()
        print("✅ Seeded challenge participation data")

    def seed_notifications(self):
        """Seed user notifications"""
        print("🔔 Seeding notifications...")
        
        users = self.db.query(User).all()
        notification_types = [
            "achievement", "challenge_reminder", "community_update", 
            "activity_verified", "new_challenge", "weekly_summary"
        ]
        
        notifications_data = []
        for i in range(30):  # Create 30 sample notifications
            user = random.choice(users)
            notification_type = random.choice(notification_types)
            
            title, message = self.generate_notification_content(notification_type)
            
            notification = Notification(
                user_id=user.id,
                type=notification_type,
                title=title,
                message=message,
                is_read=random.choice([True, False]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 14))
            )
            notifications_data.append(notification)
        
        self.db.add_all(notifications_data)
        self.db.commit()
        print(f"✅ Seeded {len(notifications_data)} notifications")

    def generate_notification_content(self, notification_type):
        """Generate notification content based on type"""
        if notification_type == "achievement":
            return "Achievement Unlocked! 🏆", "You've earned the 'Tree Hugger' badge for planting 5 trees!"
        elif notification_type == "challenge_reminder":
            return "Challenge Reminder 📢", "Don't forget to complete your 'No Plastic Wednesday' challenge today!"
        elif notification_type == "community_update":
            return "Community Milestone 🎉", "Your region has collectively saved 500kg of CO2 this month!"
        elif notification_type == "activity_verified":
            return "Activity Verified ✅", "Your beach cleanup activity has been verified. You earned 150 points!"
        elif notification_type == "new_challenge":
            return "New Challenge Available 🆕", "Join the 'Bike to Work Month' challenge and earn up to 300 points!"
        else:
            return "Weekly Summary 📊", "This week you earned 180 points and helped save 12kg of CO2!"

    def print_database_summary(self):
        """Print summary of seeded data"""
        print("\n📊 Database Summary:")
        print("=" * 40)
        
        try:
            regions_count = self.db.query(Region).count()
            users_count = self.db.query(User).count()
            challenges_count = self.db.query(Challenge).count()
            activities_count = self.db.query(Activity).count()
            notifications_count = self.db.query(Notification).count()
            
            # Count participants
            participants_count = self.db.execute(
                text("SELECT COUNT(*) FROM challenge_participants")
            ).scalar()
            
            print(f"🏘️  Regions: {regions_count}")
            print(f"👥 Users: {users_count}")
            print(f"🏆 Challenges: {challenges_count}")
            print(f"📝 Activities: {activities_count}")
            print(f"🤝 Challenge Participants: {participants_count}")
            print(f"🔔 Notifications: {notifications_count}")
            
            print("\n👤 Test User Accounts:")
            print("📧 admin@ecotrack.gh (password: admin123) - Admin")
            print("📧 kwame.test@gmail.com (password: password123)")
            print("📧 ama.demo@gmail.com (password: password123)")
            print("📧 kofi.test@yahoo.com (password: password123)")
            print("📧 akosua.demo@gmail.com (password: password123)")
            print("📧 yaw.test@hotmail.com (password: password123)")
            
        except Exception as e:
            print(f"❌ Could not generate summary: {e}")

def main():
    """Main seeding function"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL.startswith("postgresql"):
        print("❌ This script is for PostgreSQL databases only")
        sys.exit(1)
    
    print("🌍 EcoTrack Ghana - PostgreSQL Database Seeding")
    print("=" * 55)
    print(f"🔗 Database: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'Unknown'}")
    print("")
    
    seeder = PostgreSQLSeeder()
    seeder.seed_all()
    seeder.print_database_summary()
    
    print("\n🚀 Seeding complete! Your database is ready for testing.")
    print("🔧 You can now test the EcoTrack Ghana API with realistic demo data.")

if __name__ == "__main__":
    main()
