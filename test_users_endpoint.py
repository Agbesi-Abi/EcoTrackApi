#!/usr/bin/env python3
"""
Quick Backend API Test - Check if users endpoint is working
"""

import requests
import json

API_BASE = "https://ecotrack-online.onrender.com/api/v1"

def test_users_endpoint():
    """Test the users endpoint that's failing"""
    print("🔍 Testing EcoTrack Backend API...")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=10)
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test auth/me endpoint (this works)
    print(f"\n🔍 Testing /auth/me endpoint...")
    try:
        # We need a token for this, but let's see what happens
        response = requests.get(f"{API_BASE}/auth/me", timeout=10)
        print(f"Auth/me: {response.status_code}")
    except Exception as e:
        print(f"Auth/me error: {e}")
    
    # Test users/2 endpoint (this is failing)
    print(f"\n🔍 Testing /users/2 endpoint (the failing one)...")
    try:
        response = requests.get(f"{API_BASE}/users/2", timeout=10)
        print(f"Users/2: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Users/2 error: {e}")
    
    # Test if there's a different endpoint
    print(f"\n🔍 Testing alternative endpoints...")
    try:
        # Test users list
        response = requests.get(f"{API_BASE}/users", timeout=10)
        print(f"Users list: {response.status_code}")
    except Exception as e:
        print(f"Users list error: {e}")
    
    # Check available routes
    print(f"\n🔍 Testing challenges endpoint (this works)...")
    try:
        response = requests.get(f"{API_BASE}/challenges", timeout=10)
        print(f"Challenges: {response.status_code} - Success!")
    except Exception as e:
        print(f"Challenges error: {e}")

if __name__ == "__main__":
    test_users_endpoint()
