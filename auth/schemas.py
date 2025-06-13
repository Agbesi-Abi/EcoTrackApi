"""
Authentication schemas for EcoTrack Ghana
"""

from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, Dict, Any

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    location: Optional[str] = None
    region: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    location: Optional[str] = None
    region: Optional[str] = None
    total_points: int = 0
    weekly_points: int = 0
    rank: int = 0
    is_verified: bool = False
    created_at: datetime
    impact_stats: Dict[str, Any]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
