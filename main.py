"""
EcoTrack Ghana - FastAPI Backend
A sustainable environmental tracking application for Ghana
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import init_db
from auth.routes import router as auth_router
from activities.routes import router as activities_router
from challenges.routes import router as challenges_router
from community.routes import router as community_router
from users.routes import router as users_router
from admin.routes import router as admin_router

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "false").lower() == "true"

# Create FastAPI app
app = FastAPI(
    title="EcoTrack Ghana API",
    description="Backend API for EcoTrack Ghana - Environmental tracking for a sustainable future",
    version="1.0.0",
    docs_url="/docs" if (DEBUG or ENABLE_DOCS) else None,  # Enable docs if DEBUG or ENABLE_DOCS
    redoc_url="/redoc" if (DEBUG or ENABLE_DOCS) else None,  # Enable redoc if DEBUG or ENABLE_DOCS
    openapi_url="/openapi.json" if (DEBUG or ENABLE_DOCS) else None  # Enable OpenAPI schema if DEBUG or ENABLE_DOCS
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

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

# Admin routes (only in development)
if DEBUG:
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
    return {
        "status": "healthy",
        "service": "EcoTrack Ghana API",
        "environment": ENVIRONMENT,
        "version": os.getenv("PROJECT_VERSION", "1.0.0")
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
        {"name": "Savannah", "capital": "Damongo", "code": "SV"}
    ]
    return {"regions": regions, "total": len(regions)}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    if DEBUG:
        print("🌍 EcoTrack Ghana API started successfully!")
        print("📚 API Documentation: http://localhost:8000/docs")
    else:
        print("🌍 EcoTrack Ghana API started in production mode")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )
