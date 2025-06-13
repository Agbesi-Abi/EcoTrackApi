#!/usr/bin/env python3
"""
Test admin endpoints locally
"""

import requests
import time
import json

def test_admin_endpoints():
    """Test all admin endpoints"""
    base_url = "http://localhost:8000"
    admin_endpoints = [
        "/api/v1/admin/docs",
        "/api/v1/admin/stats", 
        "/api/v1/admin/tables",
        "/api/v1/admin/backup-info"
    ]
    
    print("🧪 Testing Admin Endpoints")
    print("=" * 50)
    
    # Test health first
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running with: python main.py")
        return False
    
    # Test admin endpoints
    for endpoint in admin_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 Testing: {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
                
                if endpoint == "/api/v1/admin/stats":
                    # Show some stats data
                    data = response.json()
                    print(f"   📊 Total Records: {data.get('total_records', 'N/A')}")
                    print(f"   📋 Tables: {len(data.get('tables', {}))}")
                    
            elif response.status_code == 404:
                print(f"❌ {endpoint} - Not Found (404)")
                print("   Admin routes may not be enabled")
                
            else:
                print(f"⚠️ {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    return True

def show_quick_commands():
    """Show useful commands for admin access"""
    print("\n🔧 Quick Admin Commands")
    print("=" * 50)
    print("PowerShell:")
    print('  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/stats"')
    print('  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/tables"')
    print("")
    print("Browser:")
    print("  http://localhost:8000/api/v1/admin/docs")
    print("  http://localhost:8000/docs")

if __name__ == "__main__":
    if test_admin_endpoints():
        show_quick_commands()
    else:
        print("\n❌ Admin endpoint tests failed")
        print("🔧 Troubleshooting:")
        print("1. Make sure server is running: python main.py")
        print("2. Set environment variables: $env:ENABLE_ADMIN='true'")
        print("3. Check server logs for errors")
