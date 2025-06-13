# PowerShell script to access EcoTrack Ghana production database
# Usage: .\access_prod_db.ps1

Write-Host "🌍 EcoTrack Ghana - Production Database Access" -ForegroundColor Green
Write-Host "=" * 60

# Check if we're in the correct directory
if (-not (Test-Path "ecotrack_ghana.db")) {
    Write-Host "❌ Production database not found in current directory" -ForegroundColor Red
    Write-Host "Make sure you're in the EcoTrackAPI directory and the database exists" -ForegroundColor Yellow
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "🔄 Checking required packages..." -ForegroundColor Yellow

$packages = @("pandas", "sqlite3")
foreach ($package in $packages) {
    try {
        python -c "import $package" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $package is installed" -ForegroundColor Green
        } else {
            Write-Host "❌ $package is missing. Installing..." -ForegroundColor Yellow
            pip install $package
        }
    } catch {
        Write-Host "❌ Error checking $package" -ForegroundColor Red
    }
}

# Menu for database access options
Write-Host "`n📋 Choose your database access method:" -ForegroundColor Cyan
Write-Host "1. Interactive Python Database Tool" -ForegroundColor White
Write-Host "2. SQLite Command Line" -ForegroundColor White
Write-Host "3. Quick Database Statistics" -ForegroundColor White
Write-Host "4. Access via Production API" -ForegroundColor White
Write-Host "5. Exit" -ForegroundColor White

$choice = Read-Host "`nEnter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "🚀 Starting Interactive Database Tool..." -ForegroundColor Green
        python production_db_access.py
    }
    "2" {
        Write-Host "🚀 Starting SQLite Command Line..." -ForegroundColor Green
        Write-Host "Type .help for SQLite commands, .quit to exit" -ForegroundColor Yellow
        sqlite3 ecotrack_ghana.db
    }
    "3" {
        Write-Host "📊 Quick Database Statistics..." -ForegroundColor Green
        python -c @"
import sqlite3
import os

db_path = 'ecotrack_ghana.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print('📊 EcoTrack Ghana Database Statistics')
    print('=' * 50)
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    total_records = 0
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f'{table_name}: {count} records')
        total_records += count
    
    print(f'\nTotal records: {total_records}')
    
    # Database size
    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f'Database size: {size_mb:.2f} MB')
    
    conn.close()
else:
    print('❌ Database file not found!')
"@
    }
    "4" {
        Write-Host "🌐 Accessing Production API..." -ForegroundColor Green
        python remote_db_access.py
    }
    "5" {
        Write-Host "👋 Goodbye!" -ForegroundColor Green
        exit 0
    }
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
    }
}
