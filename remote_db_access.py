#!/usr/bin/env python3
"""
Remote Production Database Access
Download and access production database from deployed server
"""

import requests
import sqlite3
import os
from datetime import datetime

class RemoteDBAccess:
    def __init__(self, server_url="https://ecotrack-online.onrender.com"):
        self.server_url = server_url
        self.local_db_path = "production_db_download.db"
    
    def download_database(self):
        """Download database from production server (if endpoint exists)"""
        print(f"🔄 Attempting to download database from {self.server_url}...")
        
        # Check if there's a database download endpoint
        try:
            response = requests.get(f"{self.server_url}/api/v1/admin/download-db")
            if response.status_code == 200:
                with open(self.local_db_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Database downloaded to {self.local_db_path}")
                return True
            else:
                print(f"❌ Database download not available: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def access_via_api(self):
        """Access database data via API endpoints"""
        print("\n🌐 Accessing production data via API...")
        
        endpoints = [
            "/api/v1/community/stats/global",
            "/api/v1/activities?limit=10",
            "/api/v1/challenges?limit=10",
            "/api/v1/community/leaderboard?limit=10"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.server_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n📊 Data from {endpoint}:")
                    print("-" * 50)
                    if isinstance(data, list):
                        print(f"Records: {len(data)}")
                        if data:
                            print(f"Sample: {data[0]}")
                    else:
                        print(f"Data: {data}")
                else:
                    print(f"❌ Failed to fetch {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error fetching {endpoint}: {e}")

def main():
    remote_db = RemoteDBAccess()
    
    print("🌍 EcoTrack Ghana - Remote Production Database Access")
    print("=" * 60)
    
    print("\n1. Access data via API endpoints")
    print("2. Attempt database download (if available)")
    
    choice = input("\nChoose option (1-2): ").strip()
    
    if choice == "1":
        remote_db.access_via_api()
    elif choice == "2":
        if remote_db.download_database():
            # Use the local database access tool
            from production_db_access import ProductionDBManager
            db = ProductionDBManager(remote_db.local_db_path)
            db.get_database_stats()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
