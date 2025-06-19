#!/usr/bin/env python3
"""
Comprehensive Admin User Seeding Script for EcoTrack Ghana
Creates multiple admin users with different roles and permissions
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Load environment variables
load_dotenv('.env.production')

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, init_db
from auth.utils import get_password_hash

class AdminUserSeeder:
    """Admin user seeding class with comprehensive admin management"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.admin_users = [
            {
                "email": "superadmin@ecotrack.gh",
                "name": "Super Administrator",
                "password": "SuperAdmin123!",
                "role": "super_admin",
                "permissions": "full",
                "location": "Accra, Greater Accra",
                "region": "Greater Accra",
                "description": "System Super Admin with full access"
            },
            {
                "email": "admin@ecotrack.gh",
                "name": "System Administrator",
                "password": "Admin123!",
                "role": "admin",
                "permissions": "full",
                "location": "Kumasi, Ashanti",
                "region": "Ashanti",
                "description": "Main System Admin"
            },
            {
                "email": "moderator@ecotrack.gh",
                "name": "Content Moderator",
                "password": "Moderator123!",
                "role": "admin",
                "permissions": "moderate",
                "location": "Cape Coast, Central",
                "region": "Central",
                "description": "Content moderation and user management"
            },
            {
                "email": "analytics@ecotrack.gh",
                "name": "Analytics Manager",
                "password": "Analytics123!",
                "role": "admin",
                "permissions": "analytics",
                "location": "Tamale, Northern",
                "region": "Northern",
                "description": "Data analytics and reporting"
            },
            {
                "email": "support@ecotrack.gh",
                "name": "Support Administrator",
                "password": "Support123!",
                "role": "admin",
                "permissions": "support",
                "location": "Ho, Volta",
                "region": "Volta",
                "description": "User support and customer service"
            },
            {
                "email": "demo.admin@ecotrack.gh",
                "name": "Demo Administrator",
                "password": "DemoAdmin123!",
                "role": "admin",
                "permissions": "demo",
                "location": "Sekondi-Takoradi, Western",
                "region": "Western",
                "description": "Demo and testing admin account"
            }
        ]

    def check_database_connection(self):
        """Test database connection"""
        try:
            self.db.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def initialize_database(self):
        """Initialize database schema if needed"""
        try:
            print("📋 Initializing database schema...")
            init_db()
            print("✅ Database schema initialized")
            return True
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False

    def check_existing_admins(self):
        """Check for existing admin users"""
        try:
            # Count existing admin users
            admin_count = self.db.query(User).filter(
                User.role.in_(['admin', 'super_admin'])
            ).count()
            
            if admin_count > 0:
                print(f"📋 Found {admin_count} existing admin users:")
                admins = self.db.query(User).filter(
                    User.role.in_(['admin', 'super_admin'])
                ).all()
                
                for admin in admins:
                    status = "ACTIVE" if admin.is_active else "INACTIVE"
                    verified = "VERIFIED" if admin.is_verified else "UNVERIFIED"
                    print(f"  • {admin.email} ({admin.role}) - {status}, {verified}")
                print()
            
            return admin_count
        except Exception as e:
            print(f"❌ Error checking existing admins: {e}")
            return 0

    def create_admin_user(self, admin_data):
        """Create or update a single admin user"""
        try:
            email = admin_data["email"]
            
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == email).first()
            
            if existing_user:
                # Update existing user to admin role
                existing_user.role = admin_data["role"]
                existing_user.permissions = admin_data["permissions"]
                existing_user.is_verified = True
                existing_user.is_active = True
                existing_user.location = admin_data["location"]
                existing_user.region = admin_data["region"]
                existing_user.updated_at = datetime.utcnow()
                
                # Update password if it's a demo/default account
                if "demo" in email or "admin" in email:
                    existing_user.hashed_password = get_password_hash(admin_data["password"])
                
                self.db.commit()
                print(f"🔄 Updated existing user: {email} -> {admin_data['role']}")
                return "updated"
            else:
                # Create new admin user
                hashed_password = get_password_hash(admin_data["password"])
                
                # Use raw SQL for better compatibility
                query = text("""
                    INSERT INTO users (
                        email, name, hashed_password, location, region, 
                        role, permissions, is_verified, is_active,
                        total_points, weekly_points, rank,
                        created_at, updated_at
                    )
                    VALUES (
                        :email, :name, :password, :location, :region,
                        :role, :permissions, :is_verified, :is_active,
                        :total_points, :weekly_points, :rank,
                        :created_at, :updated_at
                    )
                """)
                
                self.db.execute(query, {
                    'email': email,
                    'name': admin_data['name'],
                    'password': hashed_password,
                    'location': admin_data['location'],
                    'region': admin_data['region'],
                    'role': admin_data['role'],
                    'permissions': admin_data['permissions'],
                    'is_verified': True,
                    'is_active': True,
                    'total_points': 0,
                    'weekly_points': 0,
                    'rank': 0,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                })
                
                self.db.commit()
                print(f"✅ Created new admin user: {email} ({admin_data['role']})")
                return "created"
                
        except Exception as e:
            print(f"❌ Error creating admin {admin_data['email']}: {e}")
            self.db.rollback()
            return "error"

    def seed_admin_users(self):
        """Seed all admin users"""
        print("👑 Seeding Admin Users for EcoTrack Ghana")
        print("=" * 55)
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for admin_data in self.admin_users:
            result = self.create_admin_user(admin_data)
            if result == "created":
                created_count += 1
            elif result == "updated":
                updated_count += 1
            else:
                error_count += 1
        
        print(f"\n📊 Admin User Seeding Summary:")
        print(f"   ✅ Created: {created_count} new admin users")
        print(f"   🔄 Updated: {updated_count} existing users")
        print(f"   ❌ Errors: {error_count} failed operations")
        
        return created_count + updated_count > 0

    def verify_admin_users(self):
        """Verify all admin users were created successfully"""
        print("\n🔍 Verifying Admin User Creation:")
        print("=" * 40)
        
        success_count = 0
        for admin_data in self.admin_users:
            try:
                user = self.db.query(User).filter(User.email == admin_data["email"]).first()
                if user and user.role in ['admin', 'super_admin']:
                    status = "ACTIVE" if user.is_active else "INACTIVE"
                    verified = "VERIFIED" if user.is_verified else "UNVERIFIED"
                    print(f"✅ {user.email} - {user.role} ({status}, {verified})")
                    success_count += 1
                else:
                    print(f"❌ {admin_data['email']} - NOT FOUND OR INVALID ROLE")
            except Exception as e:
                print(f"❌ {admin_data['email']} - ERROR: {e}")
        
        print(f"\n✅ Successfully verified {success_count}/{len(self.admin_users)} admin users")
        return success_count == len(self.admin_users)

    def print_admin_credentials(self):
        """Print admin login credentials for reference"""
        print("\n🔑 Admin Login Credentials:")
        print("=" * 50)
        print("📧 Email | Password | Role | Permissions")
        print("-" * 50)
        
        for admin_data in self.admin_users:
            print(f"📧 {admin_data['email']}")
            print(f"   🔐 Password: {admin_data['password']}")
            print(f"   👤 Role: {admin_data['role']}")
            print(f"   🛡️  Permissions: {admin_data['permissions']}")
            print(f"   📍 Location: {admin_data['location']}")
            print(f"   📝 Description: {admin_data['description']}")
            print()

    def get_admin_dashboard_info(self):
        """Get admin dashboard access information"""
        print("\n🌐 Admin Dashboard Access:")
        print("=" * 40)
        print("🖥️  Local Development: http://localhost:3000")
        print("🌍 Production: https://your-admin-panel-url.com")
        print()
        print("🔧 Admin Panel Features:")
        print("  • User Management & Verification")
        print("  • Activity Moderation & Approval")
        print("  • Challenge Creation & Management")
        print("  • Analytics & Reporting")
        print("  • Database Administration")
        print("  • Content Moderation")
        print()

    def run_complete_seeding(self):
        """Run the complete admin user seeding process"""
        try:
            print("🌍 EcoTrack Ghana - Admin User Seeding")
            print("=" * 60)
            
            # Step 1: Check database connection
            if not self.check_database_connection():
                return False
            
            # Step 2: Initialize database schema
            if not self.initialize_database():
                return False
            
            # Step 3: Check existing admin users
            existing_count = self.check_existing_admins()
            
            # Step 4: Seed admin users
            if not self.seed_admin_users():
                print("❌ Admin user seeding failed!")
                return False
            
            # Step 5: Verify admin users
            if not self.verify_admin_users():
                print("⚠️  Some admin users may not have been created correctly")
            
            # Step 6: Print credentials and info
            self.print_admin_credentials()
            self.get_admin_dashboard_info()
            
            print("\n🎉 Admin User Seeding Completed Successfully!")
            print("🚀 Your EcoTrack Ghana admin panel is ready!")
            
            return True
            
        except Exception as e:
            print(f"❌ Fatal error during admin seeding: {e}")
            return False
        finally:
            self.db.close()

def main():
    """Main entry point"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        print("💡 Make sure .env.production file is configured correctly")
        sys.exit(1)
    
    print(f"🔗 Database: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'Local Database'}")
    print()
    
    seeder = AdminUserSeeder()
    success = seeder.run_complete_seeding()
    
    if not success:
        print("\n❌ Admin user seeding failed!")
        sys.exit(1)
    else:
        print("\n✅ Admin user seeding completed successfully!")
        print("🔧 You can now access the admin panel with any of the credentials above.")

if __name__ == "__main__":
    main()
