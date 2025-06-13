# EcoTrack Ghana API - Production Deployment Guide

## 🚀 Quick Deployment

### 1. **Prerequisites**
- Docker & Docker Compose installed
- Domain name configured
- SSL certificates (optional but recommended)

### 2. **Environment Setup**
```bash
# Copy production environment template
cp .env.production .env

# Edit with your production values
nano .env
```

**Required Changes:**
- `JWT_SECRET_KEY`: Generate a strong 256-character secret
- `DATABASE_URL`: Configure PostgreSQL connection
- `ALLOWED_ORIGINS`: Set your actual domain URLs
- `SMTP_*`: Configure email settings

### 3. **Deploy with Docker Compose**
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

Or manually:
```bash
docker-compose -f docker-compose.production.yml up -d
```

### 4. **SSL Configuration (Recommended)**
```bash
# Place your SSL certificates
mkdir ssl
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
```

## 🔧 Manual Deployment Options

### Option 1: Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 2: Heroku
```bash
# Install Heroku CLI
# Create Heroku app
heroku create ecotrack-ghana-api

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set JWT_SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-postgres-url

# Deploy
git push heroku main
```

### Option 3: DigitalOcean Droplet
```bash
# Create droplet and SSH in
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone your-repo
cd EcoTrackAPI
./deploy.sh
```

### Option 4: AWS EC2
```bash
# Launch EC2 instance
# Install Docker
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start

# Deploy application
# Configure security groups for port 8000
```

## 🔒 Security Checklist

### Environment Variables
- [ ] Change `JWT_SECRET_KEY` to a strong secret
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set proper `ALLOWED_ORIGINS`
- [ ] Configure strong database credentials

### SSL/TLS
- [ ] Install SSL certificate
- [ ] Configure HTTPS redirect
- [ ] Use secure headers

### Database Security
- [ ] Use strong passwords
- [ ] Enable connection encryption
- [ ] Restrict database access
- [ ] Enable backup encryption

### API Security
- [ ] Disable debug mode in production
- [ ] Hide API documentation
- [ ] Enable rate limiting
- [ ] Monitor for suspicious activity

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check API health
curl https://your-domain.com/health

# Check service status
docker-compose -f docker-compose.production.yml ps
```

### Logs
```bash
# View API logs
docker-compose -f docker-compose.production.yml logs -f api

# View database logs
docker-compose -f docker-compose.production.yml logs -f db
```

### Backups
```bash
# Database backup
docker-compose -f docker-compose.production.yml exec db pg_dump -U ecotrack ecotrack_ghana > backup.sql

# Restore database
docker-compose -f docker-compose.production.yml exec -T db psql -U ecotrack ecotrack_ghana < backup.sql
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d
```

## 🌐 Domain Configuration

### DNS Records
```
A     @              YOUR_SERVER_IP
A     www            YOUR_SERVER_IP
A     api            YOUR_SERVER_IP
```

### Nginx Configuration
Update `nginx.conf` with your domain:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

## 📈 Performance Optimization

### Database Optimization
- Use connection pooling
- Add database indexes
- Regular VACUUM and ANALYZE
- Monitor query performance

### API Optimization
- Enable response caching
- Use CDN for static files
- Monitor response times
- Optimize database queries

### Infrastructure
- Use load balancer for high traffic
- Auto-scaling groups
- Monitor resource usage
- Set up alerts

## 🚨 Troubleshooting

### Common Issues

**API won't start:**
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs api

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Port already in use
```

**Database connection errors:**
```bash
# Check database status
docker-compose -f docker-compose.production.yml ps db

# Reset database
docker-compose -f docker-compose.production.yml down
docker volume rm ecotrackapi_postgres_data
docker-compose -f docker-compose.production.yml up -d
```

**SSL certificate issues:**
```bash
# Verify certificate files
ls -la ssl/
openssl x509 -in ssl/cert.pem -text -noout
```

### Support
- Check logs first: `docker-compose logs`
- Verify environment variables
- Test database connectivity
- Check firewall settings
- Monitor system resources

## 🎯 Production Readiness Checklist

- [ ] Environment variables configured
- [ ] Database properly set up
- [ ] SSL certificates installed
- [ ] Domain configured
- [ ] Firewall configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated

---

**EcoTrack Ghana API** - Ready for production deployment! 🌍🇬🇭
