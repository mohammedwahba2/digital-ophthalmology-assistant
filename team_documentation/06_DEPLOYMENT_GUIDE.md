# Deployment & Setup Guide

## 🚀 Overview

This document provides comprehensive instructions for setting up, running, and deploying the Digital Ophthalmology Assistant project in development and production environments.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| pip | Latest | Python package manager |
| Node.js | 18+ (optional) | Frontend tooling |
| Git | Latest | Version control |
| Docker | 20+ (optional) | Containerization |

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Storage | 10 GB | 20+ GB |
| GPU | Not required | NVIDIA GPU for faster AI inference |

---

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/mohammedwahba2/digital-ophthalmology-assistant.git
cd digital-ophthalmology-assistant
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional)
nano .env

# Initialize database (happens automatically on first run)
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend should now be running at:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs

### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Start simple HTTP server
python3 -m http.server 8080
```

**Frontend should now be running at:** http://localhost:8080/pages/index.html

### 4. Configure API URL (if needed)

If your backend is not on the default URL:

```javascript
// In browser console on frontend page:
localStorage.setItem("doa-api-base", "http://your-backend-url:8000");
location.reload();
```

### 5. Verify Setup

1. Open http://localhost:8080/pages/index.html in your browser
2. Navigate to the "Diagnose" page
3. Upload a test eye image
4. Verify AI prediction works

---

## Production Deployment

### Option 1: Direct Deployment

#### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export HOST=0.0.0.0
export PORT=8000
export DATABASE_URL=postgresql://user:password@localhost:5432/ophthalmology
export DEBUG=false

# Run with production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend

Deploy the `frontend/` directory to any static web host:

- **Netlify**: Drag and drop the frontend folder
- **Vercel**: Connect GitHub repository
- **AWS S3**: Upload to S3 bucket with static hosting
- **Nginx**: Serve with Nginx

**Nginx Configuration Example:**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/frontend;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /predict {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### Option 2: Cloud Platform Deployment

#### Heroku

**1. Create Heroku App**

```bash
heroku create ophthalmology-assistant
```

**2. Backend (Heroku)**

Create `Procfile` in backend directory:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Create `runtime.txt`:
```
python-3.11.0
```

Deploy:
```bash
cd backend
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a ophthalmology-assistant
git push heroku main
```

**3. Frontend (Netlify)**

Connect your GitHub repository to Netlify and set build settings:
- Build command: (none)
- Publish directory: `frontend`

---

#### AWS Deployment

**1. Backend (EC2 or Elastic Beanstalk)**

```bash
# EC2 Setup
sudo yum update
sudo yum install python3 python3-pip git

# Clone and setup
git clone <repository-url>
cd digital-ophthalmology-assistant/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

**2. Frontend (S3 + CloudFront)**

```bash
# Upload to S3
aws s3 sync frontend/ s3://your-bucket-name/

# Enable static website hosting
aws s3 website s3://your-bucket-name/ --index-document index.html

# Create CloudFront distribution for HTTPS
```

---

## Docker Deployment

### 1. Build Docker Images

**Backend Dockerfile** (already exists in `backend/Dockerfile`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build Backend Image:**

```bash
cd backend
docker build -t ophthalmology-backend .
```

**Frontend Dockerfile** (create `frontend/Dockerfile`):

```dockerfile
FROM nginx:alpine

COPY . /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Build Frontend Image:**

```bash
cd frontend
docker build -t ophthalmology-frontend .
```

### 2. Docker Compose

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./predictions.db
      - DEBUG=false
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/predictions.db:/app/predictions.db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**Run with Docker Compose:**

```bash
docker-compose up -d
```

**Access:**
- Frontend: http://localhost
- Backend API: http://localhost:8000

---

## Environment Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Application Settings
DEBUG=false
APP_NAME="Digital Ophthalmology Assistant"
APP_VERSION=1.0.0

# Database Configuration
# SQLite (Development)
DATABASE_URL=sqlite:///./predictions.db

# PostgreSQL (Production)
# DATABASE_URL=postgresql://username:password@localhost:5432/ophthalmology

# MySQL (Alternative)
# DATABASE_URL=mysql://username:password@localhost:3306/ophthalmology

# CORS Settings
CORS_ORIGINS=["https://your-domain.com", "https://www.your-domain.com"]

# File Upload Settings
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=10

# Model Configuration (Optional - defaults to HuggingFace Hub)
# MODEL_PATH=models/model.keras
```

### Security Considerations

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use strong database passwords** - Generate secure random passwords
3. **Enable HTTPS** - Use SSL certificates (Let's Encrypt)
4. **Set proper CORS origins** - Restrict to your domain
5. **Limit file upload size** - Prevent DoS attacks
6. **Use environment variables** - Don't hardcode secrets

---

## Troubleshooting

### Issue 1: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

### Issue 2: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'tensorflow'`

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 3: Database Locked

**Error:** `database is locked`

**Solution:**
```bash
# For SQLite, ensure only one process accesses the database
# Kill any stale processes
pkill -f uvicorn

# Or switch to PostgreSQL for production
```

### Issue 4: Model Not Found

**Error:** `FileNotFoundError: Model file not found`

**Solution:**
1. Ensure internet connection for HuggingFace Hub download
2. Or manually place model at `backend/models/model.keras`
3. Check HuggingFace token if using private model

### Issue 5: CORS Errors

**Error:** `CORS policy blocked`

**Solution:**
```env
# In .env file
CORS_ORIGINS=["*"]  # For development only

# For production, specify exact origins
CORS_ORIGINS=["https://your-domain.com"]
```

### Issue 6: Slow Inference

**Symptoms:** Predictions take >10 seconds

**Solutions:**
1. Use GPU acceleration (CUDA-enabled TensorFlow)
2. Reduce image resolution before upload
3. Increase server resources (CPU/RAM)
4. Enable model warmup on startup

---

## Monitoring & Logging

### Application Logs

```bash
# View logs (when running with uvicorn)
# Logs appear in console

# Save logs to file
uvicorn app.main:app --log-config logging.conf
```

### Health Check

```bash
# Check if API is healthy
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### Database Backup

```bash
# SQLite backup
cp predictions.db predictions_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump -U username ophthalmology > backup_$(date +%Y%m%d).sql

# Restore PostgreSQL
psql -U username ophthalmology < backup_$(date +%Y%m%d).sql
```

---

## Performance Optimization

### 1. Enable Caching

```python
# Use Redis for caching (optional)
# Add to requirements.txt: redis, fastapi-cache2

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

### 2. Database Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);
CREATE INDEX idx_predictions_prediction ON predictions(prediction);
CREATE INDEX idx_library_items_disease_id ON library_items(disease_id);
```

### 3. CDN for Static Assets

Deploy frontend assets to CDN for faster loading:
- CloudFlare
- AWS CloudFront
- Azure CDN

---

## Checklist for Production

- [ ] Environment variables configured
- [ ] Database set up (PostgreSQL recommended)
- [ ] HTTPS enabled with SSL certificate
- [ ] CORS origins restricted to production domain
- [ ] Debug mode disabled
- [ ] Error logging configured
- [ ] Database backups scheduled
- [ ] Monitoring set up (uptime, errors)
- [ ] Rate limiting enabled (prevent abuse)
- [ ] File upload limits configured
- [ ] Model warmed up on startup
- [ ] Load testing completed

---

*For deployment issues, contact the DevOps team lead.*

*Last Updated: [Current Date]*  
*Document Version: 1.0*