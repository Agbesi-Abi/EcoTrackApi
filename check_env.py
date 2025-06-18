#!/usr/bin/env python3
"""
Quick verification that environment variables are working
"""

import os
from dotenv import load_dotenv

def main():
    print("🔍 Environment Variable Check")
    print("=" * 35)
    
    # Try loading from file first
    load_dotenv('.env.production')
    
    db_url = os.getenv('DATABASE_URL')
    environment = os.getenv('ENVIRONMENT', 'development')
    
    print(f"Environment: {environment}")
    
    if db_url:
        if db_url.startswith('postgresql'):
            print("✅ PostgreSQL URL found")
            # Hide password
            display_url = db_url.split('@')[0].split(':')[:-1]
            display_url = ':'.join(display_url) + ':***@' + db_url.split('@')[1] if '@' in db_url else db_url
            print(f"🔗 Database: {display_url}")
        else:
            print("⚠️  Non-PostgreSQL database URL found")
            print(f"🔗 Database: {db_url}")
    else:
        print("❌ No DATABASE_URL found")
        print("This will cause the app to use SQLite fallback")
    
    print(f"\nOther important variables:")
    print(f"  DEBUG: {os.getenv('DEBUG', 'Not set')}")
    print(f"  ENABLE_ADMIN: {os.getenv('ENABLE_ADMIN', 'Not set')}")
    print(f"  DB_POOL_SIZE: {os.getenv('DB_POOL_SIZE', 'Not set')}")

if __name__ == "__main__":
    main()
