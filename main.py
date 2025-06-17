"""
EcoTrack Ghana - FastAPI Backend
A sustainable environmental tracking application for Ghana
"""

import sys
import os

# Windows compatibility fixes
if sys.platform == "win32":
    # Fix Windows handle issues
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)
    
    # Disable output buffering on Windows
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import init_db, engine
from sqlalchemy import text
from auth.routes import router as auth_router
from activities.routes import router as activities_router
from challenges.routes import router as challenges_router
from community.routes import router as community_router
from users.routes import router as users_router
from admin.routes import router as admin_router
from notifications.routes import router as notifications_router

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "false").lower() == "true"
ENABLE_ADMIN = os.getenv("ENABLE_ADMIN", "false").lower() == "true"

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    if DEBUG:
        print("🌍 EcoTrack Ghana API started successfully!")
        print("📚 API Documentation: http://localhost:8000/docs")
    else:
        print("🌍 EcoTrack Ghana API started in production mode")
    yield
    # Shutdown (if needed)
    print("🔄 EcoTrack Ghana API shutting down...")

# Create FastAPI app
app = FastAPI(
    title="EcoTrack Ghana API",
    description="Backend API for EcoTrack Ghana - Environmental tracking for a sustainable future",
    version="1.0.0",
    docs_url="/docs" if (DEBUG or ENABLE_DOCS) else None,  # Enable docs if DEBUG or ENABLE_DOCS
    redoc_url="/redoc" if (DEBUG or ENABLE_DOCS) else None,  # Enable redoc if DEBUG or ENABLE_DOCS
    openapi_url="/openapi.json" if (DEBUG or ENABLE_DOCS) else None,  # Enable OpenAPI schema if DEBUG or ENABLE_DOCS
    lifespan=lifespan
)

# CORS configuration
if ENVIRONMENT == "development":
    allowed_origins = [
        "http://localhost:3000",  # React admin dashboard
        "http://127.0.0.1:3000",
        "http://localhost:8081",  # Expo dev server
        "http://127.0.0.1:8081",
        "*"  # Allow all for development
    ]
else:
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
        "https://ecotrack-admin.vercel.app",
        "https://ecotrack-ghana.vercel.app"
    ]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Only print debug info in development
if DEBUG and ENVIRONMENT != "production":
    try:
        print(f"🔧 CORS allowed origins: {allowed_origins}")
        print(f"🔧 Admin enabled: {ENABLE_ADMIN}")
        print(f"🔧 Environment: {ENVIRONMENT}")
    except OSError:
        # Handle Windows output issues
        pass

# Create uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# API version prefix
api_v1_prefix = "/api/v1"

# Include routers
app.include_router(auth_router, prefix=f"{api_v1_prefix}/auth", tags=["Authentication"])
app.include_router(activities_router, prefix=f"{api_v1_prefix}/activities", tags=["Activities"])
app.include_router(challenges_router, prefix=f"{api_v1_prefix}/challenges", tags=["Challenges"])
app.include_router(community_router, prefix=f"{api_v1_prefix}/community", tags=["Community"])
app.include_router(users_router, prefix=f"{api_v1_prefix}/users", tags=["Users"])
app.include_router(notifications_router, prefix=f"{api_v1_prefix}/notifications", tags=["Notifications"])

# Admin routes (only in development or when explicitly enabled)
if DEBUG or ENABLE_ADMIN:
    app.include_router(admin_router, prefix=f"{api_v1_prefix}/admin", tags=["Admin"])

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "🌍 Welcome to EcoTrack Ghana API",
        "version": os.getenv("PROJECT_VERSION", "1.0.0"),
        "status": "healthy",
        "environment": ENVIRONMENT,
        "motto": "Yɛ bɛyɛ yiye - We will make it better"
    }

@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "EcoTrack Ghana API",
        "environment": ENVIRONMENT,
        "version": os.getenv("PROJECT_VERSION", "1.0.0"),
        "database_type": "postgresql" if os.getenv("DATABASE_URL", "").startswith("postgresql") else "sqlite"
    }

# Ghana-specific data endpoint
@app.get(f"{api_v1_prefix}/ghana/regions")
async def get_ghana_regions():
    """Get list of Ghana regions with capitals"""
    regions = [
        {"name": "Greater Accra", "capital": "Accra", "code": "GA"},
        {"name": "Ashanti", "capital": "Kumasi", "code": "AS"},
        {"name": "Western", "capital": "Sekondi-Takoradi", "code": "WP"},
        {"name": "Central", "capital": "Cape Coast", "code": "CP"},
        {"name": "Eastern", "capital": "Koforidua", "code": "EP"},
        {"name": "Volta", "capital": "Ho", "code": "TV"},
        {"name": "Northern", "capital": "Tamale", "code": "NP"},
        {"name": "Upper East", "capital": "Bolgatanga", "code": "UE"},
        {"name": "Upper West", "capital": "Wa", "code": "UW"},
        {"name": "Brong-Ahafo", "capital": "Sunyani", "code": "BA"},
        {"name": "Western North", "capital": "Sefwi Wiawso", "code": "WN"},
        {"name": "Ahafo", "capital": "Goaso", "code": "AH"},
        {"name": "Bono", "capital": "Sunyani", "code": "BO"},
        {"name": "Bono East", "capital": "Techiman", "code": "BE"},
        {"name": "Oti", "capital": "Dambai", "code": "OT"},
        {"name": "North East", "capital": "Nalerigu", "code": "NE"},
        {"name": "Savannah", "capital": "Damongo", "code": "SV"}    ]
    return {"regions": regions, "total": len(regions)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Windows-compatible uvicorn configuration
    config = {
        "app": "main:app",
        "host": host,
        "port": port,
        "reload": DEBUG,
        "log_level": "info" if DEBUG else "warning",
        "access_log": DEBUG,
        "workers": 1,  # Single worker to avoid Windows multiprocessing issues
    }
    
    # Additional Windows-specific settings
    if sys.platform == "win32":
        config["loop"] = "asyncio"
        config["lifespan"] = "on"
    
    try:
        uvicorn.run(**config)
    except OSError as e:
        if "handle is invalid" in str(e):
            print("Windows handle error detected. Try running with: python -m uvicorn main:app --reload --port 8000 --workers 1")
        else:
            raise
