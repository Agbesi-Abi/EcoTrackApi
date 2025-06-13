# 🚀 EcoTrack Ghana API - Multi-Platform Deployment Guide

## 🐛 **Issue Fixed**: Missing Email Validator

**Problem**: `ImportError: email-validator is not installed`  
**Solution**: ✅ Added `pydantic[email]` and `email-validator` to requirements

---

## 🌐 **Platform-Specific Deployment**

### 1. **Render (Recommended - Easiest)**

#### **Quick Deploy:**
1. **Connect GitHub repo to Render**
2. **Use these settings:**
   - **Build Command**: `pip install -r requirements.production.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: `production`

#### **Environment Variables:**
```env
ENVIRONMENT=production
JWT_SECRET_KEY=your-super-secure-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/ecotrack_ghana
ALLOWED_ORIGINS=https://your-domain.com
```

#### **Auto-Deploy with render.yaml:**
```bash
# Just push render.yaml to your repo and Render will auto-configure
git add render.yaml
git commit -m "Add Render configuration"
git push
```

---

### 2. **Railway**

#### **Deploy Steps:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### **Configuration:**
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Build Command**: `pip install -r requirements.production.txt`

---

### 3. **Heroku**

#### **Deploy Steps:**
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create ecotrack-ghana-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set JWT_SECRET_KEY=your-secret-key

# Deploy
git push heroku main
```

#### **Create Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

### 4. **DigitalOcean App Platform**

#### **Deploy with Docker:**
```yaml
# .do/app.yaml
name: ecotrack-ghana-api
services:
- name: api
  source_dir: /
  github:
    repo: your-username/your-repo
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: ENVIRONMENT
    value: production
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
databases:
- name: db
  engine: PG
  version: "15"
```

---

### 5. **Docker + VPS (Advanced)**

#### **Deploy with Docker Compose:**
```bash
# On your VPS
git clone your-repo
cd EcoTrackAPI

# Configure environment
cp .env.production .env
nano .env  # Edit with your values

# Deploy
docker-compose -f docker-compose.production.yml up -d
```

---

## 🔧 **Fixed Files Summary**

### ✅ **Updated Requirements:**
- **`requirements.txt`**: Added `pydantic[email]` and `email-validator`
- **`requirements.production.txt`**: Added all missing dependencies

### ✅ **New Deployment Files:**
- **`Dockerfile.render`**: Render-optimized Docker configuration
- **`render.yaml`**: One-click Render deployment
- **`start.sh`**: Production start script

### ✅ **Platform Support:**
- ✅ **Render**: Auto-deploy with render.yaml
- ✅ **Railway**: CLI deployment ready
- ✅ **Heroku**: Procfile and config ready
- ✅ **DigitalOcean**: App platform configuration
- ✅ **Docker**: Production-ready containers

---

## 🚀 **Quick Start for Each Platform**

### **Option 1: Render (Easiest)**
1. Push your code to GitHub
2. Connect repo to Render
3. Render auto-detects configuration from `render.yaml`
4. ✅ Done!

### **Option 2: Railway**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### **Option 3: Heroku**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
git push heroku main
```

---

## 🔍 **Testing Your Deployment**

### **Health Check URLs:**
- **Health**: `https://your-app.onrender.com/health`
- **API**: `https://your-app.onrender.com/api/v1/community/stats/global`
- **Root**: `https://your-app.onrender.com/`

### **Expected Response:**
```json
{
  "status": "healthy",
  "service": "EcoTrack Ghana API",
  "environment": "production",
  "version": "1.0.0"
}
```

---

## 🔒 **Security Checklist**

- ✅ **Strong JWT Secret**: Use 256-character random key
- ✅ **Database Security**: Strong passwords, SSL enabled
- ✅ **CORS**: Only allow your frontend domains
- ✅ **Environment Variables**: Never commit secrets
- ✅ **HTTPS Only**: Enable SSL on your domain

---

## 📱 **Frontend Configuration**

Update your React Native app's API URL:

```typescript
// services/apiService.ts
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1'
  : 'https://your-deployed-api.onrender.com/api/v1';
```

---

## 🎯 **Next Steps**

1. **Choose your platform** (Render recommended)
2. **Deploy API** using the guide above
3. **Test endpoints** to ensure everything works
4. **Update frontend** with production API URL
5. **Deploy mobile app** to app stores

---

## 🆘 **Troubleshooting**

### **Common Issues:**
- **Port binding**: Ensure using `$PORT` environment variable
- **Dependencies**: Make sure all requirements are installed
- **Database**: Check DATABASE_URL connection string
- **CORS**: Verify ALLOWED_ORIGINS includes your frontend

### **Quick Fixes:**
```bash
# Check logs
docker logs container-name

# Restart service
docker-compose restart api

# Test locally
uvicorn main:app --reload
```

---

## 🌍 **Success!**

Your EcoTrack Ghana API is now deployment-ready with:

✅ **Fixed Dependencies** - No more email-validator errors  
✅ **Multi-Platform Support** - Deploy anywhere  
✅ **Production Configuration** - Secure and optimized  
✅ **Easy Deployment** - One-command deploy options  

**Choose your platform and deploy! 🚀🇬🇭**

**Yɛ bɛyɛ yiye** - We will make it better! 🌱
