"""
Test activity creation with authentication
"""
import requests
import json
import time

API_BASE_URL = "https://ecotrack-online.onrender.com/api/v1"

def test_full_activity_creation():
    """Test complete activity creation flow with authentication"""
    
    print("🔍 Testing Activity Creation Flow")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("1. Creating test user...")
    user_data = {
        "email": "testuser_activity@example.com",
        "name": "Test Activity User",
        "password": "testpass123",
        "location": "Test Location",
        "region": "Greater Accra"
    }
    
    try:
        register_response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=user_data,
            timeout=30
        )
        print(f"   Registration: {register_response.status_code}")
        if register_response.status_code == 400:
            print(f"   (User may already exist: {register_response.text[:100]})")
        elif register_response.status_code != 200:
            print(f"   Error: {register_response.text}")
            return False
    except Exception as e:
        print(f"   Registration failed: {e}")
        return False
    
    # Step 2: Login to get token
    print("2. Logging in...")
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data=login_data,  # Form data for login
            timeout=30
        )
        print(f"   Login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   Login error: {login_response.text}")
            return False
            
        login_result = login_response.json()
        access_token = login_result.get("access_token")
        
        if not access_token:
            print(f"   No access token in response: {login_result}")
            return False
            
        print(f"   ✅ Got access token: {access_token[:20]}...")
        
    except Exception as e:
        print(f"   Login failed: {e}")
        return False
    
    # Step 3: Test activity creation
    print("3. Creating activity...")
    activity_data = {
        "type": "trash",
        "title": "Test Beach Cleanup",
        "description": "Testing activity creation through the API endpoint",
        "location": "Test Beach, Accra",
        "region": "Greater Accra",
        "photos": [],
        "impact_data": {
            "test_activity": True,
            "bags_collected": 2,
            "logged_at": "2025-06-18T12:00:00Z"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        start_time = time.time()
        activity_response = requests.post(
            f"{API_BASE_URL}/activities",
            json=activity_data,
            headers=headers,
            timeout=60  # 60 second timeout
        )
        response_time = (time.time() - start_time) * 1000
        
        print(f"   Activity Creation: {activity_response.status_code} ({response_time:.0f}ms)")
        
        if activity_response.status_code == 200:
            activity_result = activity_response.json()
            print(f"   ✅ Activity created successfully!")
            print(f"   Activity ID: {activity_result.get('id')}")
            print(f"   Title: {activity_result.get('title')}")
            print(f"   Points: {activity_result.get('points')}")
            print(f"   Type: {activity_result.get('type')}")
            return True
        else:
            print(f"   ❌ Activity creation failed")
            print(f"   Status: {activity_response.status_code}")
            print(f"   Response: {activity_response.text}")
            
            # Check if it's a validation error
            try:
                error_details = activity_response.json()
                print(f"   Error details: {json.dumps(error_details, indent=2)}")
            except:
                pass
            
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Activity creation timed out (60s)")
        return False
    except Exception as e:
        print(f"   ❌ Activity creation error: {e}")
        return False

def test_schema_validation():
    """Test the activity schema validation"""
    print("\n🔍 Testing Schema Validation")
    print("=" * 50)
    
    # Test invalid activity type
    print("1. Testing invalid activity type...")
    invalid_data = {
        "type": "invalid_type",
        "title": "Test",
        "description": "This should fail validation",
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/activities",
            json=invalid_data,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 422:
            print("   ✅ Validation correctly rejected invalid type")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test missing required fields
    print("2. Testing missing required fields...")
    incomplete_data = {
        "type": "trash"
        # Missing title and description
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/activities",
            json=incomplete_data,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 422:
            print("   ✅ Validation correctly rejected incomplete data")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

def main():
    print("🚀 EcoTrack Activity Creation Test")
    print("=" * 50)
    
    # Test health first
    try:
        health_response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ API Health Check: OK")
        else:
            print(f"❌ API Health Check Failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ API Health Check Error: {e}")
        return
    
    print()
    
    # Test schema validation (no auth required)
    test_schema_validation()
    
    # Test full activity creation flow
    success = test_full_activity_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Activity creation is working correctly!")
    else:
        print("❌ Activity creation has issues that need to be fixed")

if __name__ == "__main__":
    main()
