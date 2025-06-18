"""
Database models and configuration for EcoTrack Ghana
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env.production (for local development)
# In production (Render), environment variables are set directly in the platform
try:
    load_dotenv('.env.production')
except:
    pass  # Ignore if .env.production doesn't exist (production environment)

# Database URL - prioritize environment variable, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL is set, use SQLite as fallback
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./ecotrack_ghana.db"
    print("⚠️  No DATABASE_URL found, using SQLite fallback")
else:
    print(f"🔗 Database URL found: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else 'Local'}...")

# Only print database type, not the full URL (for security)
if DATABASE_URL.startswith("postgresql"):
    print("🗄️  Using PostgreSQL database")
elif DATABASE_URL.startswith("sqlite"):
    print("🗄️  Using SQLite database (fallback)")
else:
    print("🗄️  Using custom database")


# Database connection parameters
db_pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
db_max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
db_pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
db_pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Create engine with appropriate parameters
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=db_pool_size,
        max_overflow=db_max_overflow,
        pool_timeout=db_pool_timeout,
        pool_recycle=db_pool_recycle,
        pool_pre_ping=True,  # Verify connections before use
        echo=False  # Set to True for SQL debugging
    )
else:
    # SQLite configuration (fallback)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# Association table for challenge participants
challenge_participants = Table(
    'challenge_participants',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('challenge_id', Integer, ForeignKey('challenges.id'), primary_key=True),
    Column('joined_at', DateTime, default=func.now()),
    Column('progress', Float, default=0.0),
    Column('completed', Boolean, default=False)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    location = Column(String, nullable=True)
    region = Column(String, nullable=True)
    total_points = Column(Integer, default=0)
    weekly_points = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="user")  # 'user', 'admin', 'super_admin'
    permissions = Column(String, default="basic")  # 'basic', 'full'
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Impact statistics
    trash_collected = Column(Float, default=0.0)  # in kg
    trees_planted = Column(Integer, default=0)
    co2_saved = Column(Float, default=0.0)  # in kg
    
    # Relationships
    activities = relationship("Activity", back_populates="user")
    challenges = relationship("Challenge", secondary=challenge_participants, back_populates="participants")

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # 'trash', 'trees', 'mobility', 'water', 'energy'
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    points = Column(Integer, nullable=False)
    location = Column(String, nullable=True)
    region = Column(String, nullable=True)
    photos = Column(Text, nullable=True)  # JSON string of photo URLs
    verified = Column(Boolean, default=False)
    impact_data = Column(Text, nullable=True)  # JSON string for additional impact data
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="activities")

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # 'trash', 'trees', 'mobility'
    duration = Column(String, nullable=False)
    points = Column(Integer, nullable=False)
    difficulty = Column(String, nullable=False)  # 'easy', 'medium', 'hard'
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    participants = relationship("User", secondary=challenge_participants, back_populates="challenges")

class Region(Base):
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    capital = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    population = Column(Integer, nullable=True)
    area_km2 = Column(Float, nullable=True)
    
    # Environmental statistics
    total_users = Column(Integer, default=0)
    total_activities = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    trash_collected = Column(Float, default=0.0)
    trees_planted = Column(Integer, default=0)
    co2_saved = Column(Float, default=0.0)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # 'achievement', 'challenge', 'activity', 'verification', 'leaderboard', 'system'
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON string for additional data
    is_read = Column(Boolean, default=False)
    priority = Column(String, default="normal")  # 'low', 'normal', 'high', 'urgent'
    action_url = Column(String, nullable=True)  # Deep link or URL for action
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="notifications")

# Database utility functions
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    
    # Seed Ghana regions if they don't exist
    db = SessionLocal()
    try:
        if db.query(Region).count() == 0:
            regions_data = [
                {"name": "Greater Accra", "capital": "Accra", "code": "GA", "population": 5455692},
                {"name": "Ashanti", "capital": "Kumasi", "code": "AS", "population": 5440463},
                {"name": "Western", "capital": "Sekondi-Takoradi", "code": "WP", "population": 2060585},
                {"name": "Central", "capital": "Cape Coast", "code": "CP", "population": 2859821},
                {"name": "Eastern", "capital": "Koforidua", "code": "EP", "population": 2106696},
                {"name": "Volta", "capital": "Ho", "code": "TV", "population": 1635421},
                {"name": "Northern", "capital": "Tamale", "code": "NP", "population": 1972757},
                {"name": "Upper East", "capital": "Bolgatanga", "code": "UE", "population": 920089},
                {"name": "Upper West", "capital": "Wa", "code": "UW", "population": 576583},
                {"name": "Brong-Ahafo", "capital": "Sunyani", "code": "BA", "population": 1815408},
                {"name": "Western North", "capital": "Sefwi Wiawso", "code": "WN", "population": 678555},
                {"name": "Ahafo", "capital": "Goaso", "code": "AH", "population": 563677},
                {"name": "Bono", "capital": "Sunyani", "code": "BO", "population": 691983},
                {"name": "Bono East", "capital": "Techiman", "code": "BE", "population": 1208649},
                {"name": "Oti", "capital": "Dambai", "code": "OT", "population": 563677},
                {"name": "North East", "capital": "Nalerigu", "code": "NE", "population": 466026},
                {"name": "Savannah", "capital": "Damongo", "code": "SV", "population": 685801}
            ]
            
            for region_data in regions_data:
                region = Region(**region_data)
                db.add(region)
            
            db.commit()
            print("✅ Seeded Ghana regions data")
    except Exception as e:
        print(f"❌ Error seeding regions: {e}")
        db.rollback()
    finally:
        db.close()
