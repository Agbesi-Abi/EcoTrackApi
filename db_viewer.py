#!/usr/bin/env python3
"""
Database Viewer for EcoTrack Ghana
Simple script to view and query database data
"""

import os
from sqlalchemy.orm import sessionmaker
from database import engine, User, Activity, Challenge, Region, challenge_participants

# Create session
Session = sessionmaker(bind=engine)
session = Session()

def view_all_tables():
    """Display data from all tables"""
    print("🗄️  EcoTrack Ghana Database Viewer")
    print("=" * 50)
    
    # Regions
    print("\n📍 REGIONS:")
    regions = session.query(Region).all()
    if regions:
        print(f"{'ID':<3} {'Name':<15} {'Capital':<15} {'Code':<4} {'Population':<10}")
        print("-" * 50)
        for region in regions:
            print(f"{region.id:<3} {region.name:<15} {region.capital:<15} {region.code:<4} {region.population:<10}")
    else:
        print("No regions found")
    
    # Users
    print("\n👥 USERS:")
    users = session.query(User).all()
    if users:
        print(f"{'ID':<3} {'Name':<20} {'Email':<25} {'Location':<15} {'Points':<6}")
        print("-" * 70)
        for user in users:
            print(f"{user.id:<3} {user.name:<20} {user.email:<25} {(user.location or 'N/A'):<15} {user.total_points:<6}")
    else:
        print("No users found")
    
    # Activities
    print("\n🌱 ACTIVITIES:")
    activities = session.query(Activity).all()
    if activities:
        print(f"{'ID':<3} {'User':<15} {'Type':<10} {'Title':<30} {'Points':<6}")
        print("-" * 65)
        for activity in activities:
            user_name = activity.user.name if activity.user else "Unknown"
            title = activity.title[:27] + "..." if len(activity.title) > 30 else activity.title
            print(f"{activity.id:<3} {user_name:<15} {activity.type:<10} {title:<30} {activity.points:<6}")
    else:
        print("No activities found")
    
    # Challenges
    print("\n🏆 CHALLENGES:")
    challenges = session.query(Challenge).all()
    if challenges:
        print(f"{'ID':<3} {'Title':<30} {'Category':<10} {'Points':<6} {'Active':<6}")
        print("-" * 56)
        for challenge in challenges:
            title = challenge.title[:27] + "..." if len(challenge.title) > 30 else challenge.title
            print(f"{challenge.id:<3} {title:<30} {challenge.category:<10} {challenge.points:<6} {challenge.is_active}")
    else:
        print("No challenges found")

def view_user_details(user_id=None):
    """View detailed user information"""
    if user_id is None:
        print("\n👤 Select a user:")
        users = session.query(User).all()
        for user in users:
            print(f"{user.id}: {user.name} ({user.email})")
        try:
            user_id = int(input("\nEnter user ID: "))
        except ValueError:
            print("Invalid user ID")
            return
    
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"User with ID {user_id} not found")
        return
    
    print(f"\n👤 USER DETAILS: {user.name}")
    print("=" * 40)
    print(f"Email: {user.email}")
    print(f"Location: {user.location or 'Not specified'}")
    print(f"Region: {user.region or 'Not specified'}")
    print(f"Total Points: {user.total_points}")
    print(f"Weekly Points: {user.weekly_points}")
    print(f"Rank: {user.rank}")
    print(f"Verified: {user.is_verified}")
    print(f"Active: {user.is_active}")
    print(f"Created: {user.created_at}")
    
    # Impact stats
    print(f"\n🌍 ENVIRONMENTAL IMPACT:")
    print(f"Trash Collected: {user.trash_collected} kg")
    print(f"Trees Planted: {user.trees_planted}")
    print(f"CO2 Saved: {user.co2_saved} kg")
    
    # User's activities
    activities = session.query(Activity).filter(Activity.user_id == user_id).all()
    print(f"\n📝 ACTIVITIES ({len(activities)}):")
    if activities:
        for activity in activities[-5:]:  # Show last 5 activities
            print(f"- {activity.type.upper()}: {activity.title} ({activity.points} pts)")
    else:
        print("No activities found")

def search_activities(activity_type=None):
    """Search activities by type"""
    print("\n🔍 ACTIVITY SEARCH")
    
    if activity_type is None:
        print("Available types: trash, trees, mobility, water, energy")
        activity_type = input("Enter activity type (or press Enter for all): ").strip().lower()
    
    query = session.query(Activity)
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    
    activities = query.all()
    
    print(f"\n📊 Found {len(activities)} activities")
    if activity_type:
        print(f"Type: {activity_type}")
    
    for activity in activities:
        user_name = activity.user.name if activity.user else "Unknown"
        print(f"- {activity.id}: {activity.title} by {user_name} ({activity.points} pts)")

def show_statistics():
    """Show database statistics"""
    print("\n📊 DATABASE STATISTICS")
    print("=" * 30)
    
    # Count records
    user_count = session.query(User).count()
    activity_count = session.query(Activity).count()
    challenge_count = session.query(Challenge).count()
    region_count = session.query(Region).count()
    
    print(f"Total Users: {user_count}")
    print(f"Total Activities: {activity_count}")
    print(f"Total Challenges: {challenge_count}")
    print(f"Total Regions: {region_count}")
    
    # Activity type breakdown
    from sqlalchemy import func
    activity_types = session.query(
        Activity.type,
        func.count(Activity.id).label('count')
    ).group_by(Activity.type).all()
    
    print(f"\n📈 ACTIVITY BREAKDOWN:")
    for activity_type, count in activity_types:
        print(f"{activity_type.capitalize()}: {count}")
    
    # Top users by points
    top_users = session.query(User).order_by(User.total_points.desc()).limit(5).all()
    print(f"\n🏆 TOP 5 USERS BY POINTS:")
    for i, user in enumerate(top_users, 1):
        print(f"{i}. {user.name}: {user.total_points} pts")

def interactive_menu():
    """Interactive menu for database exploration"""
    while True:
        print("\n" + "="*50)
        print("🌍 EcoTrack Ghana Database Viewer")
        print("="*50)
        print("1. View all tables")
        print("2. View user details")
        print("3. Search activities")
        print("4. Show statistics")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            view_all_tables()
        elif choice == "2":
            view_user_details()
        elif choice == "3":
            search_activities()
        elif choice == "4":
            show_statistics()
        elif choice == "5":
            print("Goodbye! 🌍")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 🌍")
    finally:
        session.close()
