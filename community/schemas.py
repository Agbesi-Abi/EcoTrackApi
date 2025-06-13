"""
Community schemas for EcoTrack Ghana
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    name: str
    location: Optional[str] = None
    region: Optional[str] = None
    total_points: int
    weekly_points: int
    impact_stats: Dict[str, Any]
    is_current_user: bool = False

class RegionalStats(BaseModel):
    rank: int
    region: str
    total_users: int
    total_points: int
    total_activities: int
    impact_stats: Dict[str, Any]

class GlobalStats(BaseModel):
    total_users: int
    active_users: int
    total_points: int
    total_activities: int
    activities_by_type: Dict[str, int]
    top_region: Optional[str] = None
    impact_stats: Dict[str, Any]
