"""
User schemas for EcoTrack Ghana
"""

from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List, Dict, Any

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    region: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Name must be at least 2 characters long')
            if len(v.strip()) > 50:
                raise ValueError('Name must be less than 50 characters')
            return v.strip()
        return v

class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None  # Only shown to profile owner
    location: Optional[str] = None
    region: Optional[str] = None
    total_points: int
    weekly_points: int
    rank: int
    avatar_url: Optional[str] = None
    is_verified: bool
    created_at: datetime
    total_activities: int
    impact_stats: Dict[str, Any]
    recent_activities: List[Dict[str, Any]]
    is_own_profile: bool = False
    
    class Config:
        from_attributes = True

class UserImpactStats(BaseModel):
    user_id: int
    timeframe: str
    total_activities: int
    total_points: int
    activity_breakdown: Dict[str, int]
    points_breakdown: Dict[str, int]
    environmental_impact: Dict[str, Any]
    region_rank: Optional[int] = None
    global_rank: int
    achievements: List[Dict[str, Any]]
