"""
Notification routes for EcoTrack Ghana
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database import get_db, Notification, User
from auth.utils import get_current_user, get_optional_current_user
from .schemas import (
    NotificationResponse, 
    NotificationCreate, 
    NotificationUpdate, 
    NotificationStats,
    BulkNotificationCreate
)
from .utils import NotificationService

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(50, le=100, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    unread_only: bool = Query(False, description="Return only unread notifications"),
    type_filter: Optional[str] = Query(None, description="Filter by notification type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications with pagination and filtering"""
    
    service = NotificationService(db)
    notifications = service.get_user_notifications(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        unread_only=unread_only
    )
    
    # Filter by type if specified
    if type_filter:
        notifications = [n for n in notifications if n.type == type_filter]
    
    # Convert notifications to response format
    response_notifications = []
    for notification in notifications:
        notification_dict = {
            'id': notification.id,
            'user_id': notification.user_id,
            'type': notification.type,
            'title': notification.title,
            'message': notification.message,
            'data': json.loads(notification.data) if notification.data else None,
            'is_read': notification.is_read,
            'priority': notification.priority,
            'action_url': notification.action_url,
            'expires_at': notification.expires_at,
            'created_at': notification.created_at,
            'read_at': notification.read_at
        }
        response_notifications.append(NotificationResponse(**notification_dict))
    
    return response_notifications

@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics for the current user"""
    
    service = NotificationService(db)
    stats = service.get_notification_stats(current_user.id)
    return NotificationStats(**stats)

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": unread_count}

@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a notification (mark as read/unread)"""
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Update notification
    if notification_update.is_read is not None:
        notification.is_read = notification_update.is_read
        if notification_update.is_read:
            notification.read_at = notification.read_at or db.func.now()
        else:
            notification.read_at = None
    
    db.commit()
    db.refresh(notification)
    
    # Convert to response format
    notification_dict = {
        'id': notification.id,
        'user_id': notification.user_id,
        'type': notification.type,
        'title': notification.title,
        'message': notification.message,
        'data': json.loads(notification.data) if notification.data else None,
        'is_read': notification.is_read,
        'priority': notification.priority,
        'action_url': notification.action_url,
        'expires_at': notification.expires_at,
        'created_at': notification.created_at,
        'read_at': notification.read_at
    }
    
    return NotificationResponse(**notification_dict)

