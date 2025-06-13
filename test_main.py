"""
Basic tests for EcoTrack Ghana API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from main import app
from database import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to EcoTrack Ghana API"
    assert data["version"] == "1.0.0"
    assert "motto" in data

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_ghana_regions(client):
    """Test Ghana regions endpoint"""
    response = client.get("/api/v1/ghana/regions")
    assert response.status_code == 200
    data = response.json()
    assert "regions" in data
    assert len(data["regions"]) == 17  # All Ghana regions
    assert data["total"] == 17

def test_user_registration(client):
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123",
        "location": "Accra, Ghana",
        "region": "Greater Accra"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data

def test_user_login(client):
    """Test user login"""
    # First register a user
    user_data = {
        "email": "login@example.com",
        "name": "Login User",
        "password": "loginpassword123",
        "location": "Kumasi, Ghana",
        "region": "Ashanti"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_activity_creation(client):
    """Test activity creation"""
    # Register and login first
    user_data = {
        "email": "activity@example.com",
        "name": "Activity User",
        "password": "activitypass123",
        "location": "Cape Coast, Ghana",
        "region": "Central"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    
    # Create activity
    activity_data = {
        "type": "trash",
        "title": "Beach Cleanup",
        "description": "Cleaned up Labadi Beach with friends",
        "location": "Labadi Beach, Accra",
        "region": "Greater Accra",
        "photos": [],
        "impact_data": {"bags_collected": 3}
    }
    
    response = client.post(
        "/api/v1/activities/",
        json=activity_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == activity_data["title"]
    assert data["type"] == activity_data["type"]
    assert data["points"] > 0

def test_get_activities(client):
    """Test getting activities"""
    response = client.get("/api/v1/activities/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_challenges_list(client):
    """Test getting challenges list"""
    response = client.get("/api/v1/challenges/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_community_leaderboard(client):
    """Test community leaderboard"""
    response = client.get("/api/v1/community/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_global_stats(client):
    """Test global statistics"""
    response = client.get("/api/v1/community/stats/global")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_activities" in data
    assert "impact_stats" in data

if __name__ == "__main__":
    pytest.main([__file__])
