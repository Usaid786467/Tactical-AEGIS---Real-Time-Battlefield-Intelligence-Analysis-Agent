# Tactical AEGIS - Real-Time Battlefield Intelligence & Analysis Agent

## Project Overview
An AI-powered command and control dashboard that fuses multiple data streams (satellite, drone, radio comms) into a single, coherent tactical picture, providing real-time analysis and threat prediction.

## Core Features

### 1. Multi-Source Data Fusion
- Integrate satellite imagery, drone video feeds, ground sensor data, and radio communications
- AI (Gemini) uses vision and NLP capabilities to identify threats
- Examples: "Vehicle convoy detected at grid X," "Weapon fire audio signature recognized"

### 2. Predictive Threat Modeling
- Analyze enemy movement patterns and historical data
- Predict potential ambush sites, IED placement locations, or next likely targets
- Enable proactive counter-measures

### 3. Automated SITREP Generation
- Voice-to-text debriefing capability
- AI automatically structures information into formal SITREP
- Extract key entities: locations, unit sizes, equipment

### 4. Friendly Force Tracking
- Overlay friendly unit positions from GPS data
- Prevent blue-on-blue incidents
- Optimize resource deployment

## Tech Stack

### Backend
- **Python 3.10+** with FastAPI for heavy data processing
- **Gemini API** for vision and NLP analysis
- **WebSocket** support for real-time data streaming
- **SQLite/PostgreSQL** for data persistence
- **Redis** for caching and real-time updates (optional)

### Frontend
- **React.js 18+** with TypeScript
- **Mapbox GL JS** or **OpenLayers** for real-time interactive maps
- **Tailwind CSS** for dark-mode, high-contrast military UI
- **Recharts** or **D3.js** for data visualization
- **Socket.io-client** for real-time updates

### AI Integration
- **Google Gemini API** (provided key: AIzaSyDoM23RVH_WZLsiNGxYpYlulLfEGb9XrNY)
- Vision analysis for satellite/drone imagery
- NLP for communication analysis and SITREP generation

## Project Structure

```
tactical-aegis/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration management
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── data_fusion.py  # Multi-source data endpoints
│   │   │   │   ├── threat_analysis.py
│   │   │   │   ├── sitrep.py       # SITREP generation
│   │   │   │   ├── tracking.py     # Friendly force tracking
│   │   │   │   └── websocket.py    # Real-time data streaming
│   │   ├── services/
│   │   │   ├── gemini_service.py   # Gemini API integration
│   │   │   ├── image_analysis.py   # Satellite/drone imagery analysis
│   │   │   ├── nlp_service.py      # Communication analysis
│   │   │   ├── threat_predictor.py # Threat modeling algorithms
│   │   │   └── gps_service.py      # GPS tracking service
│   │   ├── models/
│   │   │   ├── threat.py           # Threat data models
│   │   │   ├── sitrep.py           # SITREP data models
│   │   │   └── tracking.py         # Tracking data models
│   │   ├── utils/
│   │   │   ├── audio_processor.py  # Audio signature analysis
│   │   │   ├── data_fusion.py      # Data fusion utilities
│   │   │   └── validators.py       # Input validation
│   │   └── database/
│   │       ├── database.py         # Database connection
│   │       └── schemas.py          # Database schemas
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py             # API endpoint tests
│   │   ├── test_gemini_service.py  # Gemini integration tests
│   │   ├── test_threat_predictor.py
│   │   └── test_data_fusion.py
│   ├── requirements.txt
│   ├── .env.example                # Environment variables template
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.tsx                 # Main application component
│   │   ├── index.tsx               # Entry point
│   │   ├── components/
│   │   │   ├── Map/
│   │   │   │   ├── TacticalMap.tsx # Main map component
│   │   │   │   ├── LayerControls.tsx
│   │   │   │   └── MarkerManager.tsx
│   │   │   ├── Dashboard/
│   │   │   │   ├── ThreatPanel.tsx
│   │   │   │   ├── SitrepPanel.tsx
│   │   │   │   ├── TrackingPanel.tsx
│   │   │   │   └── DataFusionPanel.tsx
│   │   │   ├── Analysis/
│   │   │   │   ├── ImageAnalyzer.tsx
│   │   │   │   ├── ThreatPredictor.tsx
│   │   │   │   └── AudioAnalyzer.tsx
│   │   │   ├── Voice/
│   │   │   │   └── VoiceDebriefing.tsx
│   │   │   └── Common/
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── NotificationCenter.tsx
│   │   ├── services/
│   │   │   ├── api.ts              # API client
│   │   │   ├── websocket.ts        # WebSocket connection
│   │   │   └── mapService.ts       # Map utilities
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useThreatData.ts
│   │   │   └── useVoiceRecording.ts
│   │   ├── types/
│   │   │   ├── threat.ts
│   │   │   ├── sitrep.ts
│   │   │   └── tracking.ts
│   │   ├── utils/
│   │   │   ├── formatters.ts
│   │   │   └── validators.ts
│   │   └── styles/
│   │       └── globals.css         # Tailwind + custom styles
│   ├── tests/
│   │   ├── components/
│   │   │   └── TacticalMap.test.tsx
│   │   └── services/
│   │       └── api.test.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── README.md
│
├── config/
│   └── api_keys.py                 # Centralized API keys (DO NOT COMMIT)
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── docs/
│   ├── API.md                      # API documentation
│   ├── ARCHITECTURE.md             # System architecture
│   └── DEPLOYMENT.md               # Deployment guide
│
├── scripts/
│   ├── setup.sh                    # Initial setup script
│   ├── test_all.sh                 # Run all tests
│   └── start_dev.sh                # Start development servers
│
├── .gitignore
├── README.md                       # This file
└── LICENSE
```

