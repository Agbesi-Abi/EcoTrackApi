#!/usr/bin/env python3
"""
Test login functionality with demo accounts
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def test_login():
    """Test login with demo accounts"""
    
    # Use the production API URL or localhost
    api_url = "https://ecotrack-online.onrender.com/api/v1"
    
    print("🔐 Testing Login Functionality")
    print("=" * 40)
    
    # Test accounts
    test_accounts = [
        {"email": "admin@ecotrack.gh", "password": "admin123", "name": "Admin"},
        {"email": "kwame.test@gmail.com", "password": "password123", "name": "Kwame"},
        {"email": "ama.demo@gmail.com", "password": "password123", "name": "Ama"},
    ]
    
    for account in test_accounts:
        print(f"\n🧪 Testing login for {account['name']} ({account['email']})...")
        
        try:
            # Prepare login data (FastAPI expects form data for OAuth2)
            login_data = {
                "username": account["email"],  # FastAPI OAuth2 uses 'username' field
                "password": account["password"]
            }
            
            # Make login request
            response = requests.post(
                f"{api_url}/auth/login",
                data=login_data,  # Use data for form submission
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login successful!")
                print(f"   🎫 Access token received: {data.get('access_token', 'N/A')[:20]}...")
                print(f"   🔄 Refresh token received: {data.get('refresh_token', 'N/A')[:20]}...")
                
                # Test getting current user
                if 'access_token' in data:
                    headers = {"Authorization": f"Bearer {data['access_token']}"}
                    me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=5)
                    
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print(f"   👤 User data: {user_data.get('name', 'N/A')} - {user_data.get('email', 'N/A')}")
                    else:
                        print(f"   ⚠️  Could not fetch user data: {me_response.status_code}")
                
            else:
                print(f"   ❌ Login failed!")
                try:
                    error_data = response.json()
                    print(f"   📝 Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   📝 Error: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - API server might be down")
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timeout - API server slow to respond")
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
    
    # Test health endpoint
    print(f"\n🏥 Testing API Health...")
    try:
        health_response = requests.get("https://ecotrack-online.onrender.com/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ API Health: {health_data.get('status', 'unknown')}")
            print(f"   📊 Database: {health_data.get('database_type', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")

if __name__ == "__main__":
    test_login()
