#!/usr/bin/env python3
"""
Quick API Test - Check if production API is working and has data
"""

import requests
import json

def test_api():
    base_url = "https://ecotrack-online.onrender.com/api/v1"
    
    print("🔍 Testing EcoTrack Production API...")
    print(f"📡 Base URL: {base_url}")
    print("=" * 50)
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/challenges", "Challenges"),
        ("/community/stats/global", "Global stats"),
        ("/activities", "Activities")
    ]
    
    for endpoint, description in endpoints:
        try:
            print(f"\n🌐 Testing {description} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ Success: {len(data)} items found")
                        if len(data) > 0:
                            print(f"Sample: {json.dumps(data[0], indent=2)[:200]}...")
                    elif isinstance(data, dict):
                        print(f"✅ Success: Data object received")
                        print(f"Keys: {list(data.keys())}")
                    else:
                        print(f"✅ Success: {type(data)} received")
                except json.JSONDecodeError:
                    print(f"✅ Success: Non-JSON response (length: {len(response.text)})")
                    print(f"Content preview: {response.text[:200]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout - Server might be sleeping")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API test completed!")

if __name__ == "__main__":
    test_api()
