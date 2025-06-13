#!/usr/bin/env python3
"""
Debug script to check admin configuration
"""

import os

# Set environment variables
os.environ['ENABLE_ADMIN'] = 'true'
os.environ['ENABLE_DOCS'] = 'true'

print("🔍 Debug Admin Configuration")
print("=" * 50)

# Check environment variables
print("Environment Variables:")
print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT', 'development')}")
print(f"  DEBUG: {os.getenv('ENVIRONMENT', 'development') == 'development'}")
print(f"  ENABLE_ADMIN: {os.getenv('ENABLE_ADMIN', 'false')}")
print(f"  ENABLE_DOCS: {os.getenv('ENABLE_DOCS', 'false')}")

# Check the boolean evaluation
DEBUG = os.getenv('ENVIRONMENT', 'development') == 'development'
ENABLE_ADMIN = os.getenv('ENABLE_ADMIN', 'false').lower() == 'true'

print(f"\nBoolean Evaluation:")
print(f"  DEBUG: {DEBUG}")
print(f"  ENABLE_ADMIN: {ENABLE_ADMIN}")
print(f"  Should include admin: {DEBUG or ENABLE_ADMIN}")

# Try importing
try:
    from admin.routes import router as admin_router
    print(f"\n✅ Admin router imported successfully")
    print(f"   Router type: {type(admin_router)}")
    print(f"   Router routes: {len(admin_router.routes) if hasattr(admin_router, 'routes') else 'N/A'}")
except Exception as e:
    print(f"\n❌ Admin router import failed: {e}")

# Try importing main
try:
    from main import app
    print(f"\n✅ Main app imported successfully")
    
    # Check routes
    routes = [route.path for route in app.routes]
    admin_routes = [route for route in routes if '/admin' in route]
    
    print(f"   Total routes: {len(routes)}")
    print(f"   Admin routes: {len(admin_routes)}")
    
    if admin_routes:
        print("   Admin routes found:")
        for route in admin_routes:
            print(f"     • {route}")
    else:
        print("   ❌ No admin routes found")
        
except Exception as e:
    print(f"\n❌ Main app import failed: {e}")
