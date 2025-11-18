"""
API Endpoint Tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Tactical AEGIS"
    assert data["status"] == "operational"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "gemini_api" in data


def test_nonexistent_endpoint():
    """Test 404 for nonexistent endpoint"""
    response = client.get("/nonexistent")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
