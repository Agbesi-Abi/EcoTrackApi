#!/usr/bin/env pwsh
# EcoTrack Ghana API - Production Deployment Script for Windows PowerShell

param(
    [Parameter()]
    [string]$Environment = "production",
    
    [Parameter()]
    [switch]$SkipBuild,
    
    [Parameter()]
    [switch]$Force
)

Write-Host "🌍 EcoTrack Ghana API - Production Deployment" -ForegroundColor Green
Write-Host "=============================================="

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Set working directory to API folder
$ApiPath = Join-Path $PSScriptRoot "EcoTrackAPI"
if (-not (Test-Path $ApiPath)) {
    Write-Host "❌ EcoTrackAPI directory not found at $ApiPath" -ForegroundColor Red
    exit 1
}

Set-Location $ApiPath

# Create production environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.production") {
        Write-Host "📝 Creating production environment file..." -ForegroundColor Yellow
        Copy-Item ".env.production" ".env"
        Write-Host ""
        Write-Host "⚠️  IMPORTANT: Please edit .env file with your production values!" -ForegroundColor Yellow
        Write-Host "   - JWT_SECRET_KEY: Use a strong 256-character secret" -ForegroundColor Yellow
        Write-Host "   - DATABASE_URL: Configure your PostgreSQL connection" -ForegroundColor Yellow
        Write-Host "   - ALLOWED_ORIGINS: Set your actual domain URLs" -ForegroundColor Yellow
        Write-Host ""
        
        if (-not $Force) {
            $response = Read-Host "Press Enter when you've configured the .env file, or 'q' to quit"
            if ($response -eq 'q') {
                exit 0
            }
        }
    } else {
        Write-Host "❌ .env.production template not found" -ForegroundColor Red
        exit 1
    }
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Blue
@("logs", "ssl", "uploads") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "   Created: $_" -ForegroundColor Gray
    }
}

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Blue
docker-compose -f docker-compose.production.yml down 2>$null

if (-not $SkipBuild) {
    # Build containers
    Write-Host "🔨 Building Docker containers..." -ForegroundColor Blue
    docker-compose -f docker-compose.production.yml build --no-cache
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed" -ForegroundColor Red
        exit 1
    }
}

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Blue
docker-compose -f docker-compose.production.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check API health
Write-Host "🔍 Checking API health..." -ForegroundColor Blue
$maxAttempts = 30
$attempt = 0
$apiHealthy = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API is running successfully!" -ForegroundColor Green
            $apiHealthy = $true
            break
        }
    } catch {
        # Continue trying
    }
    
    $attempt++
    Write-Host "   Attempt $attempt/$maxAttempts - waiting for API..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

if (-not $apiHealthy) {
    Write-Host "❌ API failed to start. Check logs with:" -ForegroundColor Red
    Write-Host "   docker-compose -f docker-compose.production.yml logs api" -ForegroundColor Red
    exit 1
}

# Show service status
Write-Host ""
Write-Host "🎉 EcoTrack Ghana API deployed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Blue
docker-compose -f docker-compose.production.yml ps

Write-Host ""
Write-Host "🔗 Access Points:" -ForegroundColor Blue
Write-Host "   API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "   Database: PostgreSQL on localhost:5432" -ForegroundColor Cyan

# Test API endpoint
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health"
    Write-Host ""
    Write-Host "🏥 Health Check Response:" -ForegroundColor Blue
    Write-Host "   Status: $($healthResponse.status)" -ForegroundColor Cyan
    Write-Host "   Environment: $($healthResponse.environment)" -ForegroundColor Cyan
    Write-Host "   Version: $($healthResponse.version)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  Could not fetch health status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Blue
Write-Host "   1. Configure SSL certificates in .\ssl\ directory" -ForegroundColor Gray
Write-Host "   2. Update DNS to point to your server" -ForegroundColor Gray
Write-Host "   3. Configure your domain in ALLOWED_ORIGINS" -ForegroundColor Gray
Write-Host "   4. Set up monitoring and backups" -ForegroundColor Gray
Write-Host "   5. Test all endpoints" -ForegroundColor Gray

Write-Host ""
Write-Host "📝 Useful Commands:" -ForegroundColor Blue
Write-Host "   View logs: docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor Gray
Write-Host "   Stop services: docker-compose -f docker-compose.production.yml down" -ForegroundColor Gray
Write-Host "   Restart API: docker-compose -f docker-compose.production.yml restart api" -ForegroundColor Gray
Write-Host "   Update deployment: .\deploy.ps1 -SkipBuild" -ForegroundColor Gray

Write-Host ""
Write-Host "Yɛ bɛyɛ yiye - We will make it better! 🇬🇭" -ForegroundColor Green