@router.put("/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user"""
    
    service = NotificationService(db)
    updated_count = service.mark_all_as_read(current_user.id)
    
    return {
        "message": f"Marked {updated_count} notifications as read",
        "updated_count": updated_count
    }

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    
    service = NotificationService(db)
    deleted = service.delete_notification(notification_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification deleted successfully"}

@router.get("/types")
async def get_notification_types():
    """Get available notification types"""
    
    types = [
        {
            "type": "achievement",
            "name": "Achievements",
            "description": "Notifications about unlocked achievements and milestones",
            "icon": "🏆"
        },
        {
            "type": "challenge",
            "name": "Challenges",
            "description": "Updates about challenges and competitions",
            "icon": "🎯"
        },
        {
            "type": "activity",
            "name": "Activities",
            "description": "Notifications about your logged activities",
            "icon": "🌱"
        },
        {
            "type": "verification",
            "name": "Verification",
            "description": "Updates about activity and profile verification",
            "icon": "✅"
        },
        {
            "type": "leaderboard",
            "name": "Leaderboard",
            "description": "Your position updates on leaderboards",
            "icon": "📊"
        },
        {
            "type": "system",
            "name": "System",
            "description": "Important system announcements and updates",
            "icon": "🔔"
        }
    ]
    
    return {"notification_types": types}

# Admin endpoints for notifications (no authentication required since we removed permissions)
@router.post("/admin/create", response_model=NotificationResponse)
async def create_notification_admin(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a notification (admin endpoint)"""
    
    # Verify user exists
    user = db.query(User).filter(User.id == notification_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    service = NotificationService(db)
    notification = service.create_notification(notification_data)
    
    # Convert to response format
    notification_dict = {
        'id': notification.id,
        'user_id': notification.user_id,
        'type': notification.type,
        'title': notification.title,
        'message': notification.message,
        'data': json.loads(notification.data) if notification.data else None,
        'is_read': notification.is_read,
        'priority': notification.priority,
        'action_url': notification.action_url,
        'expires_at': notification.expires_at,
        'created_at': notification.created_at,
        'read_at': notification.read_at
    }
    
    return NotificationResponse(**notification_dict)

@router.post("/admin/bulk-create")
async def create_bulk_notifications_admin(
    bulk_data: BulkNotificationCreate,
    db: Session = Depends(get_db)
):
    """Create bulk notifications (admin endpoint)"""
    
    # Verify all users exist
    existing_users = db.query(User.id).filter(User.id.in_(bulk_data.user_ids)).all()
    existing_user_ids = {user.id for user in existing_users}
    
    invalid_user_ids = set(bulk_data.user_ids) - existing_user_ids
    if invalid_user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user IDs: {list(invalid_user_ids)}"
        )
    
    service = NotificationService(db)
    notifications = service.create_bulk_notifications(bulk_data)
    
    return {
        "message": f"Created {len(notifications)} notifications",
        "notification_count": len(notifications),
        "user_count": len(bulk_data.user_ids)
    }

@router.post("/admin/broadcast")
async def broadcast_notification(
    title: str,
    message: str,
    type: str = "system",
    priority: str = "normal",
    action_url: Optional[str] = None,
    region_filter: Optional[str] = None,
    verified_only: bool = False,
    db: Session = Depends(get_db)
):
    """Broadcast notification to all users or filtered users (admin endpoint)"""
    
    # Build user query
    query = db.query(User.id).filter(User.is_active == True)
    
    if region_filter:
        query = query.filter(User.region == region_filter)
    
    if verified_only:
        query = query.filter(User.is_verified == True)
    
    user_ids = [user.id for user in query.all()]
    
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users found matching the criteria"
        )
    
    # Create bulk notification
    bulk_data = BulkNotificationCreate(
        user_ids=user_ids,
        type=type,
        title=title,
        message=message,
        priority=priority,
        action_url=action_url
    )
    
    service = NotificationService(db)
    notifications = service.create_bulk_notifications(bulk_data)
    
    return {
        "message": f"Broadcast sent to {len(notifications)} users",
        "notification_count": len(notifications),
        "user_count": len(user_ids),
        "filters": {
            "region": region_filter,
            "verified_only": verified_only
        }
    }

@router.delete("/admin/cleanup")
async def cleanup_expired_notifications(
    db: Session = Depends(get_db)
):
    """Cleanup expired notifications (admin endpoint)"""
    
    service = NotificationService(db)
    deleted_count = service.cleanup_expired_notifications()
    
    return {
        "message": f"Cleaned up {deleted_count} expired notifications",
        "deleted_count": deleted_count
    }

@router.put("/admin/{notification_id}", response_model=NotificationResponse)
async def update_notification_admin(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db)
):
    """Update any notification (admin endpoint)"""
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Update notification fields
    if notification_update.is_read is not None:
        notification.is_read = notification_update.is_read
        if notification_update.is_read:
            notification.read_at = notification.read_at or db.func.now()
        else:
            notification.read_at = None
    
    db.commit()
    db.refresh(notification)
    
    # Convert to response format
    notification_dict = {
        'id': notification.id,
        'user_id': notification.user_id,
        'type': notification.type,
        'title': notification.title,
        'message': notification.message,
        'data': json.loads(notification.data) if notification.data else None,
        'is_read': notification.is_read,
        'priority': notification.priority,
        'action_url': notification.action_url,
        'expires_at': notification.expires_at,
        'created_at': notification.created_at,
        'read_at': notification.read_at
    }
    
    return NotificationResponse(**notification_dict)

@router.delete("/admin/{notification_id}")
async def delete_notification_admin(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Delete a notification (admin endpoint)"""
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    
    return {
        "message": "Notification deleted successfully",
        "notification_id": notification_id
    }

@router.get("/admin/history")
async def get_notification_history_admin(
    limit: int = Query(50, le=100, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    type_filter: Optional[str] = Query(None, description="Filter by notification type"),
    db: Session = Depends(get_db)
):
    """Get notification history for admin (all notifications)"""
    
    # Build query
    query = db.query(Notification).join(User, Notification.user_id == User.id)
    
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    
    if type_filter:
        query = query.filter(Notification.type == type_filter)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination and get results
    notifications = query.order_by(Notification.created_at.desc())\
                         .offset(offset)\
                         .limit(limit)\
                         .all()
    
    # Format response with user details
    response_notifications = []
    for notification in notifications:
        user = notification.user if hasattr(notification, 'user') else db.query(User).filter(User.id == notification.user_id).first()
        notification_dict = {
            'id': notification.id,
            'user_id': notification.user_id,
            'user_name': user.name if user else 'Unknown',
            'user_email': user.email if user else 'Unknown',
            'type': notification.type,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'action_url': notification.action_url,
            'expires_at': notification.expires_at,
            'created_at': notification.created_at,
            'read_at': notification.read_at
        }
        response_notifications.append(notification_dict)
    
    return {
        "notifications": response_notifications,
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }

@router.get("/admin/stats")
async def get_admin_notification_stats(
    db: Session = Depends(get_db)
):
    """Get notification statistics for admin dashboard"""
    
    # Total notifications
    total_notifications = db.query(Notification).count()
    
    # Read/unread counts
    read_notifications = db.query(Notification).filter(Notification.is_read == True).count()
    unread_notifications = total_notifications - read_notifications
    
    # Recent notifications (last 24 hours)
    from datetime import datetime, timedelta
    recent_cutoff = datetime.now() - timedelta(hours=24)
    recent_notifications = db.query(Notification).filter(
        Notification.created_at >= recent_cutoff
    ).count()
    
    # By type
    type_stats = db.query(
        Notification.type,
        db.func.count(Notification.id).label('count')
    ).group_by(Notification.type).all()
    by_type = {type_stat.type: type_stat.count for type_stat in type_stats}
    
    # By priority
    priority_stats = db.query(
        Notification.priority,
        db.func.count(Notification.id).label('count')
    ).group_by(Notification.priority).all()
    by_priority = {priority_stat.priority: priority_stat.count for priority_stat in priority_stats}
    
    # Calculate read rate
    read_rate = (read_notifications / total_notifications * 100) if total_notifications > 0 else 0
    
    return {
        "total_notifications": total_notifications,
        "read_notifications": read_notifications,
        "unread_notifications": unread_notifications,
        "read_rate": round(read_rate, 2),
        "recent_notifications": recent_notifications,
        "by_type": by_type,
        "by_priority": by_priority
    }
