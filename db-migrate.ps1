# PowerShell script for EcoTrack Ghana database migrations
# Usage: .\db-migrate.ps1 [command] [options]

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [Parameter(Position=1)]
    [string]$Message = "",
    [Parameter(Position=2)]
    [string]$Revision = "head"
)

# Set working directory to script location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "🗄️  EcoTrack Ghana - Database Migrations" -ForegroundColor Green
Write-Host ("=" * 50)

switch ($Command.ToLower()) {
    "help" {
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  status           - Show current migration status"
        Write-Host "  create <message> - Create new migration"
        Write-Host "  upgrade          - Apply all pending migrations"
        Write-Host "  downgrade <rev>  - Downgrade to specific revision"
        Write-Host "  pending          - Show pending migrations"
        Write-Host "  validate         - Validate migration files"
        Write-Host "  reset            - Reset database (destroys all data)"
        Write-Host "  seed             - Seed initial data"
        Write-Host "  schema           - Show database schema info"
        Write-Host "  check-db         - Check database connection"
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  .\db-migrate.ps1 status"
        Write-Host "  .\db-migrate.ps1 create 'Add user preferences'"
        Write-Host "  .\db-migrate.ps1 upgrade"
        Write-Host "  .\db-migrate.ps1 downgrade abc123"
    }
    
    "status" {
        Write-Host "📋 Checking migration status..." -ForegroundColor Blue
        python migrate.py status
    }
    
    "create" {
        if ([string]::IsNullOrEmpty($Message)) {
            Write-Host "❌ Please provide a migration message" -ForegroundColor Red
            Write-Host "Example: .\db-migrate.ps1 create 'Add user preferences table'"
            exit 1
        }
        Write-Host "📝 Creating migration: $Message" -ForegroundColor Blue
        python migrate.py create $Message
    }
    
    "upgrade" {
        Write-Host "⬆️  Upgrading database..." -ForegroundColor Blue
        python migrate.py upgrade $Revision
    }
    
    "downgrade" {
        if ([string]::IsNullOrEmpty($Message)) {
            Write-Host "❌ Please provide revision to downgrade to" -ForegroundColor Red
            Write-Host "Example: .\db-migrate.ps1 downgrade abc123"
            exit 1
        }
        Write-Host "⬇️  Downgrading database to: $Message" -ForegroundColor Yellow
        python migrate.py downgrade $Message
    }
    
    "pending" {
        Write-Host "⏳ Checking pending migrations..." -ForegroundColor Blue
        python migrate.py pending
    }
    
    "validate" {
        Write-Host "🔍 Validating migrations..." -ForegroundColor Blue
        python migrate.py validate
    }
    
    "reset" {
        Write-Host "⚠️  WARNING: This will destroy all data!" -ForegroundColor Red
        $confirm = Read-Host "Type 'RESET' to confirm"
        if ($confirm -eq "RESET") {
            python migrate.py reset
        } else {
            Write-Host "❌ Reset cancelled" -ForegroundColor Yellow
        }
    }
    
    "seed" {
        Write-Host "🌱 Seeding initial data..." -ForegroundColor Green
        python migrate.py seed
    }
    
    "schema" {
        Write-Host "📊 Database schema information..." -ForegroundColor Blue
        python migrate.py schema
    }
    
    "check-db" {
        Write-Host "🔍 Checking database connection..." -ForegroundColor Blue
        python migrate.py check-db
    }
    
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\db-migrate.ps1 help' for available commands"
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Migration command completed!" -ForegroundColor Green
