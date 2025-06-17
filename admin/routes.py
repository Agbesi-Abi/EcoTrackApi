"""
Admin routes for database management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from database import get_db, engine, User
from auth.utils import get_password_hash
from notifications.utils import trigger_activity_verification_notification
import sqlite3
import os
from typing import Dict, List, Any
import json
from pydantic import BaseModel

router = APIRouter()

# Admin User Management Models
class AdminUserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str = "admin"  # "super_admin" or "admin"
    permissions: str = "basic"  # "full" or "basic"

class AdminUserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    permissions: str
    is_active: bool
    created_at: str
    last_login: str = None

# Admin Notification Management Models
class AdminNotificationCreate(BaseModel):
    target_group: str  # "admins", "users", "verified", "unverified", "all"
    type: str  # "system", "achievement", "challenge", "activity", "verification", "leaderboard"
    title: str
    message: str
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    action_url: str = None
    expires_at: str = None
    region_filter: str = None  # Optional region filter

class AdminBulkNotificationCreate(BaseModel):
    user_ids: List[int]
    type: str
    title: str
    message: str
    priority: str = "normal"
    action_url: str = None
    expires_at: str = None

@router.get("/docs", response_class=HTMLResponse)
async def get_admin_docs():
    """Generate basic API documentation for admin use"""
    docs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EcoTrack Ghana API - Admin Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            .endpoint { margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; margin-right: 10px; }
            .get { background: #28a745; }
            .post { background: #007bff; }
            .put { background: #ffc107; color: black; }
            .delete { background: #dc3545; }
            code { background: #e9ecef; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌍 EcoTrack Ghana API Documentation</h1>
            <p>Admin access to API endpoints</p>
            
            <h2>📊 Admin Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/admin/stats</strong><br>
                Get database statistics and record counts
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/admin/tables</strong><br>
                List all database tables and their structure
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/admin/table/{table_name}</strong><br>
                Get data from a specific table with pagination<br>
                <em>Query parameters: limit (default: 10), offset (default: 0)</em>
            </div>
            
            <h2>🔐 Authentication Endpoints</h2>
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/v1/auth/register</strong><br>
                Register a new user
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/v1/auth/login</strong><br>
                Login with email and password
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/auth/me</strong><br>
                Get current user information (requires authentication)
            </div>
            
            <h2>🎯 Activities Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/activities</strong><br>
                Get all activities with optional filters
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/v1/activities</strong><br>
                Create a new activity (requires authentication)
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/activities/my</strong><br>
                Get current user's activities (requires authentication)
            </div>
            
            <h2>🏆 Challenges Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/challenges</strong><br>
                Get all challenges with optional filters
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/v1/challenges/{id}/join</strong><br>
                Join a challenge (requires authentication)
            </div>
            
            <h2>👥 Community Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/community/leaderboard</strong><br>
                Get community leaderboard
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/community/stats/global</strong><br>
                Get global community statistics
            </div>
            
            <h2>🇬🇭 Ghana Data Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/ghana/regions</strong><br>
                Get list of Ghana regions with capitals
            </div>
            
            <h2>❤️ Health Check</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/health</strong><br>
                API health check
            </div>
            
            <h3>🌐 Base URLs</h3>
            <ul>
                <li><strong>Production:</strong> <code>https://ecotrack-online.onrender.com</code></li>
                <li><strong>Development:</strong> <code>http://localhost:8000</code></li>
            </ul>
            
            <h3>📝 Example Usage</h3>
            <pre><code># Get health status
curl https://ecotrack-online.onrender.com/health

# Get global stats
curl https://ecotrack-online.onrender.com/api/v1/community/stats/global

# Get challenges
curl https://ecotrack-online.onrender.com/api/v1/challenges?active_only=true&limit=10

# Get leaderboard
curl https://ecotrack-online.onrender.com/api/v1/community/leaderboard?limit=20</code></pre>
        </div>
    </body>
    </html>
    """
    return docs_html

@router.get("/stats")
async def get_database_stats(
    db: Session = Depends(get_db)
):
    """Get database statistics"""
    try:
        # Get table information
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        stats = {
            "tables": {},
            "total_records": 0,
            "database_info": {
                "type": "SQLite",
                "tables_count": len(tables)
            }
        }
        
        # Count records in each table
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                stats["tables"][table] = count
                stats["total_records"] += count
            except Exception as e:
                stats["tables"][table] = f"Error: {str(e)}"
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database stats error: {str(e)}")

