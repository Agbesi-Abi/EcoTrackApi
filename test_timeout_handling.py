#!/usr/bin/env python3
"""
Test timeout handling for activity creation
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE_URL = "https://ecotrack-online.onrender.com/api/v1"

def test_activity_creation_timeout():
    """Test activity creation with realistic data"""
    
    print("🧪 Testing Activity Creation with Timeout Handling")
    print("=" * 60)
    
    # Step 1: Create a test user and login
    print("1. Creating test user...")
    
    user_data = {
        "email": f"timeout_test_{int(time.time())}@example.com",
        "name": "Timeout Test User",
        "password": "testpass123",
        "location": "Accra, Ghana",
        "region": "Greater Accra"
    }
    
    # Register user
    register_response = requests.post(f"{API_BASE_URL}/auth/register", json=user_data)
    if register_response.status_code == 200:
        print("✅ User registered successfully")
    else:
        print(f"❌ User registration failed: {register_response.status_code}")
        print(register_response.text)
        return
    
    # Login to get token
    print("2. Logging in...")
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    login_response = requests.post(f"{API_BASE_URL}/auth/login", data=login_data)
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    # Step 2: Create activity
    print("3. Creating activity...")
    
    activity_data = {
        "type": "trash",
        "title": f"Timeout Test Activity {datetime.now().strftime('%H:%M:%S')}",
        "description": "Testing activity creation with improved timeout handling and verification",
        "location": "Test Location, Accra",
        "region": "Greater Accra",
        "photos": [],
        "impact_data": {
            "test_timeout_handling": True,
            "logged_at": datetime.now().isoformat()
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    
    try:
        # Use a reasonable timeout for testing
        activity_response = requests.post(
            f"{API_BASE_URL}/activities", 
            json=activity_data, 
            headers=headers,
            timeout=120  # 2 minutes timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if activity_response.status_code == 200:
            activity = activity_response.json()
            print(f"✅ Activity created successfully in {duration:.2f} seconds")
            print(f"   Activity ID: {activity['id']}")
            print(f"   Points earned: {activity['points']}")
            print(f"   Title: {activity['title']}")
        else:
            print(f"❌ Activity creation failed: {activity_response.status_code}")
            print(activity_response.text)
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏰ Request timed out after {duration:.2f} seconds")
        
        # Check if activity was created despite timeout
        print("4. Checking if activity was created despite timeout...")
        
        try:
            activities_response = requests.get(
                f"{API_BASE_URL}/activities/my?limit=5", 
                headers=headers,
                timeout=30
            )
            
            if activities_response.status_code == 200:
                activities = activities_response.json()
                recent_activity = None
                
                for activity in activities:
                    if activity['title'] == activity_data['title']:
                        recent_activity = activity
                        break
                
                if recent_activity:
                    print("✅ Activity was created successfully despite timeout!")
                    print(f"   Activity ID: {recent_activity['id']}")
                    print(f"   Points earned: {recent_activity['points']}")
                else:
                    print("❌ Activity was not created")
            else:
                print(f"❌ Could not check activities: {activities_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking activities: {e}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n🏁 Test completed")

if __name__ == "__main__":
    test_activity_creation_timeout()
