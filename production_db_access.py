#!/usr/bin/env python3
"""
Production Database Access Tool for EcoTrack Ghana
Access and manage the production SQLite database
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# Production database path
PROD_DB_PATH = "ecotrack_ghana.db"

class ProductionDBManager:
    def __init__(self, db_path=PROD_DB_PATH):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Check if database exists"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found at: {self.db_path}")
            print("Make sure you're in the correct directory or the database has been created.")
            return False
        return True
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def list_tables(self):
        """List all tables in the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print("📋 Available Tables:")
            print("-" * 40)
            for table in tables:
                print(f"  • {table[0]}")
            return [table[0] for table in tables]
    
    def describe_table(self, table_name):
        """Show table structure"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"\n📊 Table Structure: {table_name}")
            print("-" * 50)
            print(f"{'Column':<20} {'Type':<15} {'Not Null':<10} {'Default'}")
            print("-" * 50)
            for col in columns:
                print(f"{col[1]:<20} {col[2]:<15} {col[3]:<10} {col[4]}")
    
    def count_records(self, table_name):
        """Count records in table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"📈 {table_name}: {count} records")
            return count
    
    def show_recent_records(self, table_name, limit=5):
        """Show recent records from table"""
        with self.get_connection() as conn:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT {limit};", conn)
                print(f"\n🔍 Recent {limit} records from {table_name}:")
                print("-" * 60)
                print(df.to_string())
            except Exception as e:
                print(f"❌ Error reading {table_name}: {e}")
    
    def execute_query(self, query):
        """Execute custom SQL query"""
        with self.get_connection() as conn:
            try:
                if query.strip().lower().startswith('select'):
                    df = pd.read_sql_query(query, conn)
                    print("\n📊 Query Results:")
                    print("-" * 60)
                    print(df.to_string())
                    return df
                else:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    print(f"✅ Query executed successfully. Rows affected: {cursor.rowcount}")
            except Exception as e:
                print(f"❌ Query error: {e}")
    
    def backup_database(self):
        """Create a backup of the database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"ecotrack_ghana_backup_{timestamp}.db"
        
        try:
            with self.get_connection() as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            print(f"✅ Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    def get_database_stats(self):
        """Get overall database statistics"""
        print("\n🏢 EcoTrack Ghana - Production Database Statistics")
        print("=" * 60)
        
        tables = self.list_tables()
        total_records = 0
        
        print(f"\n📊 Record Counts:")
        print("-" * 30)
        for table in tables:
            count = self.count_records(table)
            total_records += count
        
        print(f"\n📈 Total Records: {total_records}")
        
        # Database file size
        if os.path.exists(self.db_path):
            size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
            print(f"💾 Database Size: {size_mb:.2f} MB")
    
    def show_user_summary(self):
        """Show user summary"""
        query = """
        SELECT 
            COUNT(*) as total_users,
            COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_users,
            AVG(total_points) as avg_points,
            MAX(total_points) as max_points,
            MIN(created_at) as first_user,
            MAX(created_at) as latest_user
        FROM users;
        """
        self.execute_query(query)
    
    def show_activity_summary(self):
        """Show activity summary"""
        query = """
        SELECT 
            type,
            COUNT(*) as count,
            AVG(points) as avg_points,
            SUM(points) as total_points
        FROM activities 
        GROUP BY type 
        ORDER BY count DESC;
        """
        self.execute_query(query)

def main():
    """Main interactive interface"""
    db = ProductionDBManager()
    
    print("🌍 EcoTrack Ghana - Production Database Access Tool")
    print("=" * 60)
    
    while True:
        print("\n📋 Available Commands:")
        print("1. Show database statistics")
        print("2. List all tables")
        print("3. Describe table structure")
        print("4. Show recent records")
        print("5. Execute custom query")
        print("6. Show user summary")
        print("7. Show activity summary")
        print("8. Backup database")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == "1":
            db.get_database_stats()
        
        elif choice == "2":
            db.list_tables()
        
        elif choice == "3":
            table_name = input("Enter table name: ").strip()
            db.describe_table(table_name)
        
        elif choice == "4":
            table_name = input("Enter table name: ").strip()
            limit = input("Number of records (default 5): ").strip()
            limit = int(limit) if limit else 5
            db.show_recent_records(table_name, limit)
        
        elif choice == "5":
            query = input("Enter SQL query: ").strip()
            db.execute_query(query)
        
        elif choice == "6":
            db.show_user_summary()
        
        elif choice == "7":
            db.show_activity_summary()
        
        elif choice == "8":
            db.backup_database()
        
        elif choice == "9":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
