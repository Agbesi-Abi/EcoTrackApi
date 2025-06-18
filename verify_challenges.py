#!/usr/bin/env python3
"""
Verify challenge seeding and display results
"""

import sys
import os
from sqlalchemy.orm import Session

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, Challenge

def verify_challenges():
    """Verify the challenges were seeded correctly"""
    
    print("🔍 Verifying Challenge Database Seeding...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get all challenges
        challenges = db.query(Challenge).all()
        
        print(f"📊 Total challenges found: {len(challenges)}")
        
        if len(challenges) == 0:
            print("❌ No challenges found in database!")
            return
        
        print(f"\n🎯 Challenge Details:")
        print("=" * 80)
        
        for i, challenge in enumerate(challenges, 1):
            print(f"{i}. {challenge.title}")
            print(f"   Category: {challenge.category.title()}")
            print(f"   Difficulty: {challenge.difficulty.title()}")
            print(f"   Points: {challenge.points}")
            print(f"   Duration: {challenge.duration}")
            print(f"   Active: {'Yes' if challenge.is_active else 'No'}")
            print(f"   Description: {challenge.description[:100]}...")
            print()
        
        # Summary by category
        print(f"📈 Summary by Category:")
        categories = db.query(Challenge.category, db.func.count(Challenge.id)).group_by(Challenge.category).all()
        for category, count in categories:
            print(f"  • {category.title()}: {count} challenges")
        
        print(f"\n🏆 Summary by Difficulty:")
        difficulties = db.query(Challenge.difficulty, db.func.count(Challenge.id)).group_by(Challenge.difficulty).all()
        for difficulty, count in difficulties:
            print(f"  • {difficulty.title()}: {count} challenges")
        
        print(f"\n✅ Challenge verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Error verifying challenges: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_challenges()
