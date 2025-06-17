#!/usr/bin/env python3
"""
Production Database Seeding Script
Seeds the production database via API calls to the deployed server
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ProductionSeeder:
    def __init__(self, base_url: str = "https://ecotrack-online.onrender.com/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'EcoTrack-Seeder/1.0'
        })
        self.admin_token = None
        
    def wake_up_server(self):
        """Wake up the server if it's sleeping (Render free tier)"""
        print("🌅 Waking up production server...")
        try:
            response = self.session.get(f"{self.base_url}/", timeout=60)
            print(f"✅ Server is awake! Status: {response.status_code}")
            return True
        except requests.exceptions.Timeout:
            print("⏰ Server is taking time to wake up, trying again...")
            time.sleep(30)
            try:
                response = self.session.get(f"{self.base_url}/", timeout=60)
                print(f"✅ Server is now awake! Status: {response.status_code}")
                return True
            except Exception as e:
                print(f"❌ Failed to wake up server: {e}")
                return False
        except Exception as e:
            print(f"❌ Error waking up server: {e}")
            return False
    
    def create_admin_user(self) -> bool:
        """Create admin user and get authentication token"""
        print("👑 Creating admin user...")
        
        admin_data = {
            "name": "EcoTrack Admin",
            "email": "admin@ecotrack.com",
            "password": "admin123456",
            "location": "Accra, Ghana",
            "region": "Greater Accra"
        }
        
        try:
            # Register admin user
            response = self.session.post(f"{self.base_url}/auth/register", json=admin_data)
            if response.status_code in [200, 201, 409]:  # 409 means user already exists
                print("✅ Admin user created/exists")
                
                # Login to get token
                login_data = {
                    "email": admin_data["email"],
                    "password": admin_data["password"]
                }
                
                response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                if response.status_code == 200:
                    token_data = response.json()
                    self.admin_token = token_data.get("access_token")
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    print("✅ Admin authenticated successfully")
                    return True
                else:
                    print(f"❌ Login failed: {response.status_code} - {response.text}")
                    return False
            else:
                print(f"❌ Admin creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating admin: {e}")
            return False
    
    def create_demo_users(self) -> bool:
        """Create demo users"""
        print("👥 Creating demo users...")
        
        demo_users = [
            {
                "name": "Demo User",
                "email": "demo@ecotrack.com",
                "password": "demo123456",
                "location": "Accra, Ghana",
                "region": "Greater Accra"
            },
            {
                "name": "Eco Champion",
                "email": "eco@ghana.com",
                "password": "ecotrack123",
                "location": "Kumasi, Ghana",
                "region": "Ashanti"
            },
            {
                "name": "Test User",
                "email": "test@ecotrack.com",
                "password": "password123",
                "location": "Cape Coast, Ghana",
                "region": "Central"
            },
            {
                "name": "Kwame Asante",
                "email": "kwame.asante@ecotrack.com",
                "password": "kwame123",
                "location": "Tamale, Ghana",
                "region": "Northern"
            },
            {
                "name": "Ama Osei",
                "email": "ama.osei@ecotrack.com",
                "password": "ama123",
                "location": "Sekondi-Takoradi, Ghana",
                "region": "Western"
            }
        ]
        
        created_count = 0
        for user_data in demo_users:
            try:
                response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
                if response.status_code in [200, 201]:
                    print(f"✅ Created user: {user_data['email']}")
                    created_count += 1
                elif response.status_code == 409:
                    print(f"ℹ️  User already exists: {user_data['email']}")
                    created_count += 1
                else:
                    print(f"❌ Failed to create user {user_data['email']}: {response.status_code}")
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error creating user {user_data['email']}: {e}")
        
        print(f"✅ Demo users ready: {created_count}/{len(demo_users)}")
        return created_count > 0
    
    def create_challenges(self) -> bool:
        """Create sample challenges"""
        print("🎯 Creating challenges...")
        
        challenges = [
            {
                "title": "No Plastic Wednesday",
                "description": "Avoid single-use plastics for the entire day. Use reusable bags and containers instead of plastic ones.",
                "category": "trash",
                "duration": "1 day",
                "points": 50,
                "difficulty": "easy"
            },
            {
                "title": "Plant a Tree Challenge",
                "description": "Plant a native tree in your community. Document with photos and location for verification.",
                "category": "trees",
                "duration": "1 week",
                "points": 150,
                "difficulty": "medium"
            },
            {
                "title": "Carpool to Work Week",
                "description": "Share rides with colleagues or use public transport for a full week instead of driving alone.",
                "category": "mobility",
                "duration": "7 days",
                "points": 120,
                "difficulty": "medium"
            },
            {
                "title": "Beach Cleanup Marathon",
                "description": "Organize or join a beach cleanup in Accra, Cape Coast, or Elmina. Collect at least 5 bags of waste.",
                "category": "trash",
                "duration": "1 day",
                "points": 200,
                "difficulty": "hard"
            },
            {
                "title": "Plastic-Free Shopping Month",
                "description": "Shop without using any plastic bags or containers for an entire month. Use cloth bags and glass containers.",
                "category": "trash",
                "duration": "30 days",
                "points": 300,
                "difficulty": "hard"
            },
            {
                "title": "Urban Garden Starter",
                "description": "Start a small urban garden with at least 3 different plants. Perfect for apartments and small spaces.",
                "category": "trees",
                "duration": "2 weeks",
                "points": 100,
                "difficulty": "easy"
            },
            {
                "title": "Walk to Work Week",
                "description": "Walk or cycle to work for 5 consecutive working days. Track your distance and CO2 savings.",
                "category": "mobility",
                "duration": "5 days",
                "points": 80,
                "difficulty": "easy"
            },
            {
                "title": "Community Forest Initiative",
                "description": "Plant 10 trees in your community with friends or local groups. Organize a tree planting event.",
                "category": "trees",
                "duration": "1 month",
                "points": 500,
                "difficulty": "hard"
            }
        ]
        
        created_count = 0
        for challenge_data in challenges:
            try:
                response = self.session.post(f"{self.base_url}/challenges/", json=challenge_data)
                if response.status_code in [200, 201]:
                    print(f"✅ Created challenge: {challenge_data['title']}")
                    created_count += 1
                else:
                    print(f"❌ Failed to create challenge {challenge_data['title']}: {response.status_code}")
                    print(f"Response: {response.text}")
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error creating challenge {challenge_data['title']}: {e}")
        
        print(f"✅ Challenges created: {created_count}/{len(challenges)}")
        return created_count > 0
    
    def verify_seeding(self) -> bool:
        """Verify that data was seeded successfully"""
        print("🔍 Verifying seeded data...")
        
        endpoints_to_check = [
            ("/challenges", "challenges"),
            ("/community/stats/global", "global stats"),
        ]
        
        all_good = True
        for endpoint, description in endpoints_to_check:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        print(f"✅ {description}: {len(data)} items found")
                    elif isinstance(data, dict) and data:
                        print(f"✅ {description}: Data available")
                    else:
                        print(f"⚠️  {description}: No data found")
                        all_good = False
                else:
                    print(f"❌ {description}: API error {response.status_code}")
                    all_good = False
                    
            except Exception as e:
                print(f"❌ Error checking {description}: {e}")
                all_good = False
        
        return all_good
    
    def seed_production(self) -> bool:
        """Main seeding function"""
        print("🌱 Starting production database seeding...")
        print("=" * 50)
        
        # Step 1: Wake up server
        if not self.wake_up_server():
            return False
        
        # Step 2: Create admin user and authenticate
        if not self.create_admin_user():
            print("⚠️  Continuing without admin authentication...")
        
        # Step 3: Create demo users
        if not self.create_demo_users():
            print("❌ Failed to create demo users")
            return False
        
        # Step 4: Create challenges
        if not self.create_challenges():
            print("❌ Failed to create challenges")
            return False
        
        # Step 5: Verify everything worked
        success = self.verify_seeding()
        
        if success:
            print("\n🎉 Production database seeding completed successfully!")
            print("\n📋 Demo Accounts Available:")
            print("1. demo@ecotrack.com / demo123456")
            print("2. eco@ghana.com / ecotrack123")
            print("3. test@ecotrack.com / password123")
            print("4. kwame.asante@ecotrack.com / kwame123")
            print("5. ama.osei@ecotrack.com / ama123")
            print("\n👑 Admin Account:")
            print("admin@ecotrack.com / admin123456")
        else:
            print("\n⚠️  Seeding completed with some issues. Check the logs above.")
        
        return success

def main():
    """Main entry point"""
    seeder = ProductionSeeder()
    success = seeder.seed_production()
    
    if success:
        print("\n✅ Your Expo app should now have data to work with!")
        print("🚀 Try logging in with any of the demo accounts.")
    else:
        print("\n❌ Seeding failed. Check the error messages above.")
        print("🔧 You may need to manually check the API endpoints or server status.")

if __name__ == "__main__":
    main()
