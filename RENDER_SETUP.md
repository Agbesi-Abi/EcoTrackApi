# Render Environment Variables Setup for EcoTrack Ghana

## 🚀 Setting Up PostgreSQL on Render

Your application is using SQLite because the PostgreSQL environment variables aren't configured on Render. Here's how to fix it:

### Step 1: Access Render Dashboard

1. Go to [render.com](https://render.com) and log in
2. Find your EcoTrack API service
3. Click on your service name

### Step 2: Configure Environment Variables

In your Render dashboard, go to **Environment** tab and add these variables:

#### Required PostgreSQL Variables:

```bash
# Main Database Configuration
DATABASE_URL=postgresql://ecotrack_d3gm_user:Q6tG9Y5zLJ1h9aihzBomjnOPilYC7HH0@dpg-d18o2oggjchc739cotbg-a.oregon-postgres.render.com/ecotrack_d3gm

# Environment Settings
ENVIRONMENT=production
DEBUG=False
ENABLE_DOCS=true
ENABLE_ADMIN=true

# Server Configuration
HOST=0.0.0.0
PORT=8000
PROJECT_VERSION=1.0.0

# JWT Configuration (IMPORTANT: Change these!)
JWT_SECRET_KEY=your-super-secure-production-jwt-secret-key-256-characters-long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Pool Configuration
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# File Upload Configuration
MAX_FILE_SIZE=5242880
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
UPLOAD_DIR=uploads

# CORS Configuration
ALLOWED_ORIGINS=https://ecotrack-online.onrender.com/api/v1,https://ecotrack-ghana.com/api/v1,http://localhost:3000,http://localhost:8081

# Security Headers
SECURE_COOKIES=True
HTTPS_ONLY=True

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=WARNING
LOG_FILE=logs/ecotrack_api.log

# Ghana Regions Configuration
DEFAULT_REGION=Greater Accra
SUPPORTED_REGIONS=["Greater Accra", "Ashanti", "Central", "Eastern", "Northern", "Upper East", "Upper West", "Volta", "Western", "Brong Ahafo", "Western North", "Ahafo", "Bono East", "Oti", "North East", "Savannah"]

# Monitoring & Health Checks
ENABLE_METRICS=True
HEALTH_CHECK_INTERVAL=60
```

### Step 3: Deploy and Verify

1. After adding the environment variables, **redeploy** your service
2. Check the logs to confirm PostgreSQL is being used:
   - Should see: `🗄️  Using PostgreSQL database`
   - Should NOT see: `🗄️  Using SQLite database (fallback)`

### Step 4: Initialize Database

After deployment with PostgreSQL, run the migrations:

```bash
# You can create a script or use the Render console
python migrate.py upgrade
python migrate.py seed
```

## 🔧 Alternative: Deploy Script

You can also set these via Render's API or create a `render.yaml` file:

```yaml
services:
  - type: web
    name: ecotrack-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: DATABASE_URL
        value: postgresql://ecotrack_d3gm_user:Q6tG9Y5zLJ1h9aihzBomjnOPilYC7HH0@dpg-d18o2oggjchc739cotbg-a.oregon-postgres.render.com/ecotrack_d3gm
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: False
      # ... add all other variables
```

## 🚨 Security Note

**IMPORTANT**: Change the JWT_SECRET_KEY to a secure random string before production use!

```bash
# Generate a secure key:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## ✅ Verification

After setting up, your logs should show:
```
🗄️  Using PostgreSQL database
🔗 Database URL found: postgresql://ecotrack_d3gm_user:***...
```

Instead of:
```
🗄️  Using SQLite database (fallback)
```

## 📞 Support

If you need help:
1. Check Render logs for error messages
2. Verify environment variables are set correctly
3. Test database connection: `python migrate.py check-db`
