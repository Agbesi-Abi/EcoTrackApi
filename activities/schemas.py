"""
Activity schemas for EcoTrack Ghana
"""

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List, Dict, Any

class ActivityCreate(BaseModel):
    type: str
    title: str
    description: str
    location: Optional[str] = None
    region: Optional[str] = None
    photos: Optional[List[str]] = []
    impact_data: Optional[Dict[str, Any]] = {}
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['trash', 'trees', 'mobility', 'water', 'energy']
        if v not in allowed_types:
            raise ValueError(f'Activity type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        if len(v.strip()) > 100:
            raise ValueError('Title must be less than 100 characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        if len(v.strip()) > 500:
            raise ValueError('Description must be less than 500 characters')
        return v.strip()

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    region: Optional[str] = None
    photos: Optional[List[str]] = None
    impact_data: Optional[Dict[str, Any]] = None
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) < 3:
                raise ValueError('Title must be at least 3 characters long')
            if len(v.strip()) > 100:
                raise ValueError('Title must be less than 100 characters')
            return v.strip()
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            if len(v.strip()) < 10:
                raise ValueError('Description must be at least 10 characters long')
            if len(v.strip()) > 500:
                raise ValueError('Description must be less than 500 characters')
            return v.strip()
        return v

class ActivityResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    type: str
    title: str
    description: str
    points: int
    location: Optional[str] = None
    region: Optional[str] = None
    photos: List[str] = []
    verified: bool = False
    created_at: datetime
    impact_data: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True

class ActivityStats(BaseModel):
    total_activities: int
    total_points: int
    active_users: int
    activities_by_type: Dict[str, int]
    total_impact: Dict[str, float]
