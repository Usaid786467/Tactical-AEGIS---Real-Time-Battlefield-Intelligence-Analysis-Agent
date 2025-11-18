# Tactical AEGIS Backend

Real-Time Battlefield Intelligence & Analysis System - Backend API

## Features Implemented

### Core Services
- ✅ **Gemini AI Integration**: Vision and NLP analysis using Google Gemini API
- ✅ **Image Analysis**: Satellite and drone imagery threat detection
- ✅ **NLP Service**: Communication analysis and SITREP generation
- ✅ **Threat Prediction**: Pattern analysis and threat forecasting
- ✅ **GPS Tracking**: Friendly force tracking and blue-on-blue prevention
- ✅ **Data Fusion**: Multi-source intelligence fusion
- ✅ **Audio Processing**: Audio signature analysis (gunfire, explosions)

### Database Models
- ✅ Threat detection and tracking
- ✅ Situation reports (SITREP)
- ✅ Friendly force tracking
- ✅ Data source management
- ✅ Analysis job tracking

### Configuration
- ✅ Environment-based configuration
- ✅ Pydantic settings validation
- ✅ CORS support
- ✅ Logging configuration

## Setup

### Prerequisites
```bash
Python 3.10+
```

### Installation

1. Create virtual environment:
```bash
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/MacOS)
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running the Server

Development mode:
```bash
python -m app.main
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── api/                 # API routes
│   ├── services/            # Business logic services
│   │   ├── gemini_service.py
│   │   ├── image_analysis.py
│   │   ├── nlp_service.py
│   │   ├── threat_predictor.py
│   │   └── gps_service.py
│   ├── models/              # Pydantic models
│   ├── database/            # Database setup
│   └── utils/               # Utilities
│       ├── audio_processor.py
│       ├── data_fusion.py
│       └── validators.py
├── tests/                   # Test files
├── requirements.txt
├── .env                     # Environment variables (not in git)
└── README.md
```

## Environment Variables

Required:
- `GEMINI_API_KEY`: Google Gemini API key

Optional:
- `MAPBOX_ACCESS_TOKEN`: Mapbox API token
- `OPENWEATHER_API_KEY`: OpenWeather API key
- `DATABASE_URL`: Database connection string
- `CORS_ORIGINS`: Allowed CORS origins

## Services Overview

### Gemini Service (`gemini_service.py`)
- Image analysis for threat detection
- Text analysis for intelligence extraction
- Entity extraction from communications
- Automated SITREP generation

### Image Analysis (`image_analysis.py`)
- Tactical image preprocessing
- Threat detection from satellite/drone imagery
- Change detection between images
- Object classification (vehicles, personnel, weapons)

### NLP Service (`nlp_service.py`)
- Communication analysis
- SITREP generation from voice/text
- Entity extraction
- Priority assessment

### Threat Predictor (`threat_predictor.py`)
- Historical pattern analysis
- Geographic clustering
- Temporal pattern detection
- AI-enhanced predictions

### GPS Service (`gps_service.py`)
- Unit position tracking
- Blue-on-blue prevention
- Proximity alerts
- Deployment optimization

### Data Fusion (`data_fusion.py`)
- Multi-source threat correlation
- Tactical picture generation
- Situation assessment
- Recommendation generation

## Error Handling

All API endpoints include comprehensive error handling:
- Input validation
- Database error recovery
- Service failure fallbacks
- Detailed error logging

## Security

- Input sanitization
- SQL injection prevention
- CORS configuration
- Rate limiting (to be implemented)
- Authentication (to be implemented)

## Next Steps

- [ ] Implement API route handlers
- [ ] Add WebSocket support for real-time updates
- [ ] Implement authentication/authorization
- [ ] Add rate limiting
- [ ] Enhanced testing coverage
- [ ] API documentation
- [ ] Docker containerization

## License

[Your License Here]