## API Keys Configuration

Create a file `config/api_keys.py`:

```python
"""
API Keys Configuration
Store all API keys here. DO NOT commit this file to version control.
"""

# Gemini AI API Key
GEMINI_API_KEY = "AIzaSyDoM23RVH_WZLsiNGxYpYlulLfEGb9XrNY"

# Map Services (Free tiers available)
MAPBOX_ACCESS_TOKEN = ""  # Get from: https://www.mapbox.com/
OPENSTREETMAP_API_KEY = ""  # Optional, OSM is free

# Weather Data (Optional, for environmental analysis)
OPENWEATHER_API_KEY = ""  # Get from: https://openweathermap.org/

# Speech-to-Text (for voice debriefing)
# Using Google Cloud Speech-to-Text (free tier available)
GOOGLE_CLOUD_SPEECH_KEY = ""  # Or use Web Speech API (browser-based, free)

# Satellite Imagery (Free/Educational tiers)
SENTINEL_HUB_API_KEY = ""  # Get from: https://www.sentinel-hub.com/
NASA_API_KEY = ""  # Get from: https://api.nasa.gov/

# Database (if using cloud)
DATABASE_URL = "sqlite:///./tactical_aegis.db"  # Local SQLite by default

# Redis (Optional, for caching)
REDIS_URL = "redis://localhost:6379"  # Local Redis
```

## Environment Variables (.env.example)

```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=True

# Database
DATABASE_URL=sqlite:///./tactical_aegis.db

# Gemini AI
GEMINI_API_KEY=AIzaSyDoM23RVH_WZLsiNGxYpYlulLfEGb9XrNY

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Map Services
MAPBOX_ACCESS_TOKEN=
OPENSTREETMAP_API_KEY=

# Optional Services
OPENWEATHER_API_KEY=
SENTINEL_HUB_API_KEY=
NASA_API_KEY=

# Redis (Optional)
REDIS_URL=redis://localhost:6379
USE_REDIS=False

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Installation & Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm/yarn
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Update .env with your API keys

# Run tests
pytest tests/ -v

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install

# Copy environment variables
cp .env.example .env

# Update .env with your API keys

# Run tests
npm test
# or
yarn test

# Start development server
npm run dev
# or
yarn dev
```

## Backend Requirements (requirements.txt)

```txt
# FastAPI and dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Google Gemini AI
google-generativeai==0.3.1

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9  # PostgreSQL (optional)
aiosqlite==0.19.0

# WebSocket
websockets==12.0
python-socketio==5.10.0

# Data Processing
numpy==1.26.2
pandas==2.1.3
pillow==10.1.0
opencv-python==4.8.1.78

# Audio Processing
librosa==0.10.1
soundfile==0.12.1
pydub==0.25.1

# HTTP Client
httpx==0.25.1
aiohttp==3.9.1

# Environment Variables
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1

# Caching (Optional)
redis==5.0.1
aioredis==2.0.1

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
```

## Frontend Package.json

```json
{
  "name": "tactical-aegis-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src --ext ts,tsx",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\""
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "mapbox-gl": "^3.0.0",
    "ol": "^8.2.0",
    "socket.io-client": "^4.6.0",
    "axios": "^1.6.2",
    "recharts": "^2.10.3",
    "date-fns": "^2.30.0",
    "zustand": "^4.4.7",
    "react-query": "^3.39.3",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@types/mapbox-gl": "^3.0.0",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.7",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16",
    "vitest": "^1.0.4",
    "@vitest/ui": "^1.0.4",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "eslint": "^8.55.0",
    "prettier": "^3.1.1"
  }
}
```

