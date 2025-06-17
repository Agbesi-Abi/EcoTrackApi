"""
Test script for the notification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from database import engine, init_db
from notifications.utils import (
    NotificationService, 
    NotificationTemplates,
    trigger_welcome_notification,
    trigger_points_milestone_notification
)
from notifications.schemas import NotificationCreate

def test_notifications():
    """Test notification system functionality"""
    print("🔔 Testing EcoTrack Ghana Notification System")
    print("=" * 50)
    
    # Initialize database
    init_db()
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Test 1: Create a simple notification
        print("\n📝 Test 1: Creating a simple notification")
        service = NotificationService(db)
        
        notification_data = NotificationCreate(
            user_id=1,  # Assuming user with ID 1 exists
            type="system",
            title="Test Notification",
            message="This is a test notification from the system",
            priority="normal"
        )
        
        notification = service.create_notification(notification_data)
        print(f"✅ Created notification with ID: {notification.id}")
        
        # Test 2: Get user notifications
        print("\n📋 Test 2: Getting user notifications")
        notifications = service.get_user_notifications(user_id=1, limit=10)
        print(f"✅ Found {len(notifications)} notifications for user 1")
        
        for notif in notifications:
            print(f"   - {notif.title}: {notif.message} (Read: {notif.is_read})")
        
        # Test 3: Test templates
        print("\n🎯 Test 3: Testing notification templates")
        
        # Welcome notification
        welcome_notif = NotificationTemplates.welcome_message(1, "Test User")
        created_welcome = service.create_notification(welcome_notif)
        print(f"✅ Created welcome notification: {created_welcome.title}")
        
        # Achievement notification
        achievement_notif = NotificationTemplates.achievement_unlocked(1, "First Steps", 100)
        created_achievement = service.create_notification(achievement_notif)
        print(f"✅ Created achievement notification: {created_achievement.title}")
        
        # Points milestone notification
        milestone_notif = NotificationTemplates.points_milestone(1, 1000)
        created_milestone = service.create_notification(milestone_notif)
        print(f"✅ Created milestone notification: {created_milestone.title}")
        
        # Test 4: Mark notifications as read
        print("\n✅ Test 4: Mark notification as read")
        success = service.mark_as_read(notification.id, 1)
        print(f"✅ Marked notification as read: {success}")
        
        # Test 5: Get notification stats
        print("\n📊 Test 5: Get notification statistics")
        stats = service.get_notification_stats(1)
        print(f"✅ User 1 notification stats:")
        print(f"   - Total: {stats['total_notifications']}")
        print(f"   - Unread: {stats['unread_count']}")
        print(f"   - Read: {stats['read_count']}")
        print(f"   - By type: {stats['notifications_by_type']}")
        
        # Test 6: Create bulk notifications (simulate broadcast)
        print("\n📢 Test 6: Testing bulk notifications")
        from notifications.schemas import BulkNotificationCreate
        
        # Get a few user IDs to test with
        from database import User
        users = db.query(User.id).limit(3).all()
        user_ids = [user.id for user in users]
        
        if user_ids:
            bulk_data = BulkNotificationCreate(
                user_ids=user_ids,
                type="system",
                title="System Announcement",
                message="This is a test system announcement sent to multiple users",
                priority="high"
            )
            
            bulk_notifications = service.create_bulk_notifications(bulk_data)
            print(f"✅ Created {len(bulk_notifications)} bulk notifications")
        
        print(f"\n🎉 All notification tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_notifications()