@router.get("/tables")
async def list_tables(
    db: Session = Depends(get_db)
):
    """List all database tables"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        table_info = []
        for table in tables:
            columns = inspector.get_columns(table)
            table_info.append({
                "name": table,
                "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns]
            })
        
        return {"tables": table_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tables: {str(e)}")

@router.get("/table/{table_name}")
async def get_table_data(
    table_name: str,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Get data from a specific table"""
    try:
        # Validate table name (security)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if table_name not in tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get data with pagination
        result = db.execute(text(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"))
        columns = result.keys()
        rows = result.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        # Get total count
        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        total_count = count_result.scalar()
        
        return {
            "table": table_name,
            "data": data,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing table: {str(e)}")

@router.post("/query")
async def execute_query(
    query_data: Dict[str, str],
    db: Session = Depends(get_db)
):
    """Execute a custom SQL query (READ ONLY)"""
    query = query_data.get("query", "").strip().lower()
    
    # Security: Only allow SELECT queries
    if not query.startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    
    try:
        result = db.execute(text(query_data["query"]))
        columns = result.keys()
        rows = result.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return {"data": data, "row_count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@router.get("/backup-info")
async def get_backup_info():
    """Get information about database backups"""
    db_path = "ecotrack_ghana.db"
    
    if not os.path.exists(db_path):
        return {"error": "Database file not found"}
    
    file_size = os.path.getsize(db_path)
    file_size_mb = file_size / (1024 * 1024)
    
    return {
        "database_path": db_path,
        "size_bytes": file_size,
        "size_mb": round(file_size_mb, 2),
        "backup_available": True
    }

# User Verification Admin Endpoints
@router.put("/users/{user_id}/verify")
async def verify_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Verify a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_verified = True
        db.commit()
        db.refresh(user)
        
        # Trigger verification notification
        try:
            # For user verification, we'll create a simple achievement notification
            from notifications.utils import NotificationService, NotificationTemplates
            service = NotificationService(db)
            notification = NotificationTemplates.achievement_unlocked(
                user.id, "Account Verified", 50
            )
            service.create_notification(notification)
        except Exception as e:
            # Don't fail verification if notification fails
            print(f"Failed to create verification notification: {e}")
        
        return {
            "message": f"User {user.name} has been verified successfully",
            "user_id": user_id,
            "is_verified": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying user: {str(e)}")

@router.put("/users/{user_id}/unverify")
async def unverify_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Unverify a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_verified = False
        db.commit()
        db.refresh(user)
        
        return {
            "message": f"User {user.name} has been unverified",
            "user_id": user_id,
            "is_verified": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unverifying user: {str(e)}")

@router.get("/users/verification-stats")
async def get_verification_stats(
    db: Session = Depends(get_db)
):
    """Get user verification statistics"""
    try:
        total_users = db.query(User).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        unverified_users = db.query(User).filter(User.is_verified == False).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "unverified_users": unverified_users,
            "active_users": active_users,
            "verification_rate": round((verified_users / total_users * 100) if total_users > 0 else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting verification stats: {str(e)}")

# Admin User Management Endpoints
@router.post("/admins/create")
async def create_admin_user(
    admin_data: AdminUserCreate,
    db: Session = Depends(get_db)
):
    """Create a new admin user"""
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == admin_data.email).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Admin with this email already exists")
        
        # Create new admin user
        hashed_password = get_password_hash(admin_data.password)
        
        # Use execute with text for SQLite compatibility
        query = text("""
            INSERT INTO users (email, name, hashed_password, location, region, role, permissions, is_verified, is_active)
            VALUES (:email, :name, :password, 'Admin Location', 'Admin Region', :role, :permissions, 1, 1)
        """)
        
        db.execute(query, {
            'email': admin_data.email,
            'name': admin_data.name,
            'password': hashed_password,
            'role': admin_data.role,
            'permissions': admin_data.permissions
        })
        db.commit()
        
        # Get the created admin
        created_admin = db.query(User).filter(User.email == admin_data.email).first()
        
        return {
            "message": f"Admin user '{admin_data.name}' created successfully",
            "admin_id": created_admin.id,
            "email": admin_data.email,
            "role": admin_data.role,
            "permissions": admin_data.permissions
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating admin user: {str(e)}")

@router.get("/admins")
async def get_admin_users(
    db: Session = Depends(get_db)
):
    """Get all admin users"""
    try:
        # Query admin users using raw SQL for compatibility
        query = text("""
            SELECT id, email, name, role, permissions, is_active, created_at
            FROM users 
            WHERE role IN ('admin', 'super_admin')
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query)
        admins = []
        
        for row in result:
            admins.append({
                "id": row[0],
                "email": row[1],
                "name": row[2],
                "role": row[3] if row[3] else "admin",
                "permissions": row[4] if row[4] else "basic",
                "is_active": bool(row[5]),
                "created_at": row[6]
            })
        
        return {
            "admins": admins,
            "total_count": len(admins)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching admin users: {str(e)}")

@router.put("/admins/{admin_id}/toggle-status")
async def toggle_admin_status(
    admin_id: int,
    db: Session = Depends(get_db)
):
    """Toggle admin user active status"""
    try:
        admin = db.query(User).filter(User.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        # Toggle status
        admin.is_active = not admin.is_active
        db.commit()
        db.refresh(admin)
        
        status = "activated" if admin.is_active else "deactivated"
        return {
            "message": f"Admin user '{admin.name}' has been {status}",
            "admin_id": admin_id,
            "is_active": admin.is_active
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating admin status: {str(e)}")

@router.delete("/admins/{admin_id}")
async def delete_admin_user(
    admin_id: int,
    db: Session = Depends(get_db)
):
    """Delete admin user"""
    try:
        admin = db.query(User).filter(User.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        admin_name = admin.name
        db.delete(admin)
        db.commit()
        
        return {
            "message": f"Admin user '{admin_name}' has been deleted permanently",
            "admin_id": admin_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting admin user: {str(e)}")

# Admin Notification Endpoints
@router.post("/notifications/create")
async def create_admin_notification(
    notification_data: AdminNotificationCreate,
    db: Session = Depends(get_db)
):
    """Create notifications for specific user groups"""
    try:
        from notifications.utils import NotificationService
        from datetime import datetime
        
        service = NotificationService(db)
        
        # Get target users based on group
        target_users = []
        
        if notification_data.target_group == "admins":
            # Get all admin users
            admin_users = db.query(User).filter(
                User.role.in_(["admin", "super_admin"])
            ).all()
            target_users = admin_users
            
        elif notification_data.target_group == "users":
            # Get all regular users (non-admin)
            regular_users = db.query(User).filter(
                ~User.role.in_(["admin", "super_admin"])
            ).all()
            target_users = regular_users
            
        elif notification_data.target_group == "verified":
            # Get all verified users
            verified_users = db.query(User).filter(User.is_verified == True).all()
            target_users = verified_users
            
        elif notification_data.target_group == "unverified":
            # Get all unverified users
            unverified_users = db.query(User).filter(User.is_verified == False).all()
            target_users = unverified_users
            
        elif notification_data.target_group == "all":
            # Get all users
            all_users = db.query(User).all()
            target_users = all_users
        else:
            raise HTTPException(status_code=400, detail="Invalid target group")
        
        # Apply region filter if specified
        if notification_data.region_filter:
            target_users = [user for user in target_users if user.region == notification_data.region_filter]
        
        if not target_users:
            raise HTTPException(status_code=400, detail="No users found for the specified criteria")
        
        # Parse expires_at if provided
        expires_at = None
        if notification_data.expires_at:
            try:
                expires_at = datetime.fromisoformat(notification_data.expires_at.replace('Z', '+00:00'))
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid expires_at format")
        
        # Create notifications for each target user
        created_notifications = []
        for user in target_users:
            notification_dict = {
                "user_id": user.id,
                "type": notification_data.type,
                "title": notification_data.title,
                "message": notification_data.message,
                "priority": notification_data.priority,
                "action_url": notification_data.action_url,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
            
            notification = service.create_notification(notification_dict)
            created_notifications.append(notification.id)
        
        return {
            "message": f"Successfully created {len(created_notifications)} notifications",
            "target_group": notification_data.target_group,
            "target_count": len(target_users),
            "notification_ids": created_notifications,
            "filters": {
                "region": notification_data.region_filter
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating notifications: {str(e)}")

@router.post("/notifications/bulk")
async def create_bulk_notification(
    notification_data: AdminBulkNotificationCreate,
    db: Session = Depends(get_db)
):
    """Create notifications for specific user IDs"""
    try:
        from notifications.utils import NotificationService
        from datetime import datetime
        
        service = NotificationService(db)
        
        # Validate user IDs exist
        existing_users = db.query(User).filter(User.id.in_(notification_data.user_ids)).all()
        existing_user_ids = [user.id for user in existing_users]
        
        if len(existing_user_ids) != len(notification_data.user_ids):
            missing_ids = set(notification_data.user_ids) - set(existing_user_ids)
            raise HTTPException(
                status_code=400, 
                detail=f"Users not found: {list(missing_ids)}"
            )
        
        # Parse expires_at if provided
        expires_at = None
        if notification_data.expires_at:
            try:
                expires_at = datetime.fromisoformat(notification_data.expires_at.replace('Z', '+00:00'))
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid expires_at format")
        
        # Create notifications for each user
        created_notifications = []
        for user_id in notification_data.user_ids:
            notification_dict = {
                "user_id": user_id,
                "type": notification_data.type,
                "title": notification_data.title,
                "message": notification_data.message,
                "priority": notification_data.priority,
                "action_url": notification_data.action_url,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
            
            notification = service.create_notification(notification_dict)
            created_notifications.append(notification.id)
        
        return {
            "message": f"Successfully created {len(created_notifications)} notifications",
            "target_user_ids": notification_data.user_ids,
            "notification_ids": created_notifications
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bulk notifications: {str(e)}")

@router.get("/notifications/history")
async def get_notification_history(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: int = Query(default=None),
    type_filter: str = Query(default=None),
    db: Session = Depends(get_db)
):
    """Get notification history for admin dashboard"""
    try:
        from database import Notification
        
        # Build query
        query = db.query(Notification)
        
        # Apply filters
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        if type_filter:
            query = query.filter(Notification.type == type_filter)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format response
        notification_list = []
        for notif in notifications:
            # Get user info
            user = db.query(User).filter(User.id == notif.user_id).first()
            
            notification_list.append({
                "id": notif.id,
                "user_id": notif.user_id,
                "user_name": user.name if user else "Unknown User",
                "user_email": user.email if user else "Unknown Email",
                "type": notif.type,
                "title": notif.title,
                "message": notif.message,
                "priority": notif.priority,
                "is_read": notif.is_read,
                "action_url": notif.action_url,
                "expires_at": notif.expires_at.isoformat() if notif.expires_at else None,
                "created_at": notif.created_at.isoformat(),
                "read_at": notif.read_at.isoformat() if notif.read_at else None
            })
        
        return {
            "notifications": notification_list,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notification history: {str(e)}")

@router.get("/notifications/stats")
async def get_notification_stats(
    db: Session = Depends(get_db)
):
    """Get notification statistics for admin dashboard"""
    try:
        from database import Notification
        from sqlalchemy import func
        
        # Total notifications
        total_notifications = db.query(Notification).count()
        
        # Read vs unread
        read_notifications = db.query(Notification).filter(Notification.is_read == True).count()
        unread_notifications = db.query(Notification).filter(Notification.is_read == False).count()
        
        # By type
        type_stats = db.query(
            Notification.type,
            func.count(Notification.id).label('count')
        ).group_by(Notification.type).all()
        
        # By priority
        priority_stats = db.query(
            Notification.priority,
            func.count(Notification.id).label('count')
        ).group_by(Notification.priority).all()
        
        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_notifications = db.query(Notification).filter(
            Notification.created_at >= week_ago
        ).count()
        
        return {
            "total_notifications": total_notifications,
            "read_notifications": read_notifications,
            "unread_notifications": unread_notifications,
            "read_rate": round((read_notifications / total_notifications * 100) if total_notifications > 0 else 0, 2),
            "recent_notifications": recent_notifications,
            "by_type": {item.type: item.count for item in type_stats},
            "by_priority": {item.priority: item.count for item in priority_stats}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notification stats: {str(e)}")

@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific notification"""
    try:
        from database import Notification
        
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        db.delete(notification)
        db.commit()
        
        return {
            "message": "Notification deleted successfully",
            "notification_id": notification_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")

@router.get("/users/groups")
async def get_user_groups(
    db: Session = Depends(get_db)
):
    """Get user group statistics for notification targeting"""
    try:
        # Get counts for different user groups
        total_users = db.query(User).count()
        admin_users = db.query(User).filter(User.role.in_(["admin", "super_admin"])).count()
        regular_users = db.query(User).filter(~User.role.in_(["admin", "super_admin"])).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        unverified_users = db.query(User).filter(User.is_verified == False).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # Get users by region
        region_stats = db.execute(text("""
            SELECT region, COUNT(*) as count
            FROM users 
            WHERE region IS NOT NULL AND region != ''
            GROUP BY region
            ORDER BY count DESC
        """)).fetchall()
        
        regions = [{"region": row[0], "count": row[1]} for row in region_stats]
        
        return {
            "total_users": total_users,
            "admin_users": admin_users,
            "regular_users": regular_users,
            "verified_users": verified_users,
            "unverified_users": unverified_users,
            "active_users": active_users,
            "regions": regions,
            "groups": {
                "admins": {"label": "Admin Users", "count": admin_users},
                "users": {"label": "Regular Users", "count": regular_users},
                "verified": {"label": "Verified Users", "count": verified_users},
                "unverified": {"label": "Unverified Users", "count": unverified_users},
                "all": {"label": "All Users", "count": total_users}
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user groups: {str(e)}")
