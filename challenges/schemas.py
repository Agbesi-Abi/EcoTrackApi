"""
Challenge schemas for EcoTrack Ghana
"""

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class ChallengeCreate(BaseModel):
    title: str
    description: str
    category: str
    duration: str
    points: int
    difficulty: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('category')
    def validate_category(cls, v):
        allowed_categories = ['trash', 'trees', 'mobility', 'water', 'energy']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed_difficulties = ['easy', 'medium', 'hard']
        if v not in allowed_difficulties:
            raise ValueError(f'Difficulty must be one of: {", ".join(allowed_difficulties)}')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters long')
        if len(v.strip()) > 100:
            raise ValueError('Title must be less than 100 characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 20:
            raise ValueError('Description must be at least 20 characters long')
        if len(v.strip()) > 500:
            raise ValueError('Description must be less than 500 characters')
        return v.strip()
    
    @validator('points')
    def validate_points(cls, v):
        if v < 1:
            raise ValueError('Points must be positive')
        if v > 1000:
            raise ValueError('Points cannot exceed 1000')
        return v

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    points: Optional[int] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ChallengeResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    duration: str
    points: int
    difficulty: str
    participants: int
    joined: bool = False
    progress: float = 0.0
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChallengeParticipation(BaseModel):
    progress: float
    
    @validator('progress')
    def validate_progress(cls, v):
        if v < 0:
            raise ValueError('Progress cannot be negative')
        if v > 100:
            raise ValueError('Progress cannot exceed 100%')
        return v
