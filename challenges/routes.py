"""
Challenges routes for EcoTrack Ghana
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db, Challenge, User, challenge_participants
from auth.utils import get_current_user, get_optional_current_user
from .schemas import ChallengeCreate, ChallengeResponse, ChallengeUpdate, ChallengeParticipation

router = APIRouter()

@router.get("/", response_model=List[ChallengeResponse])
async def get_challenges(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    active_only: bool = True,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get list of challenges with optional filters"""
    
    query = db.query(Challenge)
    
    # Apply filters
    if category:
        query = query.filter(Challenge.category == category)
    if difficulty:
        query = query.filter(Challenge.difficulty == difficulty)
    if active_only:
        query = query.filter(Challenge.is_active == True)
    
    challenges = query.order_by(desc(Challenge.created_at)).offset(skip).limit(limit).all()
    
    challenge_responses = []
    for challenge in challenges:
        # Get participant count
        participant_count = db.query(func.count(challenge_participants.c.user_id)).filter(
            challenge_participants.c.challenge_id == challenge.id
        ).scalar()
        
        # Check if current user has joined
        joined = False
        progress = 0.0
        if current_user:
            participation = db.query(challenge_participants).filter(
                challenge_participants.c.user_id == current_user.id,
                challenge_participants.c.challenge_id == challenge.id
            ).first()
            if participation:
                joined = True
                progress = participation.progress
        
        challenge_responses.append(ChallengeResponse(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            category=challenge.category,
            duration=challenge.duration,
            points=challenge.points,
            difficulty=challenge.difficulty,
            participants=participant_count,
            joined=joined,
            progress=progress,
            is_active=challenge.is_active,
            start_date=challenge.start_date,
            end_date=challenge.end_date,
            created_at=challenge.created_at
        ))
    
    return challenge_responses

