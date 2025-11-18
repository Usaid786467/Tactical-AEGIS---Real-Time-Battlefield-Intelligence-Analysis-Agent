# Tactical AEGIS - Real-Time Battlefield Intelligence & Analysis System

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178c6.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://www.docker.com/)

An AI-powered command and control system that fuses multiple intelligence sources (satellite imagery, drone feeds, sensor data, radio communications) into a unified tactical picture with real-time threat analysis and predictive modeling.

## 🎯 Core Capabilities

### 1. **Multi-Source Intelligence Fusion**
- **Image Analysis**: AI-powered threat detection from satellite and drone imagery
- **Audio Processing**: Voice-to-text debriefing with automatic SITREP generation
- **Sensor Integration**: Real-time data fusion from ground sensors
- **Communication Analysis**: NLP-based analysis of radio traffic

### 2. **Predictive Threat Modeling**
- **Pattern Recognition**: Analyze historical threat data to identify patterns
- **Geographic Clustering**: Detect threat concentration zones
- **Temporal Analysis**: Predict timing of potential hostile actions
- **AI-Enhanced Predictions**: Gemini-powered reasoning for threat forecasting

### 3. **Automated SITREP Generation**
- **Voice Debriefing**: Convert field reports to structured SITREPs
- **Entity Extraction**: Automatically identify units, locations, equipment
- **Military Format**: Generate reports in standard SITREP format
- **Priority Classification**: AI-based priority assignment (Routine → Flash)

### 4. **Friendly Force Tracking**
- **Real-Time GPS Tracking**: Monitor all friendly unit positions
- **Blue-on-Blue Prevention**: 3-tier proximity alerts (500m/1km/2km)
- **Deployment Optimization**: Calculate optimal unit deployment routes
- **Status Monitoring**: Track unit readiness (Green/Amber/Red/Black)

### 5. **Interactive Tactical Map**
- **Live Updates**: WebSocket-powered real-time position updates
- **Threat Visualization**: Color-coded threat markers (Low → Critical)
- **Unit Tracking**: Friendly force markers with status indicators
- **Layer Controls**: Toggle threat/unit/sensor layers independently

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Tactical-AEGIS.git
cd Tactical-AEGIS

# 2. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Start the system
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000/docs
# WebSocket: ws://localhost:8000/ws
```

### First Run

```bash
# Initialize database
docker-compose exec backend alembic upgrade head

# (Optional) Load test data
docker-compose exec backend python scripts/seed_test_data.py
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  Dashboard │ Map │ Threats │ SITREP │ Tracking              │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API / WebSocket
┌─────────────────────┴───────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Threat API   │  │ SITREP API   │  │ Tracking API │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│  ┌──────┴──────────────────┴──────────────────┴───────┐     │
│  │              Core Services Layer                     │     │
│  │  • Gemini AI  • Image Analysis  • GPS Service      │     │
│  │  • NLP Engine • Data Fusion     • Threat Predictor │     │
│  └───────────────────────┬──────────────────────────────┘     │
└────────────────────────┬─┴────────────────────────────────────┘
                         │
