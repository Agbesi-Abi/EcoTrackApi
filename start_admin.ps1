# PowerShell script to start EcoTrack API with admin enabled
# Usage: .\start_admin.ps1

Write-Host "🌍 Starting EcoTrack Ghana API with Admin Panel" -ForegroundColor Green
Write-Host "=" * 60

# Set environment variables
$env:ENABLE_ADMIN = "true"
$env:ENABLE_DOCS = "true"
$env:ENVIRONMENT = "development"

# Display configuration
Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "  ENABLE_ADMIN: $env:ENABLE_ADMIN" -ForegroundColor Yellow
Write-Host "  ENABLE_DOCS: $env:ENABLE_DOCS" -ForegroundColor Yellow  
Write-Host "  ENVIRONMENT: $env:ENVIRONMENT" -ForegroundColor Yellow

Write-Host "`n🚀 Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "📚 Admin Panel: http://localhost:8000/api/v1/admin/docs" -ForegroundColor Cyan
Write-Host "📖 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

# Start the server
python main.py
