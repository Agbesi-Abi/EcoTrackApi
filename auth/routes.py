"""
Authentication routes for EcoTrack Ghana
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import os

from database import get_db, User
from .schemas import UserCreate, UserResponse, Token, UserLogin
from .utils import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_current_user
)
from notifications.utils import trigger_welcome_notification

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Token expiration settings
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        location=user_data.location,
        region=user_data.region
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Trigger welcome notification
    try:
        trigger_welcome_notification(db, db_user.id, db_user.name)
    except Exception as e:
        # Don't fail registration if notification fails
        print(f"Failed to create welcome notification: {e}")
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        name=db_user.name,
        location=db_user.location,
        region=db_user.region,
        role=db_user.role,
        permissions=db_user.permissions,
        is_active=db_user.is_active,
        total_points=db_user.total_points,
        weekly_points=db_user.weekly_points,
        rank=db_user.rank,
        is_verified=db_user.is_verified,
        created_at=db_user.created_at,
        impact_stats={
            "trash_collected": db_user.trash_collected,
            "trees_planted": db_user.trees_planted,
            "co2_saved": db_user.co2_saved
        }
    )

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token"""
    
    # Get user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
      # Create refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            location=user.location,
            region=user.region,
            role=user.role or "user",
            permissions=user.permissions or "basic",
            is_active=user.is_active if user.is_active is not None else True,
            total_points=user.total_points or 0,
            weekly_points=user.weekly_points or 0,
            rank=user.rank or 0,
            is_verified=user.is_verified if user.is_verified is not None else False,
            created_at=user.created_at or datetime.utcnow(),
            impact_stats={
                "trash_collected": user.trash_collected or 0.0,
                "trees_planted": user.trees_planted or 0,
                "co2_saved": user.co2_saved or 0.0
            }
        )
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    
    try:
        payload = verify_token(refresh_token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            location=user.location,
            region=user.region,
            role=user.role or "user",
            permissions=user.permissions or "basic",
            is_active=user.is_active if user.is_active is not None else True,
            total_points=user.total_points or 0,
            weekly_points=user.weekly_points or 0,
            rank=user.rank or 0,
            is_verified=user.is_verified if user.is_verified is not None else False,
            created_at=user.created_at or datetime.utcnow(),
            impact_stats={
                "trash_collected": user.trash_collected or 0.0,
                "trees_planted": user.trees_planted or 0,
                "co2_saved": user.co2_saved or 0.0
            }
        )
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        location=current_user.location,
        region=current_user.region,
        role=current_user.role or "user",
        permissions=current_user.permissions or "basic",
        is_active=current_user.is_active if current_user.is_active is not None else True,
        total_points=current_user.total_points or 0,
        weekly_points=current_user.weekly_points or 0,
        rank=current_user.rank or 0,
        is_verified=current_user.is_verified if current_user.is_verified is not None else False,
        created_at=current_user.created_at or datetime.utcnow(),
        impact_stats={
            "trash_collected": current_user.trash_collected or 0.0,
            "trees_planted": current_user.trees_planted or 0,
            "co2_saved": current_user.co2_saved or 0.0
        }
    )

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}
