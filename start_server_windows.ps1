# Windows-compatible server startup script for EcoTrack API
# This avoids multiprocessing issues on Windows

Write-Host "🌍 Starting EcoTrack Ghana API Server..." -ForegroundColor Green

# Change to the API directory
Set-Location "c:\Users\Abigail Adwoa Agbesi\Desktop\GhanaClean\EcoTrackAPI"

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  No virtual environment found. Using global Python..." -ForegroundColor Yellow
}

# Set environment variables for Windows
$env:PYTHONPATH = (Get-Location).Path
$env:ENVIRONMENT = "development"
$env:DEBUG = "true"

Write-Host "🚀 Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "📝 API docs available at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "👨‍💼 Admin panel at http://localhost:3000" -ForegroundColor Cyan
Write-Host "" 
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

# Start uvicorn with Windows-compatible settings
# Using --workers 1 to avoid multiprocessing issues on Windows
try {
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --workers 1 --access-log
} catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    Write-Host "Please check that all dependencies are installed:" -ForegroundColor Yellow
    Write-Host "pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host "Server stopped." -ForegroundColor Yellow
