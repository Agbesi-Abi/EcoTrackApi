#!/usr/bin/env python3
"""
Test script to check admin endpoints locally
"""

import os
import sys
import subprocess
import time
import requests

def test_admin_endpoints():
    """Test admin endpoints"""
    
    # Set environment variables
    os.environ['ENABLE_ADMIN'] = 'true'
    os.environ['ENABLE_DOCS'] = 'true'
    
    print("🧪 Testing Admin Endpoints Configuration")
    print("=" * 50)
    
    # Test imports
    try:
        from admin.routes import router
        print("✅ Admin routes imported successfully")
    except Exception as e:
        print(f"❌ Admin routes import failed: {e}")
        return False
    
    try:
        import main
        print("✅ Main module imported successfully")
    except Exception as e:
        print(f"❌ Main module import failed: {e}")
        return False
    
    # Check if admin router is included
    from main import app
    routes = [route.path for route in app.routes]
    admin_routes = [route for route in routes if '/admin' in route]
    
    print(f"\n📋 Available routes with '/admin':")
    for route in admin_routes:
        print(f"  • {route}")
    
    if admin_routes:
        print("✅ Admin routes are registered in the app")
        return True
    else:
        print("❌ No admin routes found in the app")
        return False

def check_production_deployment():
    """Check what's needed for production deployment"""
    print("\n🚀 Production Deployment Requirements")
    print("=" * 50)
    
    env_file = ".env.production"
    if os.path.exists(env_file):
        print(f"✅ {env_file} exists")
        
        with open(env_file, 'r') as f:
            content = f.read()
            if 'ENABLE_ADMIN=true' in content:
                print("✅ ENABLE_ADMIN=true is set in production")
            else:
                print("❌ ENABLE_ADMIN=true not found in production")
                
            if 'ENABLE_DOCS=true' in content:
                print("✅ ENABLE_DOCS=true is set in production")
            else:
                print("❌ ENABLE_DOCS=true not found in production")
    else:
        print(f"❌ {env_file} not found")
    
    print("\n📝 Next Steps:")
    print("1. Commit and push the changes to GitHub")
    print("2. Render will auto-deploy (if connected to GitHub)")
    print("3. Wait for deployment to complete")
    print("4. Test admin endpoints on production")

if __name__ == "__main__":
    if test_admin_endpoints():
        check_production_deployment()
    else:
        print("\n❌ Admin endpoints test failed. Please check the configuration.")
