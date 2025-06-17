#!/usr/bin/env python3
"""
Comprehensive diagnostic for login issues
"""

import os
import sys
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('.env.production')

def full_diagnostic():
    """Run full diagnostic for login issues"""
    
    print("🔍 EcoTrack Ghana - Login Diagnostic")
    print("=" * 50)
    
    # 1. Check environment configuration
    print("\n📋 1. Environment Configuration")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        db_host = DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'unknown'
        print(f"   ✅ DATABASE_URL configured: {db_host}")
    else:
        print("   ❌ DATABASE_URL not found")
        return False
    
    # 2. Test database connection
    print("\n🗄️  2. Database Connection")
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("   ✅ Database connection successful")
                
                # Check if users table exists
                tables = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'users'
                """)).fetchall()
                
                if tables:
                    print("   ✅ Users table exists")
                    
                    # Count users
                    user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                    print(f"   📊 Total users: {user_count}")
                    
                    # Check specific demo users
                    demo_emails = ['admin@ecotrack.gh', 'kwame.test@gmail.com', 'ama.demo@gmail.com']
                    for email in demo_emails:
                        user = conn.execute(text("""
                            SELECT name, is_active, hashed_password 
                            FROM users 
                            WHERE email = :email
                        """), {"email": email}).fetchone()
                        
                        if user:
                            status = "✅ ACTIVE" if user[1] else "❌ INACTIVE"
                            has_password = "✅ HAS PASSWORD" if user[2] else "❌ NO PASSWORD"
                            print(f"   {status} {email} - {user[0]} - {has_password}")
                        else:
                            print(f"   ❌ MISSING {email}")
                else:
                    print("   ❌ Users table does not exist")
                    return False
            else:
                print("   ❌ Database connection failed")
                return False
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # 3. Test API health
    print("\n🏥 3. API Health Check")
    try:
        health_response = requests.get("https://ecotrack-online.onrender.com/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ API Status: {health_data.get('status', 'unknown')}")
            print(f"   📊 Database Type: {health_data.get('database_type', 'unknown')}")
            print(f"   🌍 Environment: {health_data.get('environment', 'unknown')}")
        else:
            print(f"   ❌ API health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API health error: {e}")
        return False
    
    # 4. Test authentication endpoint
    print("\n🔐 4. Authentication Endpoint Test")
    try:
        # Test with a known demo account
        login_data = {
            "username": "admin@ecotrack.gh",
            "password": "admin123"
        }
        
        login_response = requests.post(
            "https://ecotrack-online.onrender.com/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )
        
        print(f"   📡 Login attempt status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            data = login_response.json()
            print("   ✅ Login endpoint working correctly")
            print(f"   🎫 Token received: {data.get('access_token', 'N/A')[:20]}...")
            
            # Test getting current user
            if 'access_token' in data:
                headers = {"Authorization": f"Bearer {data['access_token']}"}
                me_response = requests.get(
                    "https://ecotrack-online.onrender.com/api/v1/auth/me", 
                    headers=headers, 
                    timeout=10
                )
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"   👤 User verification: {user_data.get('name', 'N/A')} ({user_data.get('email', 'N/A')})")
                    print("   ✅ Full authentication flow working")
                else:
                    print(f"   ⚠️  User verification failed: {me_response.status_code}")
        else:
            try:
                error_data = login_response.json()
                print(f"   ❌ Login failed: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   ❌ Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Authentication test error: {e}")
        return False
    
    # 5. Summary
    print("\n📋 5. Diagnostic Summary")
    print("   ✅ Database connection: Working")
    print("   ✅ Users table: Present with data")
    print("   ✅ API health: Healthy")
    print("   ✅ Authentication: Functional")
    print("\n🎉 All systems appear to be working correctly!")
    
    print("\n🔑 Ready to test with these accounts:")
    print("   📧 admin@ecotrack.gh (password: admin123)")
    print("   📧 kwame.test@gmail.com (password: password123)")
    print("   📧 ama.demo@gmail.com (password: password123)")
    
    return True

if __name__ == "__main__":
    success = full_diagnostic()
    
    if not success:
        print("\n❌ Issues detected! Check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ System ready for login testing!")
