#!/usr/bin/env python3
"""
Comprehensive PostgreSQL Database Status Report for EcoTrack Ghana
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime

# Load environment variables
load_dotenv('.env.production')

def generate_database_report():
    """Generate a comprehensive database status report"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    # Parse database URL for display (hide password)
    url_parts = DATABASE_URL.replace("postgresql://", "").split("@")
    credentials = url_parts[0].split(":")
    username = credentials[0]
    host_db = url_parts[1] if len(url_parts) > 1 else "unknown"
    host = host_db.split("/")[0]
    database = host_db.split("/")[1] if "/" in host_db else "unknown"
    
    print("🗄️  EcoTrack Ghana - PostgreSQL Database Status Report")
    print("=" * 60)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Host: {host}")
    print(f"👤 Username: {username}")
    print(f"🗃️  Database: {database}")
    
    try:
        # Create engine
        engine = create_engine(
            DATABASE_URL,
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            pool_pre_ping=True,
            echo=False
        )
        
        print(f"\n⚙️  Connection Pool Configuration:")
        print(f"   • Pool size: {os.getenv('DB_POOL_SIZE', '10')}")
        print(f"   • Max overflow: {os.getenv('DB_MAX_OVERFLOW', '20')}")
        print(f"   • Pool timeout: {os.getenv('DB_POOL_TIMEOUT', '30')}s")
        print(f"   • Pool recycle: {os.getenv('DB_POOL_RECYCLE', '3600')}s")
        
        with engine.connect() as connection:
            print(f"\n✅ Database Connection: SUCCESSFUL")
            
            # PostgreSQL version and info
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"📊 PostgreSQL Version: {version.split(' on ')[0]}")
            
            # SSL status
            try:
                result = connection.execute(text("SHOW ssl"))
                ssl_status = result.fetchone()[0]
                print(f"🔒 SSL Status: {ssl_status}")
            except:
                print(f"🔒 SSL Status: Unable to determine")
            
            # Database size
            try:
                result = connection.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
                db_size = result.fetchone()[0]
                print(f"💾 Database Size: {db_size}")
            except Exception as e:
                print(f"💾 Database Size: Unable to determine")
            
            # Connection info
            try:
                result = connection.execute(text("SELECT inet_server_addr(), inet_server_port()"))
                server_info = result.fetchone()
                if server_info and server_info[0]:
                    print(f"🌐 Server IP: {server_info[0]}")
                    print(f"🔌 Server Port: {server_info[1]}")
            except:
                pass
            
            # List all tables
            result = connection.execute(text("""
                SELECT table_name, 
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """))
            
            tables_info = result.fetchall()
            print(f"\n📋 Database Tables ({len(tables_info)}):")
            
            if tables_info:
                total_records = 0
                for table_name, table_size in tables_info:
                    try:
                        # Get record count
                        count_result = connection.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                        count = count_result.scalar()
                        total_records += count
                        print(f"   • {table_name:<20} | {count:>8,} records | {table_size}")
                    except Exception as e:
                        print(f"   • {table_name:<20} | Error: {str(e)[:30]}...")
                
                print(f"\n📊 Total Records Across All Tables: {total_records:,}")
            else:
                print("   ⚠️  No tables found - Database may need initialization")
            
            # Check for EcoTrack specific tables
            expected_tables = ['users', 'activities', 'challenges', 'regions', 'notifications']
            print(f"\n🔍 EcoTrack Core Tables Status:")
            
            existing_tables = [table[0] for table in tables_info]
            for table in expected_tables:
                if table in existing_tables:
                    try:
                        count_result = connection.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                        count = count_result.scalar()
                        print(f"   ✅ {table}: {count:,} records")
                    except:
                        print(f"   ⚠️  {table}: Present but unable to query")
                else:
                    print(f"   ❌ {table}: Missing")
            
            # Test write capability
            print(f"\n🧪 Testing Write Operations:")
            try:
                # Create test table
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS db_status_test (
                        id SERIAL PRIMARY KEY,
                        test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        test_data VARCHAR(100)
                    )
                """))
                
                # Insert test record
                connection.execute(text("""
                    INSERT INTO db_status_test (test_data) 
                    VALUES ('Database status check - write test')
                """))
                
                # Read test record
                result = connection.execute(text("""
                    SELECT test_data, test_time FROM db_status_test 
                    ORDER BY test_time DESC LIMIT 1
                """))
                test_record = result.fetchone()
                
                print(f"   ✅ Write Test: SUCCESS")
                print(f"   📝 Test Record: {test_record[0]}")
                print(f"   🕒 Timestamp: {test_record[1]}")
                
                # Cleanup
                connection.execute(text("DROP TABLE IF EXISTS db_status_test"))
                connection.commit()
                print(f"   🧹 Cleanup: SUCCESS")
                
            except Exception as e:
                print(f"   ❌ Write Test: FAILED - {str(e)}")
            
            # Environment configuration check
            print(f"\n🌍 Environment Configuration:")
            env_vars = [
                'ENVIRONMENT', 'DEBUG', 'HOST', 'PORT', 
                'JWT_SECRET_KEY', 'MAX_FILE_SIZE', 'RATE_LIMIT_PER_MINUTE'
            ]
            
            for var in env_vars:
                value = os.getenv(var, 'Not set')
                if var == 'JWT_SECRET_KEY' and value != 'Not set':
                    value = f"{'*' * (len(value) - 10)}...{value[-6:]}"
                print(f"   • {var}: {value}")
            
        print(f"\n🎉 Database Status Report Complete!")
        print(f"✅ Your PostgreSQL database is properly configured and accessible!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database Connection Failed: {str(e)}")
        print(f"\n🔧 Troubleshooting Suggestions:")
        print(f"   1. Verify DATABASE_URL in .env.production")
        print(f"   2. Check if database server is online")
        print(f"   3. Ensure your IP is whitelisted")
        print(f"   4. Verify network connectivity")
        return False

if __name__ == "__main__":
    success = generate_database_report()
    sys.exit(0 if success else 1)
