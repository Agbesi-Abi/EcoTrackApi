"""
Notification utility functions for EcoTrack Ghana
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database import Notification, User
from .schemas import NotificationCreate, BulkNotificationCreate

class NotificationService:
    """Service class for handling notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a single notification"""
        # Convert data dict to JSON string if provided
        data_json = json.dumps(notification_data.data) if notification_data.data else None
        
        notification = Notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            data=data_json,
            priority=notification_data.priority,
            action_url=notification_data.action_url,
            expires_at=notification_data.expires_at
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def create_bulk_notifications(self, bulk_data: BulkNotificationCreate) -> List[Notification]:
        """Create notifications for multiple users"""
        notifications = []
        data_json = json.dumps(bulk_data.data) if bulk_data.data else None
        
        for user_id in bulk_data.user_ids:
            notification = Notification(
                user_id=user_id,
                type=bulk_data.type,
                title=bulk_data.title,
                message=bulk_data.message,
                data=data_json,
                priority=bulk_data.priority,
                action_url=bulk_data.action_url,
                expires_at=bulk_data.expires_at
            )
            notifications.append(notification)
        
        self.db.add_all(notifications)
        self.db.commit()
        return notifications
    
    def get_user_notifications(self, user_id: int, limit: int = 50, offset: int = 0, 
                             unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        # Filter out expired notifications
        query = query.filter(
            (Notification.expires_at.is_(None)) | 
            (Notification.expires_at > datetime.utcnow())
        )
        
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        updated_count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        self.db.commit()
        return updated_count
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False
    
    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """Get notification statistics for a user"""
        total = self.db.query(Notification).filter(Notification.user_id == user_id).count()
        unread = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        # Get notifications by type
        type_stats = {}
        notifications = self.db.query(Notification).filter(Notification.user_id == user_id).all()
        for notification in notifications:
            type_stats[notification.type] = type_stats.get(notification.type, 0) + 1
        
        # Get notifications by priority
        priority_stats = {}
        for notification in notifications:
            priority_stats[notification.priority] = priority_stats.get(notification.priority, 0) + 1
        
        return {
            'total_notifications': total,
            'unread_count': unread,
            'read_count': total - unread,
            'notifications_by_type': type_stats,
            'notifications_by_priority': priority_stats
        }
    
    def cleanup_expired_notifications(self) -> int:
        """Remove expired notifications"""
        expired_count = self.db.query(Notification).filter(
            Notification.expires_at < datetime.utcnow()
        ).count()
        
        self.db.query(Notification).filter(
            Notification.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        return expired_count

# Pre-defined notification templates
class NotificationTemplates:
    """Templates for common notifications"""
    
    @staticmethod
    def achievement_unlocked(user_id: int, achievement_name: str, points: int) -> NotificationCreate:
        return NotificationCreate(
            user_id=user_id,
            type="achievement",
            title="🏆 Achievement Unlocked!",
            message=f"Congratulations! You've earned the '{achievement_name}' achievement and {points} bonus points!",
            data={"achievement": achievement_name, "bonus_points": points},
            priority="high",
            action_url="/achievements"
        )
    
    @staticmethod
    def activity_verified(user_id: int, activity_title: str, points: int) -> NotificationCreate:
        return NotificationCreate(
            user_id=user_id,
            type="verification",
            title="✅ Activity Verified",
            message=f"Your activity '{activity_title}' has been verified! You earned {points} points.",
            data={"activity_title": activity_title, "points": points},
            priority="normal",
            action_url="/activities"
        )
    
    @staticmethod
    def challenge_reminder(user_id: int, challenge_title: str, days_left: int) -> NotificationCreate:
        return NotificationCreate(
            user_id=user_id,
            type="challenge",
            title="⏰ Challenge Reminder",
            message=f"Don't forget! The '{challenge_title}' challenge ends in {days_left} days.",
            data={"challenge_title": challenge_title, "days_left": days_left},
            priority="normal",
            action_url="/challenges",
            expires_at=datetime.utcnow() + timedelta(days=days_left)
        )
    
    @staticmethod
    def leaderboard_position(user_id: int, position: int, region: str = None) -> NotificationCreate:
        scope = f" in {region}" if region else ""
        return NotificationCreate(
            user_id=user_id,
            type="leaderboard",
            title="📊 Leaderboard Update",
            message=f"Great job! You're now #{position} on the leaderboard{scope}!",
            data={"position": position, "region": region},
            priority="normal",
            action_url="/leaderboard"
        )
    
    @staticmethod
    def welcome_message(user_id: int, name: str) -> NotificationCreate:
        return NotificationCreate(
            user_id=user_id,
            type="system",
            title="🌍 Welcome to EcoTrack Ghana!",
            message=f"Hi {name}! Welcome to EcoTrack Ghana. Start logging your eco-friendly activities to earn points and make a difference!",
            data={"welcome": True},
            priority="high",
            action_url="/onboarding"
        )
    
    @staticmethod
    def points_milestone(user_id: int, total_points: int) -> NotificationCreate:
        return NotificationCreate(
            user_id=user_id,
            type="achievement",
            title="🎯 Points Milestone!",
            message=f"Amazing! You've reached {total_points:,} total points. Keep up the great work!",
            data={"milestone_points": total_points},
            priority="high",
            action_url="/profile"
        )
    
    @staticmethod
    def new_challenge_available(user_id: int, challenge_title: str, points: int) -> NotificationCreate:
        return NotificationCreate(
            user_id=user_id,
            type="challenge",
            title="🆕 New Challenge Available",
            message=f"A new challenge '{challenge_title}' is now available! Earn up to {points} points by participating.",
            data={"challenge_title": challenge_title, "max_points": points},
            priority="normal",
            action_url="/challenges"
        )

# Notification trigger functions
def trigger_achievement_notification(db: Session, user_id: int, achievement_name: str, points: int):
    """Trigger achievement notification"""
    service = NotificationService(db)
    notification = NotificationTemplates.achievement_unlocked(user_id, achievement_name, points)
    return service.create_notification(notification)

def trigger_activity_verification_notification(db: Session, user_id: int, activity_title: str, points: int):
    """Trigger activity verification notification"""
    service = NotificationService(db)
    notification = NotificationTemplates.activity_verified(user_id, activity_title, points)
    return service.create_notification(notification)

def trigger_welcome_notification(db: Session, user_id: int, name: str):
    """Trigger welcome notification for new users"""
    service = NotificationService(db)
    notification = NotificationTemplates.welcome_message(user_id, name)
    return service.create_notification(notification)

def trigger_points_milestone_notification(db: Session, user_id: int, total_points: int):
    """Trigger points milestone notification"""
    # Only trigger for significant milestones
    milestones = [100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
    if total_points in milestones:
        service = NotificationService(db)
        notification = NotificationTemplates.points_milestone(user_id, total_points)
        return service.create_notification(notification)
    return None
