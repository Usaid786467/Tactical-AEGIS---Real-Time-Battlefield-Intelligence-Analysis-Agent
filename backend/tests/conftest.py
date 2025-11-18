"""
Test configuration and fixtures for Tactical AEGIS tests
"""
import os
import pytest

# Set test environment variables before importing the app
os.environ.setdefault("GEMINI_API_KEY", "test_api_key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("CORS_ORIGINS", "[\"http://localhost:3000\"]")
os.environ.setdefault("ENVIRONMENT", "test")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_threat_data():
    """Sample threat data for testing"""
    return {
        "threat_type": "vehicle",
        "threat_level": "high",
        "confidence": 0.85,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "description": "Hostile armored vehicle detected",
        "source": "satellite",
    }


@pytest.fixture
def sample_unit_data():
    """Sample friendly unit data for testing"""
    return {
        "unit_id": "1-502-INF",
        "unit_name": "1st Battalion, 502nd Infantry",
        "callsign": "Strike 6",
        "unit_type": "infantry",
        "personnel_count": 120,
        "latitude": 34.0600,
        "longitude": -118.2500,
        "status": "green",
    }


@pytest.fixture
def sample_sitrep_data():
    """Sample SITREP data for testing"""
    return {
        "title": "Routine Daily SITREP",
        "situation": "All units operational, no hostile contact",
        "mission": "Continue area security operations",
        "execution": "Units conducting scheduled patrols",
        "admin_logistics": "All supplies adequate",
        "command_signal": "Command net operational",
        "priority": "routine",
        "source": "TOC",
    }