@router.get("/my", response_model=List[ChallengeResponse])
async def get_my_challenges(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's joined challenges"""
    
    # Get challenges user has joined
    user_challenges = db.query(Challenge).join(
        challenge_participants,
        Challenge.id == challenge_participants.c.challenge_id
    ).filter(
        challenge_participants.c.user_id == current_user.id
    ).order_by(desc(challenge_participants.c.joined_at)).offset(skip).limit(limit).all()
    
    challenge_responses = []
    for challenge in user_challenges:
        # Get participant count
        participant_count = db.query(func.count(challenge_participants.c.user_id)).filter(
            challenge_participants.c.challenge_id == challenge.id
        ).scalar()
        
        # Get user's progress
        participation = db.query(challenge_participants).filter(
            challenge_participants.c.user_id == current_user.id,
            challenge_participants.c.challenge_id == challenge.id
        ).first()
        
        challenge_responses.append(ChallengeResponse(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            category=challenge.category,
            duration=challenge.duration,
            points=challenge.points,
            difficulty=challenge.difficulty,
            participants=participant_count,
            joined=True,
            progress=participation.progress if participation else 0.0,
            is_active=challenge.is_active,
            start_date=challenge.start_date,
            end_date=challenge.end_date,
            created_at=challenge.created_at
        ))
    
    return challenge_responses

@router.post("/", response_model=ChallengeResponse)
async def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new challenge (admin only for now)"""
    
    # For now, allow any user to create challenges
    # In production, you might want to restrict this to admin users
    
    db_challenge = Challenge(
        title=challenge_data.title,
        description=challenge_data.description,
        category=challenge_data.category,
        duration=challenge_data.duration,
        points=challenge_data.points,
        difficulty=challenge_data.difficulty,
        start_date=challenge_data.start_date,
        end_date=challenge_data.end_date
    )
    
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    
    return ChallengeResponse(
        id=db_challenge.id,
        title=db_challenge.title,
        description=db_challenge.description,
        category=db_challenge.category,
        duration=db_challenge.duration,
        points=db_challenge.points,
        difficulty=db_challenge.difficulty,
        participants=0,
        joined=False,
        progress=0.0,
        is_active=db_challenge.is_active,
        start_date=db_challenge.start_date,
        end_date=db_challenge.end_date,
        created_at=db_challenge.created_at
    )

@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: int,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get specific challenge by ID"""
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # Get participant count
    participant_count = db.query(func.count(challenge_participants.c.user_id)).filter(
        challenge_participants.c.challenge_id == challenge.id
    ).scalar()
    
    # Check if current user has joined
    joined = False
    progress = 0.0
    if current_user:
        participation = db.query(challenge_participants).filter(
            challenge_participants.c.user_id == current_user.id,
            challenge_participants.c.challenge_id == challenge.id
        ).first()
        if participation:
            joined = True
            progress = participation.progress
    
    return ChallengeResponse(
        id=challenge.id,
        title=challenge.title,
        description=challenge.description,
        category=challenge.category,
        duration=challenge.duration,
        points=challenge.points,
        difficulty=challenge.difficulty,
        participants=participant_count,
        joined=joined,
        progress=progress,
        is_active=challenge.is_active,
        start_date=challenge.start_date,
        end_date=challenge.end_date,
        created_at=challenge.created_at
    )

@router.post("/{challenge_id}/join")
async def join_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a challenge"""
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    if not challenge.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge is not active"
        )
    
    # Check if user already joined
    existing = db.query(challenge_participants).filter(
        challenge_participants.c.user_id == current_user.id,
        challenge_participants.c.challenge_id == challenge_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already joined this challenge"
        )
    
    # Add user to challenge
    db.execute(
        challenge_participants.insert().values(
            user_id=current_user.id,
            challenge_id=challenge_id,
            joined_at=datetime.utcnow()
        )
    )
    db.commit()
    
    return {"message": "Successfully joined challenge"}

@router.post("/{challenge_id}/leave")
async def leave_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a challenge"""
    
    # Check if user has joined the challenge
    participation = db.query(challenge_participants).filter(
        challenge_participants.c.user_id == current_user.id,
        challenge_participants.c.challenge_id == challenge_id
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not joined to this challenge"
        )
    
    # Remove user from challenge
    db.execute(
        challenge_participants.delete().where(
            challenge_participants.c.user_id == current_user.id,
            challenge_participants.c.challenge_id == challenge_id
        )
    )
    db.commit()
    
    return {"message": "Successfully left challenge"}

@router.put("/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: int,
    progress_data: ChallengeParticipation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress in a challenge"""
    
    # Check if user has joined the challenge
    participation = db.query(challenge_participants).filter(
        challenge_participants.c.user_id == current_user.id,
        challenge_participants.c.challenge_id == challenge_id
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not joined to this challenge"
        )
    
    # Update progress
    db.execute(
        challenge_participants.update().where(
            challenge_participants.c.user_id == current_user.id,
            challenge_participants.c.challenge_id == challenge_id
        ).values(
            progress=min(progress_data.progress, 100.0),
            completed=progress_data.progress >= 100.0
        )
    )
    db.commit()
    
    # Award points if challenge completed
    if progress_data.progress >= 100.0:
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if challenge:
            current_user.total_points += challenge.points
            current_user.weekly_points += challenge.points
            db.commit()
    
    return {"message": "Progress updated successfully"}

@router.get("/{challenge_id}/participants", response_model=List[dict])
async def get_challenge_participants(
    challenge_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get challenge participants with their progress"""
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # Get participants with their progress
    participants = db.query(User, challenge_participants.c.progress, challenge_participants.c.joined_at).join(
        challenge_participants,
        User.id == challenge_participants.c.user_id
    ).filter(
        challenge_participants.c.challenge_id == challenge_id
    ).order_by(desc(challenge_participants.c.progress)).offset(skip).limit(limit).all()
    
    return [
        {
            "user_id": user.id,
            "name": user.name,
            "location": user.location,
            "progress": progress,
            "joined_at": joined_at,
            "total_points": user.total_points
        }
        for user, progress, joined_at in participants
    ]
