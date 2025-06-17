#!/usr/bin/env python3
"""
Script to create an admin user for the EcoTrack Admin Dashboard
"""

import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, User, init_db
from auth.utils import get_password_hash

def create_admin_user():
    """Create an admin user for the dashboard"""
    
    print("🔧 Creating Admin User for EcoTrack Ghana")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if any admin users exist
        admin_count = db.query(User).filter(User.role.in_(['admin', 'super_admin'])).count()
        
        if admin_count > 0:
            print(f"✅ Admin users already exist ({admin_count} found)")
            
            # List existing admins
            admins = db.query(User).filter(User.role.in_(['admin', 'super_admin'])).all()
            print("\n📋 Existing Admin Users:")
            for admin in admins:
                print(f"  • {admin.email} ({admin.role}) - {admin.name}")
            
            return True
        
        # Create super admin user
        admin_email = "admin@ecotrack.com"
        admin_password = "admin123456"
        admin_name = "Super Admin"
        
        # Check if user with this email already exists
        existing_user = db.query(User).filter(User.email == admin_email).first()
        if existing_user:
            # Update existing user to admin
            existing_user.role = "super_admin"
            existing_user.permissions = "full"
            existing_user.is_verified = True
            existing_user.is_active = True
            db.commit()
            print(f"✅ Updated existing user {admin_email} to super admin")
        else:
            # Create new admin user
            hashed_password = get_password_hash(admin_password)
            
            # Use raw SQL for better compatibility
            query = text("""
                INSERT INTO users (
                    email, name, hashed_password, location, region, 
                    role, permissions, is_verified, is_active,
                    total_points, weekly_points, rank
                )
                VALUES (
                    :email, :name, :password, :location, :region,
                    :role, :permissions, :is_verified, :is_active,
                    :total_points, :weekly_points, :rank
                )
            """)
            
            db.execute(query, {
                'email': admin_email,
                'name': admin_name,
                'password': hashed_password,
                'location': 'Admin Location',
                'region': 'Admin Region',
                'role': 'super_admin',
                'permissions': 'full',
                'is_verified': True,
                'is_active': True,
                'total_points': 0,
                'weekly_points': 0,
                'rank': 0
            })
            
            db.commit()
            print(f"✅ Created super admin user: {admin_email}")
        
        print(f"\n🔑 Admin Login Credentials:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"\n🌐 Login at: http://localhost:3000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_admin_user()
    if success:
        print("\n✅ Admin user setup completed successfully!")
    else:
        print("\n❌ Admin user setup failed!")
        sys.exit(1)
