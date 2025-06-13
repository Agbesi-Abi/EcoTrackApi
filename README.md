# EcoTrack Ghana API Backend

A comprehensive FastAPI backend service for the EcoTrack Ghana mobile application, providing authentication, activity tracking, challenges, and community features for environmental conservation in Ghana.

## 🌍 Features

- 🔐 **User Authentication & Authorization** - JWT-based auth with secure password hashing
- 🌱 **Activity Logging & Tracking** - Log environmental activities with points calculation
- 🏆 **Challenge Management System** - Create, join, and track progress in eco-challenges
- 👥 **Community Leaderboards** - Regional and global rankings with impact statistics
- 📊 **Environmental Impact Analytics** - Track CO2 savings, waste collected, trees planted
- 🎯 **Points & Rewards System** - Gamification with smart points calculation
- 📍 **Ghana-Focused Features** - All 16 regions, local context, regional competitions
- 📱 **Photo Upload Support** - Activity verification with image uploads
- 🔄 **Real-time Sync** - RESTful API for React Native app integration

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: SQLAlchemy with SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT tokens with bcrypt password hashing
- **File Upload**: Async file handling with aiofiles
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Testing**: pytest with async support

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or poetry

### Installation

1. **Clone and navigate to the project**:
```bash
cd EcoTrackAPI
```

2. **Create virtual environment**:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Start the development server**:
```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication
```
POST /api/v1/auth/register     - User registration
POST /api/v1/auth/login        - User login
POST /api/v1/auth/refresh      - Refresh JWT token
GET  /api/v1/auth/me           - Get current user profile
POST /api/v1/auth/logout       - Logout user
```

### Activities
```
GET    /api/v1/activities              - List activities (with filters)
POST   /api/v1/activities              - Log new activity
GET    /api/v1/activities/my           - Get current user's activities
GET    /api/v1/activities/{id}         - Get activity details
PUT    /api/v1/activities/{id}         - Update activity
DELETE /api/v1/activities/{id}         - Delete activity
POST   /api/v1/activities/upload-photo - Upload activity photo
GET    /api/v1/activities/stats/global - Get global activity statistics
```

### Challenges
```
GET    /api/v1/challenges                    - List available challenges
POST   /api/v1/challenges                    - Create new challenge
GET    /api/v1/challenges/my                 - Get user's joined challenges
GET    /api/v1/challenges/{id}               - Get challenge details
POST   /api/v1/challenges/{id}/join          - Join a challenge
POST   /api/v1/challenges/{id}/leave         - Leave a challenge
PUT    /api/v1/challenges/{id}/progress      - Update challenge progress
GET    /api/v1/challenges/{id}/participants  - Get challenge participants
```

### Community
```
GET /api/v1/community/leaderboard            - Get community leaderboard
GET /api/v1/community/leaderboard/regional   - Get regional leaderboard
GET /api/v1/community/stats/global           - Get global community stats
GET /api/v1/community/regions/{name}/stats   - Get specific region stats
GET /api/v1/community/impact/recent          - Get recent impactful activities
GET /api/v1/community/achievements/top       - Get top community achievements
```

### User Profile
```
GET    /api/v1/users/{id}            - Get user profile
PUT    /api/v1/users/{id}            - Update user profile
POST   /api/v1/users/{id}/avatar     - Upload user avatar
GET    /api/v1/users/{id}/impact     - Get user impact statistics
GET    /api/v1/users/{id}/activities - Get user's activities
DELETE /api/v1/users/{id}            - Delete user account
```

### Ghana Data
```
GET /api/v1/ghana/regions - Get all Ghana regions with capitals
```

## 🗄 Database Schema

### Users Table
```sql
- id (Primary Key)
- email (Unique)
- name
- hashed_password
- location, region
- total_points, weekly_points, rank
- avatar_url
- is_active, is_verified
- trash_collected, trees_planted, co2_saved
- created_at, updated_at
```

### Activities Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- type (trash/trees/mobility/water/energy)
- title, description
- points, location, region
- photos (JSON), verified
- impact_data (JSON)
- created_at
```

