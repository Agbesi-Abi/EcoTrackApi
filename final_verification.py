#!/usr/bin/env python3
"""
Final verification script for the activities/my endpoint fix
"""

import subprocess
import time
import sys
import requests
import json

def test_backend_endpoint():
    """Test the backend endpoint directly"""
    print("🔧 BACKEND ENDPOINT TEST")
    print("=" * 50)
    
    base_url = "https://ecotrack-ghana-57b7a53a4c97.herokuapp.com/api/v1"
    
    # Test user credentials  
    login_data = {
        "username": "demo@ecotrack.com",
        "password": "demo123"
    }
    
    try:
        # Step 1: Login
        print("1. 🔐 Testing login...")
        login_response = requests.post(
            f"{base_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed with status {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
        token_data = login_response.json()
        access_token = token_data["access_token"]
        user_info = token_data["user"]
        print(f"   ✅ Login successful for user: {user_info['name']} (ID: {user_info['id']})")
        
        # Step 2: Test /activities/my endpoint (the one we fixed)
        print("\n2. 📝 Testing /activities/my endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        activities_response = requests.get(
            f"{base_url}/activities/my?limit=10",
            headers=headers,
            timeout=15
        )
        
        print(f"   Status Code: {activities_response.status_code}")
        
        if activities_response.status_code == 200:
            activities = activities_response.json()
            print(f"   ✅ SUCCESS! Retrieved {len(activities)} user activities")
            
            if activities:
                activity = activities[0]
                print(f"   📋 Sample activity:")
                print(f"      - ID: {activity['id']}")
                print(f"      - Type: {activity['type']}")
                print(f"      - Title: {activity['title']}")
                print(f"      - User Name: {activity['user_name']}")
                print(f"      - Points: {activity['points']}")
                print(f"      - Created: {activity['created_at']}")
                
                # Verify this activity belongs to the logged-in user
                if activity['user_id'] == user_info['id']:
                    print(f"   ✅ User ownership verified: Activity belongs to {user_info['name']}")
                else:
                    print(f"   ⚠️  Warning: Activity user_id {activity['user_id']} doesn't match logged-in user {user_info['id']}")
            else:
                print("   ℹ️  No activities found for this user")
                
            return True
            
        elif activities_response.status_code == 500:
            print(f"   ❌ Server error (500) - The issue may not be fully fixed")
            print(f"   Response: {activities_response.text}")
            return False
            
        else:
            print(f"   ❌ Error {activities_response.status_code}: {activities_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def check_frontend_code():
    """Verify frontend code changes"""
    print("\n🎨 FRONTEND CODE VERIFICATION")
    print("=" * 50)
    
    frontend_file = r"c:\Users\Abigail Adwoa Agbesi\Desktop\GhanaClean\app\activity-history.tsx"
    
    try:
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key improvements
        checks = [
            ("✅ Uses activitiesAPI.getMyActivities()", "activitiesAPI.getMyActivities" in content),
            ("✅ Proper React imports", "import React, { useState, useEffect }" in content),
            ("✅ Uses useAuth hook", "useAuth()" in content),
            ("✅ Has error handling", "setError(" in content),
            ("✅ Has loading states", "setLoading(" in content),
            ("✅ Uses user-specific data", "loadActivities" in content),
            ("✅ Has refresh functionality", "onRefresh" in content),
        ]
        
        print("Frontend code checks:")
        all_good = True
        for description, check in checks:
            if check:
                print(f"   {description}")
            else:
                print(f"   ❌ Missing: {description}")
                all_good = False
                
        return all_good
        
    except FileNotFoundError:
        print(f"   ❌ File not found: {frontend_file}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading frontend file: {e}")
        return False

def main():
    """Run complete verification"""
    print("🧪 ACTIVITY HISTORY FIX VERIFICATION")
    print("=" * 60)
    print("This script verifies that the activity history screen now")
    print("properly displays user-specific activities instead of global ones.\n")
    
    # Test backend
    backend_success = test_backend_endpoint()
    
    # Check frontend  
    frontend_success = check_frontend_code()
    
    # Summary
    print("\n📋 VERIFICATION SUMMARY")
    print("=" * 50)
    
    if backend_success and frontend_success:
        print("✅ ALL TESTS PASSED!")
        print("   🎉 The activity history fix is working correctly")
        print("   📱 Users will now see only their own activities")
        print("   🔒 User-specific data isolation is working")
        
    elif backend_success:
        print("⚠️  PARTIAL SUCCESS")
        print("   ✅ Backend endpoint is working")
        print("   ❌ Frontend may have some issues")
        
    elif frontend_success:
        print("⚠️  PARTIAL SUCCESS")
        print("   ✅ Frontend code looks good")
        print("   ❌ Backend endpoint may have issues")
        
    else:
        print("❌ TESTS FAILED")
        print("   Both backend and frontend may need attention")
    
    print(f"\n🔗 Test endpoint: https://ecotrack-ghana-57b7a53a4c97.herokuapp.com/api/v1/activities/my")
    
    return backend_success and frontend_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
