"""
Notification schemas for EcoTrack Ghana
"""

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List, Dict, Any

class NotificationCreate(BaseModel):
    user_id: int
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str = "normal"
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['achievement', 'challenge', 'activity', 'verification', 'leaderboard', 'system']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    is_read: bool
    priority: str
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationStats(BaseModel):
    total_notifications: int
    unread_count: int
    read_count: int
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]

class BulkNotificationCreate(BaseModel):
    user_ids: List[int]
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str = "normal"
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['achievement', 'challenge', 'activity', 'verification', 'leaderboard', 'system']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v

class NotificationPreferences(BaseModel):
    user_id: int
    email_notifications: bool = True
    push_notifications: bool = True
    achievement_notifications: bool = True
    challenge_notifications: bool = True
    activity_notifications: bool = True
    verification_notifications: bool = True
    leaderboard_notifications: bool = True
    system_notifications: bool = True
    notification_frequency: str = "immediate"  # 'immediate', 'daily', 'weekly'
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format
    
    @validator('notification_frequency')
    def validate_frequency(cls, v):
        allowed_frequencies = ['immediate', 'daily', 'weekly']
        if v not in allowed_frequencies:
            raise ValueError(f'Frequency must be one of: {", ".join(allowed_frequencies)}')
        return v
