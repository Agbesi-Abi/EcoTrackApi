#!/usr/bin/env python3
"""
Quick test to verify the activities/my endpoint fix
"""

import requests
import json

def test_my_activities():
    """Test the /activities/my endpoint"""
    print("🧪 Testing /activities/my endpoint fix...")
    
    base_url = "https://ecotrack-ghana-57b7a53a4c97.herokuapp.com/api/v1"
    
    # Test user credentials
    login_data = {
        "username": "demo@ecotrack.com",
        "password": "demo123"
    }
    
    # Login to get token
    print("🔐 Logging in...")
    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
            
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print(f"✅ Login successful! Token: {access_token[:20]}...")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test /activities/my endpoint
    print("\n📝 Testing /activities/my endpoint...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{base_url}/activities/my?limit=5",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            activities = response.json()
            print(f"✅ SUCCESS! Got {len(activities)} activities")
            
            if activities:
                activity = activities[0]
                print(f"Sample activity:")
                print(f"  - ID: {activity['id']}")
                print(f"  - Type: {activity['type']}")
                print(f"  - Title: {activity['title']}")
                print(f"  - User Name: {activity['user_name']}")
                print(f"  - Points: {activity['points']}")
                print(f"  - Created: {activity['created_at']}")
            else:
                print("No activities found for this user")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Activities request error: {e}")

if __name__ == "__main__":
    test_my_activities()
