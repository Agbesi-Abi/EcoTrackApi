#!/usr/bin/env python3
"""
Test login with direct requests to identify the exact issue
"""

import requests
import json
from urllib.parse import urlencode

def test_login_directly():
    """Test login with different methods to identify the issue"""
    
    base_url = "https://ecotrack-online.onrender.com"
    
    print("🧪 Direct Login Testing")
    print("=" * 40)
    
    # Test 1: Check if API is responsive
    print("1. Testing API health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        print(f"   Health Status: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"   Health Data: {health}")
            db_type = health.get('database_type', 'unknown')
            print(f"   Database Type: {db_type}")
        else:
            print(f"   Health Error: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ API not responsive: {e}")
        return
    
    # Test 2: Try login with form data (FastAPI OAuth2 expects this)
    print("\n2. Testing login with form data...")
    try:
        login_data = {
            'username': 'admin@ecotrack.gh',
            'password': 'demo123'
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"   Login Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Login successful!")
            print(f"   User: {result.get('user', {}).get('email', 'unknown')}")
        elif response.status_code == 401:
            print("   ❌ Invalid credentials (user may not exist)")
        elif response.status_code == 422:
            print("   ❌ Validation error (wrong request format)")
            print(f"   Error: {response.text}")
        elif response.status_code == 500:
            print("   ❌ Server error (database or backend issue)")
            print(f"   Error details: {response.text[:500]}")
        else:
            print(f"   ❌ Unexpected error: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Try with different user
    print("\n3. Testing with demo user...")
    try:
        login_data = {
            'username': 'demo@mail.com',
            'password': 'demo123'
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"   Demo Login Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Demo login successful!")
        else:
            print(f"   ❌ Demo login failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Demo login request failed: {e}")
    
    # Test 4: Check public endpoints
    print("\n4. Testing public endpoints...")
    try:
        response = requests.get(f"{base_url}/api/v1/community/stats/global", timeout=30)
        print(f"   Stats Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total Users: {stats.get('total_users', 0)}")
        else:
            print(f"   Stats Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Stats request failed: {e}")

if __name__ == "__main__":
    test_login_directly()
