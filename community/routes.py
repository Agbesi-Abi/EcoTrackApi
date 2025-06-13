"""
Community routes for EcoTrack Ghana
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db, User, Activity, Region
from auth.utils import get_current_user, get_optional_current_user
from .schemas import LeaderboardEntry, RegionalStats, GlobalStats

router = APIRouter()

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    region: Optional[str] = None,
    timeframe: str = "all_time",  # all_time, monthly, weekly
    limit: int = 50,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get community leaderboard"""
    
    query = db.query(User).filter(User.is_active == True)
    
    # Filter by region if specified
    if region:
        query = query.filter(User.region == region)
    
    # Apply timeframe filter
    if timeframe == "weekly":
        query = query.order_by(desc(User.weekly_points), desc(User.total_points))
    elif timeframe == "monthly":
        # For simplicity, using weekly_points as monthly (you could add a monthly_points field)
        query = query.order_by(desc(User.weekly_points), desc(User.total_points))
    else:  # all_time
        query = query.order_by(desc(User.total_points))
    
    users = query.limit(limit).all()
    
    leaderboard = []
    for idx, user in enumerate(users, 1):
        # Calculate current rank if not set
        rank = idx
        
        # Check if this is the current user - ensure boolean
        is_current_user = bool(current_user is not None and user.id == current_user.id)
        
        leaderboard.append(LeaderboardEntry(
            rank=rank,
            user_id=user.id,
            name=user.name,
            location=user.location,
            region=user.region,
            total_points=user.total_points,
            weekly_points=user.weekly_points,
            impact_stats={
                "trash_collected": user.trash_collected,
                "trees_planted": user.trees_planted,
                "co2_saved": user.co2_saved
            },
            is_current_user=is_current_user
        ))
    
    return leaderboard

@router.get("/stats/global", response_model=GlobalStats)
async def get_global_stats(db: Session = Depends(get_db)):
    """Get global community statistics"""
    
    # Get basic stats
    basic_stats = db.query(
        func.count(User.id).label('total_users'),
        func.sum(User.total_points).label('total_points'),
        func.count(Activity.id).label('total_activities'),
        func.sum(User.trash_collected).label('total_trash'),
        func.sum(User.trees_planted).label('total_trees'),
        func.sum(User.co2_saved).label('total_co2_saved')
    ).outerjoin(Activity, User.id == Activity.user_id).filter(User.is_active == True).first()
    
    # Get active users (users with activities in the last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(func.count(func.distinct(Activity.user_id))).filter(
        Activity.created_at >= thirty_days_ago
    ).scalar()
    
    # Get activities by type
    activity_types = db.query(
        Activity.type,
        func.count(Activity.id).label('count')
    ).group_by(Activity.type).all()
    
    activities_by_type = {activity_type.type: activity_type.count for activity_type in activity_types}
    
    # Get top performing region
    top_region = db.query(
        User.region,
        func.sum(User.total_points).label('total_points')
    ).filter(
        User.region.isnot(None),
        User.is_active == True
    ).group_by(User.region).order_by(desc(func.sum(User.total_points))).first()
    
    return GlobalStats(
        total_users=basic_stats.total_users or 0,
        active_users=active_users or 0,
        total_points=basic_stats.total_points or 0,
        total_activities=basic_stats.total_activities or 0,
        activities_by_type=activities_by_type,
        top_region=top_region.region if top_region else None,
        impact_stats={
            "trash_collected": float(basic_stats.total_trash or 0),
            "trees_planted": int(basic_stats.total_trees or 0),
            "co2_saved": float(basic_stats.total_co2_saved or 0)
        }
    )
