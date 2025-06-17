"""
Test role-based access control for EcoTrack Ghana API
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
ADMIN_ENDPOINTS = [
    # Database management (super_admin only)
    "/admin/stats",
    "/admin/tables", 
    "/admin/table/users",
    "/admin/backup-info",
    
    # Admin user management (super_admin only)
    "/admin/admins",
    "/admin/admins/create",
    
    # User verification (admin or super_admin)
    "/admin/users/verification-stats",
    "/admin/users/1/verify",
]

# Test users (these should exist in your database)
TEST_USERS = {
    "super_admin": {
        "email": "superadmin@ecotrack.com",
        "password": "superadmin123"
    },
    "admin": {
        "email": "admin@ecotrack.com", 
        "password": "admin123"
    },
    "regular_user": {
        "email": "user@ecotrack.com",
        "password": "user123"
    }
}

def login_user(email: str, password: str) -> Dict[str, Any]:
    """Login and get access token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "token": data.get("access_token"),
                "user": data.get("user", {}),
                "role": data.get("user", {}).get("role", "unknown")
            }
        else:
            return {
                "success": False,
                "error": f"Login failed: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Login error: {str(e)}"
        }

def test_endpoint_access(token: str, endpoint: str, method: str = "GET") -> Dict[str, Any]:
    """Test access to a specific endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers, json={})
        elif method == "PUT":
            response = requests.put(f"{API_BASE_URL}{endpoint}", headers=headers, json={})
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        return {
            "success": response.status_code in [200, 201],
            "status_code": response.status_code,
            "allowed": response.status_code != 403,
            "response": response.text[:200] if response.text else "No response"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Request error: {str(e)}"
        }

def run_access_control_tests():
    """Run comprehensive role-based access control tests"""
    print("🔐 EcoTrack Ghana - Role-Based Access Control Tests")
    print("=" * 60)
    
    # Test each user type
    for user_type, credentials in TEST_USERS.items():
        print(f"\n👤 Testing {user_type.upper()} access...")
        print("-" * 40)
        
        # Login
        login_result = login_user(credentials["email"], credentials["password"])
        
        if not login_result["success"]:
            print(f"❌ Login failed: {login_result['error']}")
            continue
        
        token = login_result["token"]
        role = login_result["role"]
        user_info = login_result["user"]
        
        print(f"✅ Login successful")
        print(f"   Role: {role}")
        print(f"   Name: {user_info.get('name', 'Unknown')}")
        print(f"   Permissions: {user_info.get('permissions', 'Unknown')}")
        
        # Test endpoints
        print(f"\n🧪 Testing endpoint access...")
        
        for endpoint in ADMIN_ENDPOINTS:
            result = test_endpoint_access(token, endpoint)
            
            # Determine expected access
            if endpoint.startswith("/admin/stats") or \
               endpoint.startswith("/admin/tables") or \
               endpoint.startswith("/admin/table/") or \
               endpoint.startswith("/admin/backup-info") or \
               endpoint.startswith("/admin/admins"):
                # Database management and admin user management - super_admin only
                expected_access = (role == "super_admin")
            elif endpoint.startswith("/admin/users/"):
                # User verification - admin or super_admin
                expected_access = (role in ["admin", "super_admin"])
            else:
                expected_access = False
            
            # Check result
            status_icon = "✅" if result["allowed"] == expected_access else "❌"
            access_text = "ALLOWED" if result["allowed"] else "DENIED"
            expected_text = "SHOULD ALLOW" if expected_access else "SHOULD DENY"
            
            print(f"   {status_icon} {endpoint}")
            print(f"      Status: {result['status_code']} - {access_text}")
            print(f"      Expected: {expected_text}")
            
            if result["allowed"] != expected_access:
                print(f"      ⚠️  ACCESS CONTROL VIOLATION!")
        
        print()

def create_test_admin_user():
    """Create a test admin user for testing"""
    print("\n🔧 Creating test admin user...")
    
    # First login as super admin
    super_admin_creds = TEST_USERS["super_admin"]
    login_result = login_user(super_admin_creds["email"], super_admin_creds["password"])
    
    if not login_result["success"]:
        print(f"❌ Cannot login as super admin: {login_result['error']}")
        return False
    
    token = login_result["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test admin
    admin_data = {
        "email": "testadmin@ecotrack.com",
        "name": "Test Admin",
        "password": "testadmin123",
        "role": "admin",
        "permissions": "basic"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/admin/admins/create",
            headers=headers,
            json=admin_data
        )
        
        if response.status_code in [200, 201]:
            print("✅ Test admin user created successfully")
            print(f"   Email: {admin_data['email']}")
            print(f"   Password: {admin_data['password']}")
            print(f"   Role: {admin_data['role']}")
            return True
        else:
            print(f"❌ Failed to create test admin: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating test admin: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Starting role-based access control tests...")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code != 200:
            print("❌ API is not running or not healthy")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print("Make sure the backend is running on http://localhost:8000")
        sys.exit(1)
    
    print("✅ API is running and healthy")
    
    # Run tests
    run_access_control_tests()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("- Super admins should have access to all endpoints")
    print("- Regular admins should only access user verification endpoints")
    print("- Regular users should be denied access to all admin endpoints")
    print("=" * 60)

if __name__ == "__main__":
    main()
