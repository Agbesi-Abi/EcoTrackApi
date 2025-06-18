#!/usr/bin/env python3
"""
Render Deployment Helper for EcoTrack Ghana
Checks configuration and provides deployment guidance
"""

import os
import sys
from dotenv import load_dotenv

def check_environment_config():
    """Check if environment is properly configured for PostgreSQL"""
    print("🔍 EcoTrack Ghana - Environment Configuration Check")
    print("=" * 55)
    
    # Load local environment for comparison
    load_dotenv('.env.production')
    local_db_url = os.getenv('DATABASE_URL')
    
    if local_db_url and local_db_url.startswith('postgresql'):
        print("✅ Local .env.production has PostgreSQL configured")
        print(f"🔗 Database: {local_db_url.split('@')[1].split('/')[0] if '@' in local_db_url else 'Unknown'}")
    else:
        print("❌ Local .env.production missing or not using PostgreSQL")
        return False
    
    return True

def display_render_setup_instructions():
    """Display step-by-step Render setup instructions"""
    print("\n🚀 Render Environment Variables Setup Instructions")
    print("=" * 55)
    
    print("1. Go to your Render dashboard: https://dashboard.render.com")
    print("2. Find and click on your 'ecotrack-ghana-api' service")
    print("3. Go to the 'Environment' tab")
    print("4. Add/update these environment variables:")
    print()
    
    # Load variables from local env
    load_dotenv('.env.production')
    
    critical_vars = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'ENVIRONMENT': 'production',
        'DEBUG': 'False',
        'ENABLE_DOCS': 'true',
        'ENABLE_ADMIN': 'true',
        'DB_POOL_SIZE': '10',
        'DB_MAX_OVERFLOW': '20',
        'DB_POOL_TIMEOUT': '30',
        'DB_POOL_RECYCLE': '3600',
        'JWT_SECRET_KEY': 'GENERATE_NEW_SECURE_KEY',
        'JWT_ALGORITHM': 'HS256',
        'JWT_ACCESS_TOKEN_EXPIRE_MINUTES': '30',
        'JWT_REFRESH_TOKEN_EXPIRE_DAYS': '7',
        'MAX_FILE_SIZE': '5242880',
        'ALLOWED_IMAGE_TYPES': 'image/jpeg,image/png,image/webp',
        'ALLOWED_ORIGINS': 'https://ecotrack-online.onrender.com/api/v1,http://localhost:3000',
        'RATE_LIMIT_PER_MINUTE': '100',
        'LOG_LEVEL': 'WARNING',
        'DEFAULT_REGION': 'Greater Accra'
    }
    
    print("📋 Environment Variables to Set:")
    print("-" * 40)
    for key, value in critical_vars.items():
        if key == 'DATABASE_URL' and value:
            # Hide password in display
            display_value = value.split('@')[0].split(':')[:-1]
            display_value = ':'.join(display_value) + ':***@' + value.split('@')[1]
            print(f"   {key} = {display_value}")
        elif key == 'JWT_SECRET_KEY':
            print(f"   {key} = [Generate new secure key in Render]")
        else:
            print(f"   {key} = {value}")
    
    print("\n🔧 After adding variables:")
    print("5. Click 'Deploy Latest Commit' or trigger a new deployment")
    print("6. Monitor the logs for: '🗄️  Using PostgreSQL database'")
    print("7. If successful, run database migrations")

def generate_jwt_secret():
    """Generate a secure JWT secret"""
    import secrets
    secret = secrets.token_urlsafe(32)
    print(f"\n🔐 Generated secure JWT secret:")
    print(f"JWT_SECRET_KEY={secret}")
    print("Copy this and paste it into Render's environment variables")

def check_deployment_status():
    """Check if deployment is using PostgreSQL"""
    print("\n📊 Deployment Status Check")
    print("=" * 30)
    print("After deployment, check your Render logs for:")
    print("✅ GOOD: '🗄️  Using PostgreSQL database'")
    print("❌ BAD:  '🗄️  Using SQLite database (fallback)'")
    print()
    print("If you see SQLite, the environment variables weren't set correctly.")

def show_migration_commands():
    """Show commands to run after successful PostgreSQL deployment"""
    print("\n🗄️  Database Migration Commands")
    print("=" * 35)
    print("After PostgreSQL is working, run these commands:")
    print()
    print("# Option 1: Use the web service shell (if available)")
    print("python migrate.py status")
    print("python migrate.py upgrade")
    print("python migrate.py seed")
    print()
    print("# Option 2: Add migration to your deployment script")
    print("# Add this to your start command or create a separate job")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--jwt':
        generate_jwt_secret()
        return
    
    print("🚀 EcoTrack Ghana - Render Deployment Helper")
    print("=" * 50)
    
    # Check local configuration
    if not check_environment_config():
        print("\n❌ Please fix local configuration first!")
        return
    
    # Show Render setup instructions
    display_render_setup_instructions()
    
    # Generate JWT secret
    print("\n" + "="*50)
    generate_jwt_secret()
    
    # Show deployment status check
    check_deployment_status()
    
    # Show migration commands
    show_migration_commands()
    
    print("\n✅ Setup Instructions Complete!")
    print("📞 If you need help, check the logs and RENDER_SETUP.md")

if __name__ == "__main__":
    main()
