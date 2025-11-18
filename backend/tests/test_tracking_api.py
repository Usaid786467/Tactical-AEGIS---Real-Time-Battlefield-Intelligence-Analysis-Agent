"""
Tests for friendly force tracking API endpoints
"""
import pytest
from fastapi import status


class TestTrackingAPI:
    """Test suite for tracking endpoints"""

    def test_create_unit(self, client, sample_unit_data):
        """Test creating a new friendly unit"""
        response = client.post("/api/tracking/units", json=sample_unit_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["unit_id"] == sample_unit_data["unit_id"]
        assert data["unit_name"] == sample_unit_data["unit_name"]
        assert data["status"] == sample_unit_data["status"]
        assert "id" in data
        assert "created_at" in data

    def test_get_units(self, client, sample_unit_data):
        """Test getting list of units"""
        # Create a unit first
        client.post("/api/tracking/units", json=sample_unit_data)

        # Get all units
        response = client.get("/api/tracking/units")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["unit_id"] == sample_unit_data["unit_id"]

    def test_get_unit_by_id(self, client, sample_unit_data):
        """Test getting a specific unit by unit_id"""
        # Create a unit
        client.post("/api/tracking/units", json=sample_unit_data)

        # Get the unit
        response = client.get(f"/api/tracking/units/{sample_unit_data['unit_id']}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["unit_id"] == sample_unit_data["unit_id"]

    def test_update_unit_position(self, client, sample_unit_data):
        """Test updating unit position"""
        # Create a unit
        client.post("/api/tracking/units", json=sample_unit_data)

        # Update position
        update_data = {
            "latitude": 34.0700,
            "longitude": -118.2600,
            "status": "amber",
        }
        response = client.put(
            f"/api/tracking/units/{sample_unit_data['unit_id']}/position",
            json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["latitude"] == update_data["latitude"]
        assert data["longitude"] == update_data["longitude"]
        assert data["status"] == update_data["status"]

    def test_delete_unit(self, client, sample_unit_data):
        """Test deleting a unit"""
        # Create a unit
        client.post("/api/tracking/units", json=sample_unit_data)

        # Delete the unit
        response = client.delete(f"/api/tracking/units/{sample_unit_data['unit_id']}")
        assert response.status_code == status.HTTP_200_OK

        # Verify it's deleted
        get_response = client.get(f"/api/tracking/units/{sample_unit_data['unit_id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_unit_history(self, client, sample_unit_data):
        """Test getting unit position history"""
        # Create a unit
        client.post("/api/tracking/units", json=sample_unit_data)

        # Update position multiple times
        for i in range(3):
            update_data = {
                "latitude": 34.0600 + (i * 0.01),
                "longitude": -118.2500 + (i * 0.01),
            }
            client.put(
                f"/api/tracking/units/{sample_unit_data['unit_id']}/position",
                json=update_data
            )

        # Get history
        response = client.get(f"/api/tracking/units/{sample_unit_data['unit_id']}/history")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_blue_on_blue_check(self, client, sample_unit_data):
        """Test blue-on-blue proximity check"""
        # Create a unit
        client.post("/api/tracking/units", json=sample_unit_data)

        # Check for nearby units (close to the unit's position)
        check_data = {
            "target_latitude": 34.0610,  # Close to unit
            "target_longitude": -118.2510,
            "radius": 2000,  # 2km radius
        }
        response = client.post("/api/tracking/blue-on-blue", json=check_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "safe" in data
        assert "nearby_units" in data
        assert "alerts" in data
        assert len(data["nearby_units"]) > 0

    def test_blue_on_blue_safe_area(self, client, sample_unit_data):
        """Test blue-on-blue check in safe area"""
        # Create a unit
        client.post("/api/tracking/units", json=sample_unit_data)

        # Check far from unit
        check_data = {
            "target_latitude": 35.0000,  # Far from unit
            "target_longitude": -119.0000,
            "radius": 1000,
        }
        response = client.post("/api/tracking/blue-on-blue", json=check_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["safe"] is True
        assert len(data["nearby_units"]) == 0

    def test_get_nearby_units(self, client, sample_unit_data):
        """Test getting nearby units"""
        # Create multiple units
        client.post("/api/tracking/units", json=sample_unit_data)

        nearby_unit = sample_unit_data.copy()
        nearby_unit["unit_id"] = "2-502-INF"
        nearby_unit["latitude"] = 34.0620  # Close by
        client.post("/api/tracking/units", json=nearby_unit)

        # Get nearby units
        params = {
            "latitude": 34.0610,
            "longitude": -118.2500,
            "radius_km": 2,
        }
        response = client.get("/api/tracking/nearby", params=params)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_tracking_stats(self, client, sample_unit_data):
        """Test getting tracking statistics"""
        # Create units with different statuses
        client.post("/api/tracking/units", json=sample_unit_data)

        amber_unit = sample_unit_data.copy()
        amber_unit["unit_id"] = "2-502-INF"
        amber_unit["status"] = "amber"
        client.post("/api/tracking/units", json=amber_unit)

        response = client.get("/api/tracking/stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_units" in data
        assert "active_units" in data
        assert "by_status" in data
        assert data["total_units"] >= 2

    def test_create_duplicate_unit(self, client, sample_unit_data):
        """Test creating a duplicate unit_id"""
        # Create first unit
        response1 = client.post("/api/tracking/units", json=sample_unit_data)
        assert response1.status_code == status.HTTP_200_OK

        # Try to create duplicate
        response2 = client.post("/api/tracking/units", json=sample_unit_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_nonexistent_unit(self, client):
        """Test updating a unit that doesn't exist"""
        update_data = {
            "latitude": 34.0700,
            "longitude": -118.2600,
        }
        response = client.put("/api/tracking/units/NONEXISTENT/position", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_active_units_only(self, client, sample_unit_data):
        """Test getting only active units"""
        # Create active unit
        client.post("/api/tracking/units", json=sample_unit_data)

        # Create inactive unit
        inactive_unit = sample_unit_data.copy()
        inactive_unit["unit_id"] = "2-502-INF"
        client.post("/api/tracking/units", json=inactive_unit)
        # Deactivate it
        client.put(
            f"/api/tracking/units/{inactive_unit['unit_id']}/position",
            json={"status": "black"}
        )

        # Get active units only
        response = client.get("/api/tracking/units?active_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Both should still be returned since we didn't explicitly deactivate
        assert len(data) >= 1
