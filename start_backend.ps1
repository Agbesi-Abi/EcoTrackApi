# EcoTrack Backend Server Startup Script
Write-Host "🌍 Starting EcoTrack Backend Server..." -ForegroundColor Green
Write-Host "=" * 50

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Start the FastAPI server
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Yellow
python main.py
