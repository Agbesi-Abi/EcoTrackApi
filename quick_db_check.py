#!/usr/bin/env python3
"""
Quick database queries for EcoTrack Ghana
"""

from sqlalchemy.orm import sessionmaker
from database import engine, User, Activity, Challenge, Region

# Create session
Session = sessionmaker(bind=engine)
session = Session()

def quick_overview():
    """Quick overview of database contents"""
    print("🌍 EcoTrack Ghana - Quick Database Overview")
    print("=" * 45)
    
    # Check if database has data
    region_count = session.query(Region).count()
    user_count = session.query(User).count()
    activity_count = session.query(Activity).count()
    challenge_count = session.query(Challenge).count()
    
    print(f"📍 Regions: {region_count}")
    print(f"👥 Users: {user_count}")
    print(f"🌱 Activities: {activity_count}")
    print(f"🏆 Challenges: {challenge_count}")
    
    if region_count > 0:
        print(f"\n📍 Sample regions:")
        regions = session.query(Region).limit(3).all()
        for region in regions:
            print(f"   - {region.name} (Capital: {region.capital})")
    
    if user_count > 0:
        print(f"\n👥 Sample users:")
        users = session.query(User).limit(3).all()
        for user in users:
            print(f"   - {user.name} ({user.total_points} points)")
    
    if activity_count > 0:
        print(f"\n🌱 Recent activities:")
        activities = session.query(Activity).order_by(Activity.created_at.desc()).limit(3).all()
        for activity in activities:
            user_name = activity.user.name if activity.user else "Unknown"
            print(f"   - {activity.type}: {activity.title} by {user_name}")
    
    if challenge_count > 0:
        print(f"\n🏆 Active challenges:")
        challenges = session.query(Challenge).filter(Challenge.is_active == True).limit(3).all()
        for challenge in challenges:
            print(f"   - {challenge.title} ({challenge.points} points)")

if __name__ == "__main__":
    try:
        quick_overview()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()
