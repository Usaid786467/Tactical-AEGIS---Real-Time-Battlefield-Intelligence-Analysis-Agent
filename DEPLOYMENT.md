# Tactical AEGIS Deployment Guide

Complete guide for deploying the Tactical AEGIS real-time battlefield intelligence system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Manual Deployment](#manual-deployment)
- [Environment Configuration](#environment-configuration)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git**

### Required API Keys
- **Google Gemini API Key** (Required): Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Mapbox Token** (Optional): For enhanced map features
- Other optional services: OpenWeather, NASA API, Sentinel Hub

### System Requirements
- **Memory**: 4GB minimum, 8GB recommended
- **CPU**: 2 cores minimum, 4 cores recommended
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Tactical-AEGIS.git
cd Tactical-AEGIS
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Minimum Required Configuration:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_PASSWORD=your_secure_database_password
SECRET_KEY=$(openssl rand -hex 32)
```

### 3. Start the System

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

### 5. Initial Setup

```bash
# Create database tables
docker-compose exec backend python -m alembic upgrade head

# (Optional) Create test data
docker-compose exec backend python scripts/seed_test_data.py
```

## Manual Deployment

### Backend Setup

1. **Install Python Dependencies**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize Database**

```bash
# PostgreSQL
createdb tactical_aegis
alembic upgrade head

# Or SQLite for development
export DATABASE_URL="sqlite:///./tactical_aegis.db"
```

4. **Run Backend**

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install Node Dependencies**

```bash
cd frontend
npm install
```

2. **Configure API Endpoint**

```bash
# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
echo "VITE_WS_URL=ws://localhost:8000" >> .env
```

3. **Build and Serve**

```bash
# Development
npm run dev

# Production build
npm run build
npm run preview
```

## Environment Configuration

### Core Settings

```env
# Database
DATABASE_URL=postgresql://aegis:password@localhost:5432/tactical_aegis

# AI Service
GEMINI_API_KEY=your_api_key_here

# Security
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (comma-separated origins)
CORS_ORIGINS='["http://localhost:3000","http://localhost:80"]'
```

### Optional Services

```env
# Map Services
MAPBOX_ACCESS_TOKEN=your_mapbox_token
OPENSTREETMAP_API_KEY=your_osm_key

# Weather & Satellite
OPENWEATHER_API_KEY=your_openweather_key
NASA_API_KEY=your_nasa_key
SENTINEL_HUB_API_KEY=your_sentinel_key

# Redis Cache
REDIS_URL=redis://localhost:6379
USE_REDIS=true
```

## Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Generate secure SECRET_KEY
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable application logging
- [ ] Configure rate limiting
- [ ] Review CORS origins
- [ ] Disable DEBUG mode
- [ ] Set up monitoring and alerts

### SSL/HTTPS Setup

#### Using Let's Encrypt with nginx

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal (add to crontab)
0 0 * * * certbot renew --quiet
```

#### Update docker-compose.yml for HTTPS

```yaml
frontend:
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx-ssl.conf:/etc/nginx/conf.d/default.conf
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Database Backup

```bash
# Automated daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/tactical-aegis"

mkdir -p $BACKUP_DIR

docker-compose exec -T postgres pg_dump -U aegis tactical_aegis \
  | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

### Monitoring Setup

```yaml
# Add to docker-compose.yml

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your_password
```

### Scaling

```bash
# Scale backend workers
docker-compose up -d --scale backend=3

# Use nginx for load balancing
# Update nginx.conf:
upstream backend {
    server backend:8000;
    server backend:8001;
    server backend:8002;
}
```

## Docker Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Execute commands in container
docker-compose exec backend python manage.py shell
```

### Database Management

```bash
# Create database backup
docker-compose exec postgres pg_dump -U aegis tactical_aegis > backup.sql

# Restore database
docker-compose exec -T postgres psql -U aegis tactical_aegis < backup.sql

# Reset database
docker-compose down -v  # Removes volumes
docker-compose up -d
```

### Maintenance

```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up old images
docker system prune -a

# View resource usage
docker stats
```

## Troubleshooting

### Backend Issues

**Problem**: Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common fixes:
# 1. Check GEMINI_API_KEY is set
# 2. Verify database connection
# 3. Ensure ports not in use
sudo netstat -tulpn | grep 8000
```

**Problem**: Database connection errors
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U aegis -d tactical_aegis

# Reset database
docker-compose down postgres
docker volume rm tactical-aegis_postgres_data
docker-compose up -d postgres
```

### Frontend Issues

**Problem**: API connection errors
```bash
# Check backend is accessible
curl http://localhost:8000/health

# Verify CORS settings in backend
# Update CORS_ORIGINS in .env if needed
```

**Problem**: Build failures
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install
npm run build
```

### WebSocket Issues

**Problem**: Real-time updates not working
```bash
# Test WebSocket connection
wscat -c ws://localhost:8000/ws/tactical

# Check nginx WebSocket proxy (if using)
# Ensure these headers are set:
# Upgrade $http_upgrade
# Connection "upgrade"
```

### Performance Issues

```bash
# Monitor resource usage
docker stats

# Check logs for errors
docker-compose logs --tail=100

# Increase worker count
# Edit docker-compose.yml:
# CMD ["uvicorn", "app.main:app", "--workers", "8"]
```

### API Rate Limiting

If experiencing API rate limits:
```env
# Adjust in .env
MAX_CONCURRENT_ANALYSES=10  # Increase if needed
GEMINI_API_RATE_LIMIT=60    # Requests per minute
```

## Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost/health

# Database health
docker-compose exec postgres pg_isready -U aegis

# Redis health
docker-compose exec redis redis-cli ping
```

## Support

For issues and questions:
- **Documentation**: [README.md](README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: [Report a bug](https://github.com/yourusername/Tactical-AEGIS/issues)

## License

See [LICENSE](LICENSE) file for details.
