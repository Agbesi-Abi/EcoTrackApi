#!/usr/bin/env python3
"""
Check registered routes in the FastAPI app
"""

import os
os.environ['ENABLE_ADMIN'] = 'true'
os.environ['ENABLE_DOCS'] = 'true'

from main import app

print("🔍 Checking Registered Routes")
print("=" * 50)

admin_routes = []
all_routes = []

for route in app.routes:
    route_info = f"{route.methods} {route.path}" if hasattr(route, 'methods') else f"- {route.path}"
    all_routes.append(route_info)
    
    if '/admin' in route.path:
        admin_routes.append(route_info)

print(f"📋 Total Routes: {len(all_routes)}")
print(f"🔧 Admin Routes: {len(admin_routes)}")

if admin_routes:
    print("\n✅ Admin Routes Found:")
    for route in admin_routes:
        print(f"  • {route}")
else:
    print("\n❌ No Admin Routes Found!")

print(f"\n📋 All Routes:")
for route in all_routes:
    print(f"  • {route}")