### Challenges Table
```sql
- id (Primary Key)
- title, description, category
- duration, points, difficulty
- is_active
- start_date, end_date, created_at
```

### Challenge Participants (Association Table)
```sql
- user_id, challenge_id (Composite Key)
- joined_at, progress, completed
```

### Regions Table
```sql
- id (Primary Key)
- name, capital, code
- population, area_km2
- Environmental stats (users, activities, points, impact)
```

## 🇬🇭 Ghana-Focused Features

### Regional Coverage
- **16 Regions**: Complete coverage of all Ghana regions
- **Regional Competitions**: Leaderboards by region
- **Local Context**: Ghana-specific environmental challenges

### Cultural Integration
- **Local Proverbs**: Akan wisdom integrated into community features
- **Regional Capitals**: Accurate mapping of all regional capitals
- **Population Data**: Real Ghana census data for regional statistics

### Environmental Focus
- **Local Challenges**: Waste management, deforestation, sustainable transport
- **Impact Metrics**: CO2 calculations based on Ghana's energy grid
- **Community NGOs**: Integration points for local environmental organizations

## 🔧 Development

### Environment Variables
Create a `.env` file based on `.env.example`:

```env
DATABASE_URL=sqlite:///./ecotrack_ghana.db
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_FILE_SIZE=5242880
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081
```

### Points Calculation System

Activities earn points based on:
- **Base Points**: Each activity type has base points (trash: 25, trees: 50, etc.)
- **Photo Bonus**: +5 points for photo documentation
- **Location Bonus**: +3 points for sharing location
- **Impact Bonus**: Additional points based on quantity (bags collected, trees planted, etc.)
- **Maximum Cap**: 200 points per activity to prevent gaming

### Impact Statistics

Environmental impact calculated as:
- **Trash Collection**: 1 bag = 2kg waste, 0.5kg CO2 saved
- **Tree Planting**: 1 tree = 21.77kg CO2 absorbed per year
- **Sustainable Mobility**: CO2 savings vs. driving alone
- **Water Conservation**: Indirect CO2 savings from reduced treatment
- **Energy Conservation**: Ghana grid factor (0.45 kg CO2/kWh)

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

### Database Migrations

```bash
# Initialize Alembic (if needed)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🚀 Production Deployment

### Using Docker

1. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Docker Compose**:
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/ecotrack
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ecotrack
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Environment Configuration

For production, update your `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost/ecotrack_ghana
JWT_SECRET_KEY=super-secure-secret-key-256-bits
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### Security Considerations

- ✅ JWT token expiration (30 min access, 7 days refresh)
- ✅ Password hashing with bcrypt
- ✅ Input validation with Pydantic
- ✅ SQL injection protection with SQLAlchemy
- ✅ CORS configuration
- ✅ File upload size limits
- ✅ User data privacy (email only shown to profile owner)

## 📱 React Native Integration

### API Base URL Configuration

In your React Native app, set the API base URL:

```typescript
// For development
const API_BASE_URL = 'http://localhost:8000/api/v1';

// For production
const API_BASE_URL = 'https://your-api-domain.com/api/v1';
```

### Authentication Integration

```typescript
// Login
const response = await fetch(`${API_BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: `username=${email}&password=${password}`
});

// Authenticated requests
const response = await fetch(`${API_BASE_URL}/activities`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

### Activity Logging Integration

```typescript
const logActivity = async (activityData) => {
  const response = await fetch(`${API_BASE_URL}/activities`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(activityData)
  });
  return response.json();
};
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to all functions and classes
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **API Documentation**: http://localhost:8000/docs
- **Issues**: Create an issue on GitHub
- **Email**: support@ecotrack-ghana.com

## 🙏 Acknowledgments

- **Ghana Environmental Protection Agency** - For environmental data and guidelines
- **Let's Do It Ghana** - Community cleanup inspiration
- **Ghana Youth Environmental Movement (GAYO)** - Youth engagement model
- **FastAPI Community** - Excellent framework and documentation

---

**Yɛ bɛyɛ yiye** - We will make it better 🇬🇭

Built with ❤️ for Ghana's sustainable future
#   E c o T r a c k A p i  
 