"""
Role-based access control for EcoTrack Ghana API
"""

from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db, User
from .utils import get_current_user
from functools import wraps

def require_super_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency that ensures the current user is a super admin
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    
    return current_user

def require_admin_or_super_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency that ensures the current user is either admin or super admin
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user

def check_user_permissions(required_role: str):
    """
    Decorator factory for checking user permissions
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if required_role == "super_admin" and current_user.role != "super_admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Super admin privileges required"
                )
            elif required_role == "admin" and current_user.role not in ["admin", "super_admin"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin privileges required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
