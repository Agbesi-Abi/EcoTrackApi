#!/usr/bin/env python3
"""
Quick test to verify the correct API endpoint is working
"""

import requests

def test_heroku_api():
    """Test the Heroku API endpoint"""
    print("🧪 Testing Heroku API endpoint...")
    
    base_url = "https://ecotrack-ghana-57b7a53a4c97.herokuapp.com/api/v1"
    
    # Test health endpoint first
    print("🏥 Testing health endpoint...")
    try:
        health_response = requests.get(f"{base_url}/../health", timeout=10)
        if health_response.status_code == 200:
            print(f"✅ Health check passed: {health_response.json()}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test root endpoint 
    print("\n🌍 Testing root endpoint...")
    try:
        root_response = requests.get(f"{base_url}/../", timeout=10)
        if root_response.status_code == 200:
            print(f"✅ Root endpoint works: {root_response.json()}")
        else:
            print(f"❌ Root endpoint failed: {root_response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test activities endpoint (public)
    print("\n📝 Testing activities endpoint...")
    try:
        activities_response = requests.get(f"{base_url}/activities?limit=2", timeout=10)
        if activities_response.status_code == 200:
            activities = activities_response.json()
            print(f"✅ Activities endpoint works: {len(activities)} activities found")
            if activities:
                print(f"Sample activity: {activities[0]['title']}")
        else:
            print(f"❌ Activities endpoint failed: {activities_response.status_code}")
    except Exception as e:
        print(f"❌ Activities endpoint error: {e}")
    
    # Test with demo user login
    print("\n🔐 Testing login endpoint...")
    try:
        login_data = {
            "username": "demo@ecotrack.com",
            "password": "demo123"
        }
        
        login_response = requests.post(
            f"{base_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            print(f"✅ Login successful for user: {token_data['user']['name']}")
            
            # Test /activities/my endpoint (the one we fixed)
            print("\n📋 Testing /activities/my endpoint (our fix)...")
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            my_activities_response = requests.get(
                f"{base_url}/activities/my?limit=5",
                headers=headers,
                timeout=10
            )
            
            if my_activities_response.status_code == 200:
                my_activities = my_activities_response.json()
                print(f"✅ User activities endpoint works: {len(my_activities)} activities")
                if my_activities:
                    activity = my_activities[0]
                    print(f"Sample user activity: {activity['title']} by {activity['user_name']}")
            else:
                print(f"❌ User activities failed: {my_activities_response.status_code}")
                print(f"Response: {my_activities_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Login/user activities error: {e}")

if __name__ == "__main__":
    test_heroku_api()