## Testing Strategy

### Backend Testing
Each backend module must have corresponding tests in the `tests/` directory:
- Unit tests for services and utilities
- Integration tests for API endpoints
- Mock Gemini API responses for consistent testing
- Test coverage target: >80%

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_gemini_service.py -v
```

### Frontend Testing
Each frontend component should have tests:
- Component rendering tests
- User interaction tests
- API integration tests with mocked responses
- WebSocket connection tests

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

## Free API Resources

### Maps
- **Mapbox**: Free tier with 50,000 map loads/month - https://www.mapbox.com/
- **OpenStreetMap**: Completely free - https://www.openstreetmap.org/
- **Leaflet**: Open-source map library - https://leafletjs.com/

### Satellite Imagery
- **Sentinel Hub**: Educational/trial accounts - https://www.sentinel-hub.com/
- **NASA API**: Free with API key - https://api.nasa.gov/
- **Copernicus Open Access Hub**: Free Sentinel satellite data - https://scihub.copernicus.eu/

### Weather Data
- **OpenWeatherMap**: Free tier with 60 calls/minute - https://openweathermap.org/

### Speech-to-Text
- **Web Speech API**: Browser-based, completely free
- **Google Cloud Speech**: Free tier with 60 minutes/month

## Development Workflow

1. **Start Backend**: `cd backend && uvicorn app.main:app --reload`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Run Tests**: Use `scripts/test_all.sh` to run both backend and frontend tests
4. **Check Logs**: Monitor console output for errors
5. **Iterate**: Make changes and tests will auto-run

## Key Implementation Notes

### Gemini Integration
- Use Gemini Pro Vision for satellite/drone image analysis
- Use Gemini Pro for text analysis and SITREP generation
- Implement proper error handling for API rate limits
- Cache analyzed results to minimize API calls

### Real-Time Updates
- Use WebSocket for pushing threat updates to frontend
- Implement reconnection logic for dropped connections
- Use Server-Sent Events (SSE) as fallback

### Security Considerations
- Implement proper authentication (JWT tokens)
- Sanitize all user inputs
- Use HTTPS in production
- Implement rate limiting on API endpoints

### Performance Optimization
- Lazy load map tiles
- Implement data pagination for large datasets
- Use Redis for caching frequently accessed data
- Optimize image processing with async operations

## Success Criteria

- ✅ All tests passing in both backend and frontend
- ✅ No errors in console during normal operation
- ✅ Real-time map updates within 2 seconds
- ✅ Gemini API integration working for image and text analysis
- ✅ Voice debriefing converts to structured SITREP
- ✅ Threat predictions display on map with confidence scores
- ✅ Responsive UI works on tablets/desktop
- ✅ Dark mode military-style UI implemented

## Error Handling Requirements

- All API calls must have try-catch blocks
- Display user-friendly error messages
- Log errors to backend for debugging
- Implement graceful degradation if AI services fail
- Add reconnection logic for WebSocket failures

## Deployment

See `docs/DEPLOYMENT.md` for production deployment instructions.

## License

[Specify your license]

## Contributors

Usaid Ahmad - Lead Developer & ML Engineer

---

## IMPORTANT NOTES FOR CLAUDE CODE

1. **Start with Backend First**: Build the complete backend structure, implement all services, and ensure all tests pass before starting frontend.

2. **Test at Every Step**: After creating each service or component, write and run tests immediately. DO NOT proceed if tests fail.

3. **Use Free APIs Initially**: Start with free tier APIs and mock data where needed. The system should work even with limited API calls.

4. **Error Handling is Critical**: Every function must handle errors gracefully. No unhandled exceptions.

5. **Dark Mode Military UI**: Use high contrast colors (green/amber on black), military-style fonts, and tactical symbology.

6. **Real Data Simulation**: Create realistic mock data for testing when real satellite/drone feeds aren't available.

7. **Documentation**: Add docstrings to all functions and components. Keep README.md files in each major directory.

8. **Git Best Practices**: Make atomic commits with clear messages. Use feature branches.

9. **Configuration Management**: Never hardcode API keys. Always use environment variables.

10. **Performance First**: Optimize for real-time performance. Map should render smoothly even with 100+ markers.

---

**Ready to build? Start with backend setup and let's create an impressive tactical intelligence system!**
