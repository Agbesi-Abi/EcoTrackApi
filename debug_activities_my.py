#!/usr/bin/env python3
"""
Debug script to test /activities/my endpoint
"""
import requests
import json
from pathlib import Path
import sys

# Add the API directory to the Python path
sys.path.append(str(Path(__file__).parent))

# API base URL
API_BASE_URL = "https://ecotrack-online.onrender.com/api/v1"

def test_login_and_activities():
    """Test login and then try to fetch user activities"""
    
    print("🔍 Testing /activities/my endpoint...")
    
    # First, try to login with a demo user
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }
    
    print("🔐 Logging in...")
    try:
        # Login
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login", 
            data=login_data,  # Use form data format
            timeout=30
        )
        
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('access_token')
            user_info = login_result.get('user', {})
            
            print(f"✅ Login successful for user: {user_info.get('name', 'Unknown')} (ID: {user_info.get('id')})")
            
            # Now test /activities/my endpoint
            print("\n📋 Testing /activities/my endpoint...")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            activities_response = requests.get(
                f"{API_BASE_URL}/activities/my",
                headers=headers,
                timeout=30
            )
            
            print(f"Activities status: {activities_response.status_code}")
            
            if activities_response.status_code == 200:
                activities = activities_response.json()
                print(f"✅ Activities fetched successfully: {len(activities)} activities")
                
                for activity in activities[:3]:  # Show first 3 activities
                    print(f"  - {activity.get('title', 'No title')} ({activity.get('type', 'unknown')})")
                    
            else:
                print(f"❌ Activities fetch failed: {activities_response.status_code}")
                try:
                    error_detail = activities_response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Error text: {activities_response.text}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            try:
                error_detail = login_response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error text: {login_response.text}")
                
    except Exception as e:
        print(f"💥 Exception occurred: {e}")

def test_health_check():
    """Test the health endpoint"""
    print("\n🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=10)
        print(f"Health status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data}")
        else:
            print(f"❌ Health check failed: {response.text}")
            
    except Exception as e:
        print(f"💥 Health check exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting API debug session...")
    
    test_health_check()
    test_login_and_activities()
    
    print("\n✅ Debug session complete")
