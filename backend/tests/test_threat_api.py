"""
Tests for threat analysis API endpoints
"""
import pytest
from fastapi import status


class TestThreatAPI:
    """Test suite for threat analysis endpoints"""

    def test_create_threat(self, client, sample_threat_data):
        """Test creating a new threat"""
        response = client.post("/api/threats", json=sample_threat_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["threat_type"] == sample_threat_data["threat_type"]
        assert data["threat_level"] == sample_threat_data["threat_level"]
        assert data["confidence"] == sample_threat_data["confidence"]
        assert "id" in data
        assert "created_at" in data

    def test_get_threats(self, client, sample_threat_data):
        """Test getting list of threats"""
        # Create a threat first
        client.post("/api/threats", json=sample_threat_data)

        # Get all threats
        response = client.get("/api/threats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["threat_type"] == sample_threat_data["threat_type"]

    def test_get_threats_with_filters(self, client, sample_threat_data):
        """Test getting threats with filters"""
        # Create threats
        client.post("/api/threats", json=sample_threat_data)

        low_threat = sample_threat_data.copy()
        low_threat["threat_level"] = "low"
        client.post("/api/threats", json=low_threat)

        # Filter by threat level
        response = client.get("/api/threats?threat_level=high")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["threat_level"] == "high"

    def test_get_threat_by_id(self, client, sample_threat_data):
        """Test getting a specific threat by ID"""
        # Create a threat
        create_response = client.post("/api/threats", json=sample_threat_data)
        threat_id = create_response.json()["id"]

        # Get the threat
        response = client.get(f"/api/threats/{threat_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == threat_id
        assert data["threat_type"] == sample_threat_data["threat_type"]

    def test_update_threat(self, client, sample_threat_data):
        """Test updating a threat"""
        # Create a threat
        create_response = client.post("/api/threats", json=sample_threat_data)
        threat_id = create_response.json()["id"]

        # Update the threat
        update_data = {
            "threat_level": "critical",
            "verified": True,
        }
        response = client.put(f"/api/threats/{threat_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["threat_level"] == "critical"
        assert data["verified"] is True

    def test_delete_threat(self, client, sample_threat_data):
        """Test deleting a threat"""
        # Create a threat
        create_response = client.post("/api/threats", json=sample_threat_data)
        threat_id = create_response.json()["id"]

        # Delete the threat
        response = client.delete(f"/api/threats/{threat_id}")
        assert response.status_code == status.HTTP_200_OK

        # Verify it's deleted
        get_response = client.get(f"/api/threats/{threat_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_threat_stats(self, client, sample_threat_data):
        """Test getting threat statistics"""
        # Create multiple threats
        for _ in range(3):
            client.post("/api/threats", json=sample_threat_data)

        response = client.get("/api/threats/stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_threats" in data
        assert "active_threats" in data
        assert "by_level" in data
        assert data["total_threats"] >= 3

    def test_analyze_image_missing_data(self, client):
        """Test image analysis with missing data"""
        request_data = {
            "source": "satellite",
        }
        response = client.post("/api/threats/analyze/image", json=request_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_predict_threats_invalid_bounds(self, client):
        """Test threat prediction with invalid area bounds"""
        request_data = {
            "area_bounds": {
                "north": 0,
                "south": 90,  # Invalid: south > north
                "east": 0,
                "west": 0,
            }
        }
        response = client.post("/api/threats/predict", json=request_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_threat_invalid_confidence(self, client, sample_threat_data):
        """Test creating threat with invalid confidence value"""
        invalid_data = sample_threat_data.copy()
        invalid_data["confidence"] = 1.5  # Invalid: > 1.0
        response = client.post("/api/threats", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_active_threats_only(self, client, sample_threat_data):
        """Test getting only active threats"""
        # Create active threat
        client.post("/api/threats", json=sample_threat_data)

        # Create inactive threat
        inactive_threat = sample_threat_data.copy()
        inactive_threat["latitude"] = 35.0
        create_response = client.post("/api/threats", json=inactive_threat)
        threat_id = create_response.json()["id"]
        client.put(f"/api/threats/{threat_id}", json={"active": False})

        # Get active threats only
        response = client.get("/api/threats?active_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(threat["active"] for threat in data)