┌────────────────────────┴─────────────────────────────────────┐
│              Data Layer                                       │
│  PostgreSQL │ Redis Cache │ File Storage                     │
└───────────────────────────────────────────────────────────────┘
```

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104 (Python 3.11)
- **AI/ML**: Google Gemini 1.5 Pro API
- **Database**: PostgreSQL 16 + SQLAlchemy ORM
- **Cache**: Redis 7
- **Image Processing**: OpenCV, Pillow
- **Audio**: Librosa, Soundfile
- **Real-Time**: WebSockets

### Frontend
- **Framework**: React 18.2 + TypeScript 5.3
- **Build Tool**: Vite 5.0
- **Styling**: Tailwind CSS 3.3
- **Maps**: Mapbox GL JS 3.0
- **State**: TanStack React Query 5.12
- **Icons**: Lucide React
- **HTTP Client**: Axios

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (for frontend)
- **Process Manager**: Uvicorn (4 workers)
- **Database Migrations**: Alembic

## 📁 Project Structure

```
Tactical-AEGIS/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # REST API routes
│   │   │   ├── threat_analysis.py  (280 lines)
│   │   │   ├── sitrep.py           (245 lines)
│   │   │   ├── tracking.py         (290 lines)
│   │   │   ├── data_fusion.py      (180 lines)
│   │   │   └── websocket.py        (260 lines)
│   │   ├── services/       # Core business logic
│   │   │   ├── gemini_service.py   (380 lines)
│   │   │   ├── image_analysis.py   (350 lines)
│   │   │   ├── nlp_service.py      (320 lines)
│   │   │   ├── threat_predictor.py (380 lines)
│   │   │   ├── gps_service.py      (350 lines)
│   │   │   ├── audio_processor.py  (280 lines)
│   │   │   └── data_fusion.py      (420 lines)
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   └── main.py         # Application entry
│   ├── tests/              # Test suite
│   │   ├── test_threat_api.py
│   │   ├── test_tracking_api.py
│   │   └── test_sitrep_api.py
│   ├── scripts/            # Utility scripts
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/       # Main dashboard
│   │   │   ├── TacticalMap/     # Interactive map (400 lines)
│   │   │   ├── ThreatPanel/     # Threat management (650 lines)
│   │   │   ├── SitrepPanel/     # SITREP generator (750 lines)
│   │   │   └── TrackingPanel/   # Force tracking (850 lines)
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API & WebSocket clients
│   │   ├── types/          # TypeScript definitions
│   │   ├── pages/          # Route pages
│   │   ├── styles/         # Global styles
│   │   └── App.tsx         # Main app component
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml      # Multi-service orchestration
├── .env.example            # Environment template
├── DEPLOYMENT.md           # Deployment guide
└── README.md              # This file
```

## 🔌 API Endpoints

### Threat Analysis
- `POST /api/threats/analyze/image` - Analyze tactical imagery
- `POST /api/threats/predict` - Generate threat predictions
- `GET /api/threats` - List all threats (with filters)
- `POST /api/threats` - Create threat manually
- `PUT /api/threats/{id}` - Update threat
- `DELETE /api/threats/{id}` - Delete threat
- `GET /api/threats/stats` - Get threat statistics

### SITREP Management
- `POST /api/sitrep/generate` - AI-powered SITREP generation
- `POST /api/sitrep/voice-debrief` - Voice-to-SITREP conversion
- `GET /api/sitrep` - List all SITREPs
- `POST /api/sitrep` - Create SITREP
- `PUT /api/sitrep/{id}` - Update SITREP
- `DELETE /api/sitrep/{id}` - Delete SITREP
- `GET /api/sitrep/stats` - Get SITREP statistics

### Force Tracking
- `POST /api/tracking/units` - Register new unit
- `GET /api/tracking/units` - List all units
- `GET /api/tracking/units/{unit_id}` - Get unit details
- `PUT /api/tracking/units/{unit_id}/position` - Update position
- `DELETE /api/tracking/units/{unit_id}` - Remove unit
- `POST /api/tracking/blue-on-blue` - Check blue-on-blue risks
- `GET /api/tracking/nearby` - Find nearby units
- `POST /api/tracking/optimize-deployment` - Optimize deployment

### Data Fusion
- `GET /api/fusion/tactical-picture` - Get complete tactical picture
- `POST /api/fusion/correlate` - Correlate multiple data sources
- `GET /api/fusion/analysis` - Get fusion analysis

### WebSocket Channels
- `ws://localhost:8000/ws/threats` - Threat updates
- `ws://localhost:8000/ws/tracking` - Unit position updates
- `ws://localhost:8000/ws/sitrep` - SITREP updates
- `ws://localhost:8000/ws/tactical` - Full tactical picture
- `ws://localhost:8000/ws/all` - All updates

## 🎨 Frontend Features

### Dashboard
- Real-time stats (threats, units, status)
- Recent threats list with color coding
- Friendly forces overview
- AI-powered situation assessment
- Connection status indicators

