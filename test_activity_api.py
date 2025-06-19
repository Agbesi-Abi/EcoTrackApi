"""
Quick test script to verify activity creation API endpoint
"""
import requests
import json
import time

API_BASE_URL = "https://ecotrack-ghana-57b7a53a4c97.herokuapp.com/api/v1"

def test_health():
    """Test health endpoint"""
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=30)
        response_time = (time.time() - start_time) * 1000
        
        print(f"✅ Health Check: {response.status_code} ({response_time:.0f}ms)")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Service: {health_data.get('service')}")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Environment: {health_data.get('environment')}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_activity_creation():
    """Test activity creation without authentication (should fail gracefully)"""
    try:
        start_time = time.time()
        
        # Test data
        activity_data = {
            "type": "trash",
            "title": "Test Activity",
            "description": "This is a test activity to verify the endpoint",
            "location": "Test Location",
            "region": "Greater Accra",
            "photos": [],
            "impact_data": {
                "test": True,
                "logged_at": "2025-06-18T12:00:00Z"
            }
        }
        
        response = requests.post(
            f"{API_BASE_URL}/activities",
            json=activity_data,
            timeout=60,  # 60 second timeout for activity creation
            headers={"Content-Type": "application/json"}
        )
        
        response_time = (time.time() - start_time) * 1000
        
        print(f"📝 Activity Creation Test: {response.status_code} ({response_time:.0f}ms)")
        
        if response.status_code == 401:
            print("   ✅ Expected authentication error (endpoint is working)")
            return True
        elif response.status_code == 200:
            print("   ✅ Unexpected success (no auth required?)")
            return True
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout after 60 seconds (server may be cold starting)")
        return False
    except Exception as e:
        print(f"   ❌ Activity Creation Failed: {e}")
        return False

def main():
    print("🚀 EcoTrack API Connectivity Test")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health()
    print()
    
    if health_ok:
        # Test activity creation
        test_activity_creation()
    else:
        print("⚠️ Skipping activity test due to health check failure")
    
    print()
    print("🏁 Test completed")

if __name__ == "__main__":
    main()
