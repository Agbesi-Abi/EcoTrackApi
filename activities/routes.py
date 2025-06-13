"""
Activities routes for EcoTrack Ghana
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import json
import aiofiles
import os
from datetime import datetime
from pathlib import Path

from database import get_db, Activity, User
from auth.utils import get_current_user, get_optional_current_user
from .schemas import ActivityCreate, ActivityResponse, ActivityUpdate, ActivityStats
from .utils import calculate_points, update_user_impact_stats, save_uploaded_file

router = APIRouter()

@router.get("/", response_model=List[ActivityResponse])
async def get_activities(
    skip: int = 0,
    limit: int = 20,
    activity_type: Optional[str] = None,
    region: Optional[str] = None,
    verified_only: bool = False,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get list of activities with optional filters"""
    
    query = db.query(Activity)
    
    # Apply filters
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    if region:
        query = query.filter(Activity.region == region)
    if verified_only:
        query = query.filter(Activity.verified == True)
    
    # If user is authenticated, show their activities first
    if current_user:
        query = query.order_by(
            (Activity.user_id == current_user.id).desc(),
            desc(Activity.created_at)
        )
    else:
        query = query.order_by(desc(Activity.created_at))
    
    activities = query.offset(skip).limit(limit).all()
    
    return [
        ActivityResponse(
            id=activity.id,
            user_id=activity.user_id,
            user_name=activity.user.name,
            type=activity.type,
            title=activity.title,
            description=activity.description,
            points=activity.points,
            location=activity.location,
            region=activity.region,
            photos=json.loads(activity.photos) if activity.photos else [],
            verified=activity.verified,
            created_at=activity.created_at,
            impact_data=json.loads(activity.impact_data) if activity.impact_data else {}
        ) for activity in activities
    ]

@router.get("/my", response_model=List[ActivityResponse])
async def get_my_activities(
    skip: int = 0,
    limit: int = 20,
    activity_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's activities"""
    
    query = db.query(Activity).filter(Activity.user_id == current_user.id)
    
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    
    activities = query.order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()
    
    return [
        ActivityResponse(
            id=activity.id,
            user_id=activity.user_id,
            user_name=activity.user.name,
            type=activity.type,
            title=activity.title,
            description=activity.description,
            points=activity.points,
            location=activity.location,
            region=activity.region,
            photos=json.loads(activity.photos) if activity.photos else [],
            verified=activity.verified,
            created_at=activity.created_at,
            impact_data=json.loads(activity.impact_data) if activity.impact_data else {}
        ) for activity in activities
    ]

@router.post("/", response_model=ActivityResponse)
async def create_activity(
    activity_data: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new activity"""
    
    # Calculate points for the activity
    points = calculate_points(activity_data.type, activity_data.dict())
    
    # Create activity
    db_activity = Activity(
        user_id=current_user.id,
        type=activity_data.type,
        title=activity_data.title,
        description=activity_data.description,
        points=points,
        location=activity_data.location,
        region=activity_data.region,
        photos=json.dumps(activity_data.photos) if activity_data.photos else None,
        impact_data=json.dumps(activity_data.impact_data) if activity_data.impact_data else None
    )
    
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    # Update user points and impact stats
    current_user.total_points += points
    current_user.weekly_points += points
    update_user_impact_stats(current_user, activity_data.type, activity_data.dict())
    
    db.commit()
    db.refresh(current_user)
    
    return ActivityResponse(
        id=db_activity.id,
        user_id=db_activity.user_id,
        user_name=current_user.name,
        type=db_activity.type,
        title=db_activity.title,
        description=db_activity.description,
        points=db_activity.points,
        location=db_activity.location,
        region=db_activity.region,
        photos=json.loads(db_activity.photos) if db_activity.photos else [],
        verified=db_activity.verified,
        created_at=db_activity.created_at,
        impact_data=json.loads(db_activity.impact_data) if db_activity.impact_data else {}
    )

@router.post("/upload-photo")
async def upload_activity_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a photo for an activity"""
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Save file
    file_url = await save_uploaded_file(file, "activities")
    
    return {"photo_url": file_url}

@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get specific activity by ID"""
    
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    return ActivityResponse(
        id=activity.id,
        user_id=activity.user_id,
        user_name=activity.user.name,
        type=activity.type,
        title=activity.title,
        description=activity.description,
        points=activity.points,
        location=activity.location,
        region=activity.region,
        photos=json.loads(activity.photos) if activity.photos else [],
        verified=activity.verified,
        created_at=activity.created_at,
        impact_data=json.loads(activity.impact_data) if activity.impact_data else {}
    )

@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_update: ActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an activity (only by owner)"""
    
    activity = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.user_id == current_user.id
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found or you don't have permission to edit it"
        )
    
    # Update fields if provided
    update_data = activity_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "photos" and value is not None:
            setattr(activity, field, json.dumps(value))
        elif field == "impact_data" and value is not None:
            setattr(activity, field, json.dumps(value))
        else:
            setattr(activity, field, value)
    
    db.commit()
    db.refresh(activity)
    
    return ActivityResponse(
        id=activity.id,
        user_id=activity.user_id,
        user_name=activity.user.name,
        type=activity.type,
        title=activity.title,
        description=activity.description,
        points=activity.points,
        location=activity.location,
        region=activity.region,
        photos=json.loads(activity.photos) if activity.photos else [],
        verified=activity.verified,
        created_at=activity.created_at,
        impact_data=json.loads(activity.impact_data) if activity.impact_data else {}
    )

@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an activity (only by owner)"""
    
    activity = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.user_id == current_user.id
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found or you don't have permission to delete it"
        )
    
    # Subtract points from user
    current_user.total_points -= activity.points
    current_user.weekly_points -= activity.points
    
    db.delete(activity)
    db.commit()
    
    return {"message": "Activity deleted successfully"}

@router.get("/stats/global", response_model=ActivityStats)
async def get_global_stats(db: Session = Depends(get_db)):
    """Get global activity statistics"""
    
    stats = db.query(
        func.count(Activity.id).label('total_activities'),
        func.sum(Activity.points).label('total_points'),
        func.count(func.distinct(Activity.user_id)).label('active_users')
    ).first()
    
    type_stats = db.query(
        Activity.type,
        func.count(Activity.id).label('count')
    ).group_by(Activity.type).all()
    
    return ActivityStats(
        total_activities=stats.total_activities or 0,
        total_points=stats.total_points or 0,
        active_users=stats.active_users or 0,
        activities_by_type={stat.type: stat.count for stat in type_stats},
        total_impact={
            "trash_collected": db.query(func.sum(User.trash_collected)).scalar() or 0,
            "trees_planted": db.query(func.sum(User.trees_planted)).scalar() or 0,
            "co2_saved": db.query(func.sum(User.co2_saved)).scalar() or 0
        }
    )