### Tactical Map
- Interactive Mapbox GL map
- Color-coded threat markers (green → red)
- Friendly unit markers with status
- Real-time position updates
- Layer controls and legend
- Detailed popups on click

### Threat Analysis Panel
- Searchable threat list with filters
- Threat level filtering (Low/Medium/High/Critical)
- Image upload and AI analysis
- Threat prediction interface
- Detailed threat information view

### SITREP Panel
- SITREP history with priority filters
- AI-powered SITREP generation
- Voice debriefing interface
- Standard military format display
- Export functionality

### Force Tracking Panel
- Unit list with status filters
- Position update interface
- Blue-on-blue proximity checker
- Unit details and mission info
- Personnel and equipment tracking

## 🔒 Security Features

- **Input Validation**: Pydantic models on all endpoints
- **SQL Injection Prevention**: SQLAlchemy ORM parameterization
- **XSS Protection**: React automatic escaping + sanitization
- **CORS Configuration**: Whitelist-based origin control
- **Environment Secrets**: API keys in environment variables
- **Authentication Ready**: JWT infrastructure included
- **Rate Limiting**: Configurable API rate limits

## 📈 Performance

- **Backend**: 4 Uvicorn workers for concurrent requests
- **Frontend**: Code-split React build (2MB gzipped)
- **WebSocket**: Automatic reconnection with exponential backoff
- **Database**: Connection pooling + Redis caching
- **Images**: Lazy loading + CDN-ready
- **API**: Async/await throughout

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest tests/ -v --cov=app

# Run frontend tests
cd frontend
npm test

# Integration tests
docker-compose exec backend pytest tests/integration/
```

## 📝 Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/tactical_aegis

# Optional
MAPBOX_ACCESS_TOKEN=your_mapbox_token
REDIS_URL=redis://localhost:6379
USE_REDIS=true

# Security
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
CORS_ORIGINS='["http://localhost:3000"]'
```

See `.env.example` for full configuration options.

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Complete deployment instructions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)
- **[Architecture Details](BACKEND_COMPLETE.md)** - Backend architecture
- **[Session Summary](SESSION_SUMMARY.md)** - Development history

## 🚢 Production Deployment

### SSL/HTTPS

```bash
# Using Let's Encrypt
sudo certbot --nginx -d yourdomain.com

# Update docker-compose.yml to mount certificates
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Scaling

```bash
# Scale backend workers
docker-compose up -d --scale backend=4

# Add load balancer
# Update nginx.conf with upstream configuration
```

### Monitoring

```bash
# Add Prometheus + Grafana
# See DEPLOYMENT.md for full monitoring setup
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify Gemini API key
echo $GEMINI_API_KEY

# Check database connection
docker-compose exec postgres psql -U aegis -d tactical_aegis
```

### WebSocket connection issues
```bash
# Test WebSocket
wscat -c ws://localhost:8000/ws/tactical

# Check nginx WebSocket proxy configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Frontend build errors
```bash
# Clear cache and rebuild
cd frontend
rm -rf node_modules package-lock.json dist
npm install
npm run build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for vision and NLP capabilities
- **FastAPI** for the excellent async Python framework
- **React** and **TypeScript** for robust frontend development
- **Mapbox GL** for interactive mapping
- All open-source contributors

## 📞 Support

- **Documentation**: See `DEPLOYMENT.md` and `BACKEND_COMPLETE.md`
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Tactical-AEGIS/issues)

## 🎯 Future Enhancements

- [ ] Machine learning model training for threat classification
- [ ] Multi-tenant support for coalition operations
- [ ] Mobile app for field commanders
- [ ] Offline mode with sync capabilities
- [ ] Advanced analytics dashboard
- [ ] Integration with additional satellite providers
- [ ] AR/VR visualization modes
- [ ] Automated after-action report generation

---

**Built with ❤️ for tactical intelligence professionals**

**Version**: 1.0.0
**Last Updated**: 2025-01-18
**Status**: Production Ready ✅
