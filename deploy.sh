#!/bin/bash
# EcoTrack Ghana API Deployment Script

set -e

echo "🌍 EcoTrack Ghana API - Production Deployment"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create production environment file if it doesn't exist
if [ ! -f .env.production ]; then
    echo "📝 Creating production environment file..."
    cp .env.production .env
    echo "⚠️  Please edit .env file with your production values before continuing!"
    echo "   - JWT_SECRET_KEY: Use a strong 256-character secret"
    echo "   - DATABASE_URL: Configure your PostgreSQL connection"
    echo "   - ALLOWED_ORIGINS: Set your actual domain URLs"
    read -p "Press Enter when you've configured the .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs ssl uploads

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if API is running
echo "🔍 Checking API health..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is running successfully!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts - waiting for API..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ API failed to start. Check logs with: docker-compose -f docker-compose.production.yml logs api"
    exit 1
fi

# Show running services
echo ""
echo "🎉 EcoTrack Ghana API deployed successfully!"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "🔗 Access Points:"
echo "   API: http://localhost:8000"
echo "   Health Check: http://localhost:8000/health"
echo "   Database: PostgreSQL on localhost:5432"

echo ""
echo "📋 Next Steps:"
echo "   1. Configure SSL certificates in ./ssl/ directory"
echo "   2. Update DNS to point to your server"
echo "   3. Configure your domain in ALLOWED_ORIGINS"
echo "   4. Set up monitoring and backups"
echo "   5. Test all endpoints"

echo ""
echo "📝 Useful Commands:"
echo "   View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.production.yml down"
echo "   Restart API: docker-compose -f docker-compose.production.yml restart api"

echo ""
echo "Yɛ bɛyɛ yiye - We will make it better! 🇬🇭"
