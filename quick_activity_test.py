"""
Simple diagnostic for activity creation issue
"""
import requests
import json

API_BASE_URL = "https://ecotrack-online.onrender.com/api/v1"

def quick_activity_test():
    print("🔍 Quick Activity Creation Diagnostic")
    print("=" * 40)
    
    # Test 1: Check if activities endpoint exists
    print("1. Testing activities endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/activities", timeout=10)
        print(f"   GET /activities: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Try POST without auth (should get 401)
    print("2. Testing POST without auth...")
    try:
        test_data = {
            "type": "trash",
            "title": "Test Activity",
            "description": "This is a test activity"
        }
        response = requests.post(f"{API_BASE_URL}/activities", json=test_data, timeout=10)
        print(f"   POST /activities (no auth): {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check if we can register a user
    print("3. Testing user registration...")
    try:
        user_data = {
            "email": "quicktest@example.com",
            "name": "Quick Test",
            "password": "testpass123"
        }
        response = requests.post(f"{API_BASE_URL}/auth/register", json=user_data, timeout=10)
        print(f"   POST /auth/register: {response.status_code}")
        if response.status_code == 400:
            print("   (User already exists)")
        elif response.status_code == 200:
            print("   ✅ User registration works")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Try to login
    print("4. Testing login...")
    try:
        login_data = {
            "username": "quicktest@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{API_BASE_URL}/auth/login", data=login_data, timeout=10)
        print(f"   POST /auth/login: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login works")
            token_data = response.json()
            token = token_data.get("access_token")
            if token:
                print(f"   Token: {token[:20]}...")
                return token
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    return None

def test_with_auth(token):
    print("\n5. Testing activity creation with auth...")
    try:
        activity_data = {
            "type": "trash",
            "title": "Quick Test Activity",
            "description": "Testing activity creation endpoint"
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_BASE_URL}/activities", 
            json=activity_data, 
            headers=headers, 
            timeout=30
        )
        print(f"   POST /activities (with auth): {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Activity creation successful!")
            result = response.json()
            print(f"   Activity ID: {result.get('id')}")
            print(f"   Points: {result.get('points')}")
        else:
            print(f"   ❌ Activity creation failed")
            print(f"   Response: {response.text[:300]}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
                
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    token = quick_activity_test()
    if token:
        test_with_auth(token)
    else:
        print("\n❌ Could not obtain authentication token")
    
    print("\n" + "=" * 40)
    print("Diagnostic complete")
