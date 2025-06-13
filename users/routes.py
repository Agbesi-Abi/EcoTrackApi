"""
Users routes for EcoTrack Ghana
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import json

from database import get_db, User, Activity
from auth.utils import get_current_user, get_optional_current_user
from activities.utils import save_uploaded_file, get_impact_summary
from .schemas import UserProfileUpdate, UserProfileResponse, UserImpactStats

router = APIRouter()

@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile by ID"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's recent activities
    recent_activities = db.query(Activity).filter(
        Activity.user_id == user_id
    ).order_by(desc(Activity.created_at)).limit(5).all()
    
    # Get activity statistics
    total_activities = db.query(func.count(Activity.id)).filter(Activity.user_id == user_id).scalar()
    
    # Check if viewing own profile
    is_own_profile = current_user and current_user.id == user_id
    
    return UserProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email if is_own_profile else None,  # Only show email to profile owner
        location=user.location,
        region=user.region,
        total_points=user.total_points,
        weekly_points=user.weekly_points,
        rank=user.rank,
        avatar_url=user.avatar_url,
        is_verified=user.is_verified,
        created_at=user.created_at,
        total_activities=total_activities,
        impact_stats={
            "trash_collected": user.trash_collected,
            "trees_planted": user.trees_planted,
            "co2_saved": user.co2_saved
        },
        recent_activities=[
            {
                "id": activity.id,
                "type": activity.type,
                "title": activity.title,
                "points": activity.points,
                "created_at": activity.created_at,
                "verified": activity.verified
            } for activity in recent_activities
        ],
        is_own_profile=is_own_profile
    )

@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: int,
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile (only own profile)"""
    
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    # Update fields if provided
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    # Get updated profile data
    total_activities = db.query(func.count(Activity.id)).filter(Activity.user_id == current_user.id).scalar()
    recent_activities = db.query(Activity).filter(
        Activity.user_id == current_user.id
    ).order_by(desc(Activity.created_at)).limit(5).all()
    
    return UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        location=current_user.location,
        region=current_user.region,
        total_points=current_user.total_points,
        weekly_points=current_user.weekly_points,
        rank=current_user.rank,
        avatar_url=current_user.avatar_url,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        total_activities=total_activities,
        impact_stats={
            "trash_collected": current_user.trash_collected,
            "trees_planted": current_user.trees_planted,
            "co2_saved": current_user.co2_saved
        },
        recent_activities=[
            {
                "id": activity.id,
                "type": activity.type,
                "title": activity.title,
                "points": activity.points,
                "created_at": activity.created_at,
                "verified": activity.verified
            } for activity in recent_activities
        ],
        is_own_profile=True
    )

@router.post("/{user_id}/avatar")
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar (only own avatar)"""
    
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own avatar"
        )
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Save file
    avatar_url = await save_uploaded_file(file, "avatars")
    
    # Update user avatar
    current_user.avatar_url = avatar_url
    db.commit()
    
    return {"avatar_url": avatar_url}

@router.get("/{user_id}/impact", response_model=UserImpactStats)
async def get_user_impact_stats(
    user_id: int,
    timeframe: str = "all_time",  # all_time, monthly, weekly
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed impact statistics for a user"""
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get activities based on timeframe
    activities_query = db.query(Activity).filter(Activity.user_id == user_id)
    
    if timeframe == "weekly":
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        activities_query = activities_query.filter(Activity.created_at >= week_ago)
    elif timeframe == "monthly":
        from datetime import datetime, timedelta
        month_ago = datetime.utcnow() - timedelta(days=30)
        activities_query = activities_query.filter(Activity.created_at >= month_ago)
    
    activities = activities_query.order_by(desc(Activity.created_at)).all()
    
    # Calculate impact summary
    impact_summary = get_impact_summary(activities)
    
    # Get activity breakdown by type
    activity_breakdown = {}
    points_breakdown = {}
    
    for activity in activities:
        activity_type = activity.type
        activity_breakdown[activity_type] = activity_breakdown.get(activity_type, 0) + 1
        points_breakdown[activity_type] = points_breakdown.get(activity_type, 0) + activity.points
    
    # Calculate user rank in their region (if applicable)
    region_rank = None
    if user.region:
        region_users = db.query(User).filter(
            User.region == user.region,
            User.is_active == True
        ).order_by(desc(User.total_points)).all()
        
        for idx, region_user in enumerate(region_users, 1):
            if region_user.id == user_id:
                region_rank = idx
                break
    
    return UserImpactStats(
        user_id=user_id,
        timeframe=timeframe,
        total_activities=len(activities),
        total_points=sum(activity.points for activity in activities),
        activity_breakdown=activity_breakdown,
        points_breakdown=points_breakdown,
        environmental_impact={
            "trash_collected": user.trash_collected,
            "trees_planted": user.trees_planted,
            "co2_saved": user.co2_saved
        },
        region_rank=region_rank,
        global_rank=user.rank,
        achievements=[
            # Simple achievement calculation - you could expand this
            {"name": "Eco Warrior", "description": "Logged 10+ activities", "earned": len(activities) >= 10},
            {"name": "Tree Guardian", "description": "Planted 5+ trees", "earned": user.trees_planted >= 5},
            {"name": "Waste Fighter", "description": "Collected 10kg+ waste", "earned": user.trash_collected >= 10},
            {"name": "Climate Champion", "description": "Saved 100kg+ CO2", "earned": user.co2_saved >= 100}
        ]
    )

@router.get("/{user_id}/activities")
async def get_user_activities(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    activity_type: Optional[str] = None,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get user's activities (paginated)"""
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if this is the user's own activities or if activities should be public
    is_own_activities = current_user and current_user.id == user_id
    
    query = db.query(Activity).filter(Activity.user_id == user_id)
    
    # Apply filters
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    
    # If not own activities, only show verified activities for privacy
    if not is_own_activities:
        query = query.filter(Activity.verified == True)
    
    activities = query.order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()
    
    return {
        "activities": [
            {
                "id": activity.id,
                "type": activity.type,
                "title": activity.title,
                "description": activity.description,
                "points": activity.points,
                "location": activity.location,
                "verified": activity.verified,
                "created_at": activity.created_at,
                "photos": json.loads(activity.photos) if activity.photos else []
            } for activity in activities
        ],
        "total": query.count(),
        "showing_public_only": not is_own_activities
    }

@router.delete("/{user_id}")
async def delete_user_account(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account (only own account)"""
    
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    # Soft delete - set is_active to False instead of actually deleting
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}
