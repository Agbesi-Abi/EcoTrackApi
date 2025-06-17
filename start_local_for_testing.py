#!/usr/bin/env python3
"""
Start local API server for testing
"""

import subprocess
import sys
import os
from pathlib import Path

def start_local_api():
    """Start the local API server"""
    
    print("🚀 Starting Local EcoTrack API")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Make sure you're in the EcoTrackAPI directory")
        return
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn available")
    except ImportError:
        print("❌ Missing requirements. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv('.env.production')
    
    # Create database and seed if needed
    print("🗄️  Setting up database...")
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database setup warning: {e}")
    
    # Create demo users
    try:
        from quick_login_fix import quick_fix
        quick_fix()
    except Exception as e:
        print(f"⚠️  Demo user setup warning: {e}")
    
    print("\n🌐 Starting server at http://localhost:8000")
    print("💡 Update your Expo app to use: http://localhost:8000/api/v1")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 40)
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_local_api()
