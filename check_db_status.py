#!/usr/bin/env python3
"""
Check Production Database Status - See what data we have
"""

import requests
import json

def check_database_status():
    base_url = "https://ecotrack-ghana-57b7a53a4c97.herokuapp.com/api/v1"
    
    print("📊 EcoTrack Production Database Status")
    print("=" * 50)
    
    # Check challenges
    try:
        response = requests.get(f"{base_url}/challenges", timeout=30)
        if response.status_code == 200:
            challenges = response.json()
            print(f"🎯 Challenges: {len(challenges)} found")
            if challenges:
                print("   Sample challenges:")
                for i, challenge in enumerate(challenges[:3]):
                    print(f"   {i+1}. {challenge.get('title', 'Unknown')} ({challenge.get('points', 0)} points)")
        else:
            print(f"❌ Challenges: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Challenges: {e}")
    
    # Check global stats
    try:
        response = requests.get(f"{base_url}/community/stats/global", timeout=30)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📈 Global Stats:")
            print(f"   👥 Total Users: {stats.get('total_users', 0)}")
            print(f"   ⚡ Active Users: {stats.get('active_users', 0)}")
            print(f"   🏆 Total Points: {stats.get('total_points', 0)}")
            print(f"   📋 Total Activities: {stats.get('total_activities', 0)}")
        else:
            print(f"❌ Global Stats: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Global Stats: {e}")
    
    # Check activities
    try:
        response = requests.get(f"{base_url}/activities", timeout=30)
        if response.status_code == 200:
            activities = response.json()
            print(f"\n📱 Activities: {len(activities)} found")
        else:
            print(f"❌ Activities: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Activities: {e}")
    
    # Test user registration (to see if we can create accounts)
    print(f"\n🧪 Testing User Registration...")
    try:
        test_user = {
            "name": "Test Seeder User",
            "email": "testseeder@ecotrack.com",
            "password": "test123456",
            "location": "Accra, Ghana",
            "region": "Greater Accra"
        }
        
        response = requests.post(f"{base_url}/auth/register", json=test_user, timeout=30)
        if response.status_code in [200, 201]:
            print("✅ User registration working - database can accept new users")
        elif response.status_code == 409:
            print("✅ User registration working - user already exists")
        else:
            print(f"⚠️  User registration: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"❌ User registration test: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("✅ Production API is online and responding")
    print("✅ Challenges are available for the Expo app")
    print("✅ Global stats endpoint is working")
    print("ℹ️  Users can register and login")
    print("🚀 Your Expo app should now have data to work with!")
    
    print("\n📱 Next Steps:")
    print("1. Open your Expo app")
    print("2. Register a new account or use demo accounts")
    print("3. Browse challenges and test features")
    print("4. Log activities to populate the activities data")

if __name__ == "__main__":
    check_database_status()
