# PowerShell script to test role-based access control
# Usage: .\test_admin_roles.ps1

Write-Host "🌍 EcoTrack Ghana - Role-Based Access Control Test" -ForegroundColor Green
Write-Host "=" * 60

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Navigate to the API directory
$apiPath = "c:\Users\Abigail Adwoa Agbesi\Desktop\GhanaClean\EcoTrackAPI"
if (Test-Path $apiPath) {
    Set-Location $apiPath
    Write-Host "📁 Changed to API directory: $apiPath" -ForegroundColor Cyan
} else {
    Write-Host "❌ API directory not found: $apiPath" -ForegroundColor Red
    exit 1
}

# Step 1: Create test users
Write-Host "`n🔧 Step 1: Creating test users..." -ForegroundColor Yellow
try {
    python create_test_users.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create test users" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error running create_test_users.py: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Start the backend server in background
Write-Host "`n🚀 Step 2: Starting backend server..." -ForegroundColor Yellow

# Check if server is already running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend server is already running" -ForegroundColor Green
        $serverAlreadyRunning = $true
    }
} catch {
    $serverAlreadyRunning = $false
}

if (-not $serverAlreadyRunning) {
    Write-Host "Starting FastAPI backend server..." -ForegroundColor Cyan
    
    # Set environment variables
    $env:ENVIRONMENT = "development"
    $env:ENABLE_ADMIN = "true"
    
    # Start server in background
    $serverProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -NoNewWindow -PassThru
    
    # Wait for server to start
    Write-Host "Waiting for server to start..." -ForegroundColor Cyan
    $maxAttempts = 30
    $attempt = 0
    
    do {
        Start-Sleep -Seconds 2
        $attempt++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Backend server started successfully" -ForegroundColor Green
                break
            }
        } catch {
            if ($attempt -eq $maxAttempts) {
                Write-Host "❌ Backend server failed to start within timeout" -ForegroundColor Red
                if ($serverProcess) {
                    Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
                }
                exit 1
            }
        }
        Write-Host "." -NoNewline -ForegroundColor Yellow
    } while ($attempt -lt $maxAttempts)
}

# Step 3: Run access control tests
Write-Host "`n🧪 Step 3: Running access control tests..." -ForegroundColor Yellow
try {
    python test_role_based_access.py
} catch {
    Write-Host "❌ Error running access control tests: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Open admin dashboard
Write-Host "`n🌐 Step 4: Testing frontend access..." -ForegroundColor Yellow
Write-Host "Opening admin dashboard in browser..." -ForegroundColor Cyan

# Navigate to admin frontend directory
$adminPath = "c:\Users\Abigail Adwoa Agbesi\Desktop\GhanaClean\ecotrack-admin"
if (Test-Path $adminPath) {
    Set-Location $adminPath
    
    # Check if npm is available
    try {
        $npmVersion = npm --version 2>&1
        Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ npm not found. Please install Node.js first." -ForegroundColor Red
        Write-Host "You can manually test by opening: http://localhost:3000" -ForegroundColor Yellow
        return
    }
    
    # Start frontend if not running
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Host "✅ Frontend is already running" -ForegroundColor Green
        }
    } catch {
        Write-Host "Starting React frontend..." -ForegroundColor Cyan
        Start-Process -FilePath "npm" -ArgumentList "start" -NoNewWindow
        Start-Sleep -Seconds 5
    }
    
    # Open browser
    Start-Process "http://localhost:3000"
    
} else {
    Write-Host "⚠️  Admin frontend directory not found: $adminPath" -ForegroundColor Yellow
    Write-Host "You can manually open: http://localhost:3000" -ForegroundColor Yellow
}

Write-Host "`n✅ Test setup complete!" -ForegroundColor Green
Write-Host "`n📋 Test Users Created:" -ForegroundColor Cyan
Write-Host "1. Super Admin:" -ForegroundColor White
Write-Host "   Email: superadmin@ecotrack.com" -ForegroundColor Gray
Write-Host "   Password: superadmin123" -ForegroundColor Gray
Write-Host "   Access: Database + Admin Management + User Verification" -ForegroundColor Gray

Write-Host "`n2. Regular Admin:" -ForegroundColor White
Write-Host "   Email: admin@ecotrack.com" -ForegroundColor Gray
Write-Host "   Password: admin123" -ForegroundColor Gray
Write-Host "   Access: User Verification Only" -ForegroundColor Gray

Write-Host "`n3. Regular User:" -ForegroundColor White
Write-Host "   Email: user@ecotrack.com" -ForegroundColor Gray
Write-Host "   Password: user123" -ForegroundColor Gray
Write-Host "   Access: No Admin Features" -ForegroundColor Gray

Write-Host "`n🎯 How to Test:" -ForegroundColor Yellow
Write-Host "1. Login to admin dashboard (http://localhost:3000) with each user" -ForegroundColor White
Write-Host "2. Super admin should see 'Database' and 'Admin Users' tabs" -ForegroundColor White  
Write-Host "3. Regular admin should NOT see 'Database' and 'Admin Users' tabs" -ForegroundColor White
Write-Host "4. Regular user should not be able to login to admin dashboard" -ForegroundColor White

Write-Host "`n⚠️  Remember to stop the server when done:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C in the terminal running uvicorn" -ForegroundColor Gray

Write-Host "`n" + "=" * 60 -ForegroundColor Green
