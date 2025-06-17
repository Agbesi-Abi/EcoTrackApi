"""
Create test users for role-based access control testing
"""

import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User
from auth.utils import get_password_hash

def create_test_users():
    """Create test users for different roles"""
    db = SessionLocal()
    
    try:
        # Test users to create
        test_users = [
            {
                "email": "superadmin@ecotrack.com",
                "name": "Super Admin",
                "password": "superadmin123",
                "role": "super_admin",
                "permissions": "full",
                "location": "Accra, Ghana",
                "region": "Greater Accra"
            },
            {
                "email": "admin@ecotrack.com", 
                "name": "Regular Admin",
                "password": "admin123",
                "role": "admin",
                "permissions": "basic",
                "location": "Kumasi, Ghana", 
                "region": "Ashanti"
            },
            {
                "email": "user@ecotrack.com",
                "name": "Regular User",
                "password": "user123", 
                "role": "user",
                "permissions": "basic",
                "location": "Cape Coast, Ghana",
                "region": "Central"
            }
        ]
        
        print("🔧 Creating test users for role-based access control...")
        print("=" * 60)
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                print(f"⚠️  User {user_data['email']} already exists - updating role and permissions")
                existing_user.role = user_data["role"]
                existing_user.permissions = user_data["permissions"]
                existing_user.is_active = True
                existing_user.is_verified = True
                db.commit()
                db.refresh(existing_user)
                print(f"   ✅ Updated: {existing_user.name} ({existing_user.role})")
            else:
                # Create new user
                hashed_password = get_password_hash(user_data["password"])
                
                new_user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    hashed_password=hashed_password,
                    role=user_data["role"],
                    permissions=user_data["permissions"],
                    location=user_data["location"],
                    region=user_data["region"],
                    is_active=True,
                    is_verified=True,
                    total_points=0,
                    weekly_points=0,
                    rank=0,
                    trash_collected=0.0,
                    trees_planted=0,
                    co2_saved=0.0
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                print(f"   ✅ Created: {new_user.name} ({new_user.role})")
        
        print("\n📋 Test User Summary:")
        print("-" * 30)
        print("Super Admin:")
        print("  Email: superadmin@ecotrack.com")
        print("  Password: superadmin123")
        print("  Role: super_admin")
        print("  Access: All admin endpoints")
        print()
        print("Regular Admin:")
        print("  Email: admin@ecotrack.com")
        print("  Password: admin123") 
        print("  Role: admin")
        print("  Access: User verification only")
        print()
        print("Regular User:")
        print("  Email: user@ecotrack.com")
        print("  Password: user123")
        print("  Role: user") 
        print("  Access: No admin endpoints")
        
        print("\n✅ Test users created successfully!")
        print("You can now run: python test_role_based_access.py")
        
    except Exception as e:
        print(f"❌ Error creating test users: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def list_existing_admin_users():
    """List existing admin users"""
    db = SessionLocal()
    
    try:
        print("\n👥 Existing Admin Users:")
        print("-" * 40)
        
        admin_users = db.query(User).filter(User.role.in_(["admin", "super_admin"])).all()
        
        if not admin_users:
            print("No admin users found.")
        else:
            for user in admin_users:
                status = "✅ Active" if user.is_active else "❌ Inactive"
                verified = "✅ Verified" if user.is_verified else "❌ Unverified"
                print(f"  • {user.name} ({user.email})")
                print(f"    Role: {user.role}")
                print(f"    Permissions: {user.permissions}")
                print(f"    Status: {status}")
                print(f"    Verified: {verified}")
                print(f"    Created: {user.created_at}")
                print()
                
    except Exception as e:
        print(f"❌ Error listing admin users: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🌍 EcoTrack Ghana - Test User Creation")
    print("=" * 50)
    
    # List existing admin users first
    list_existing_admin_users()
    
    # Create test users
    if create_test_users():
        print("\n🎯 Next Steps:")
        print("1. Start the backend server:")
        print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print()
        print("2. Run the access control tests:")
        print("   python test_role_based_access.py")
        print()
        print("3. Test the frontend with different user roles")
    else:
        print("❌ Failed to create test users")
        sys.exit(1)
