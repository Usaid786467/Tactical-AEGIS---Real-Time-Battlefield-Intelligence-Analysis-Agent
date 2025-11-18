"""
GPS Tracking Service
Manages friendly force tracking and blue-on-blue prevention
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from math import radians, sin, cos, sqrt, atan2, degrees

from app.database.schemas import FriendlyForceDB
from app.models.tracking import UnitStatus, ProximityAlert

logger = logging.getLogger(__name__)


class GPSService:
    """Service for GPS tracking and unit management"""

    # Proximity thresholds (in meters)
    PROXIMITY_WARNING = 2000  # 2km
    PROXIMITY_ALERT = 1000    # 1km
    PROXIMITY_DANGER = 500    # 500m

    def __init__(self):
        """Initialize GPS service"""
        logger.info("GPS service initialized")

    def update_unit_position(
        self,
        db: Session,
        unit_id: str,
        latitude: float,
        longitude: float,
        altitude: Optional[float] = None,
        heading: Optional[float] = None,
        speed: Optional[float] = None,
        status: Optional[UnitStatus] = None
    ) -> FriendlyForceDB:
        """
        Update unit position and tracking data

        Args:
            db: Database session
            unit_id: Unique unit identifier
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            altitude: Optional altitude in meters
            heading: Optional heading in degrees (0-360)
            speed: Optional speed in m/s
            status: Optional unit status

        Returns:
            Updated FriendlyForceDB record
        """
        try:
            # Get existing unit or create new
            unit = db.query(FriendlyForceDB).filter(
                FriendlyForceDB.unit_id == unit_id
            ).first()

            if unit:
                # Update existing unit
                unit.latitude = latitude
                unit.longitude = longitude
                if altitude is not None:
                    unit.altitude = altitude
                if heading is not None:
                    unit.heading = heading
                if speed is not None:
                    unit.speed = speed
                if status is not None:
                    unit.status = status.value
                unit.last_contact = datetime.utcnow()
            else:
                logger.warning(f"Unit {unit_id} not found for position update")
                return None

            db.commit()
            db.refresh(unit)

            logger.debug(f"Updated position for unit {unit_id}")
            return unit

        except Exception as e:
            logger.error(f"Failed to update unit position: {e}")
            db.rollback()
            raise

    def get_nearby_units(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0
    ) -> List[FriendlyForceDB]:
        """
        Get all friendly units within radius

        Args:
            db: Database session
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers

        Returns:
            List of nearby units
        """
        try:
            # Get all active units
            all_units = db.query(FriendlyForceDB).filter(
                FriendlyForceDB.active == True
            ).all()

            # Filter by distance
            nearby_units = []
            for unit in all_units:
                distance = self.calculate_distance(
                    latitude, longitude,
                    unit.latitude, unit.longitude
                )

                if distance <= radius_km:
                    nearby_units.append(unit)

            logger.debug(f"Found {len(nearby_units)} units within {radius_km}km")
            return nearby_units

        except Exception as e:
            logger.error(f"Failed to get nearby units: {e}")
            return []

    def check_blue_on_blue(
        self,
        db: Session,
        target_latitude: float,
        target_longitude: float,
        radius_meters: float = 1000
    ) -> Dict[str, Any]:
        """
        Check for potential blue-on-blue incidents

        Args:
            db: Database session
            target_latitude: Target latitude
            target_longitude: Target longitude
            radius_meters: Safety radius in meters

        Returns:
            Safety check results with nearby units
        """
        try:
            # Get nearby units
            radius_km = radius_meters / 1000
            nearby_units = self.get_nearby_units(
                db,
                target_latitude,
                target_longitude,
                radius_km
            )

            # Calculate distances
            unit_distances = []
            minimum_distance = float('inf')
            alerts = []

            for unit in nearby_units:
                distance_m = self.calculate_distance(
                    target_latitude, target_longitude,
                    unit.latitude, unit.longitude
                ) * 1000  # Convert to meters

                unit_distances.append({
                    "unit_id": unit.unit_id,
                    "unit_name": unit.unit_name,
                    "callsign": unit.callsign,
                    "distance_meters": distance_m,
                    "latitude": unit.latitude,
                    "longitude": unit.longitude,
                    "status": unit.status
                })

                minimum_distance = min(minimum_distance, distance_m)

                # Generate alerts based on distance
                if distance_m < self.PROXIMITY_DANGER:
                    alerts.append({
                        "alert_type": "proximity",
                        "unit1_id": unit.unit_id,
                        "unit2_id": "target",
                        "distance": distance_m,
                        "severity": "high",
                        "message": f"DANGER: Friendly unit {unit.callsign or unit.unit_name} within {distance_m:.0f}m of target"
                    })
                elif distance_m < self.PROXIMITY_ALERT:
                    alerts.append({
                        "alert_type": "proximity",
                        "unit1_id": unit.unit_id,
                        "unit2_id": "target",
                        "distance": distance_m,
                        "severity": "medium",
                        "message": f"WARNING: Friendly unit {unit.callsign or unit.unit_name} within {distance_m:.0f}m of target"
                    })
                elif distance_m < self.PROXIMITY_WARNING:
                    alerts.append({
                        "alert_type": "proximity",
                        "unit1_id": unit.unit_id,
                        "unit2_id": "target",
                        "distance": distance_m,
                        "severity": "low",
                        "message": f"CAUTION: Friendly unit {unit.callsign or unit.unit_name} within {distance_m:.0f}m of target"
                    })

            safe = len(alerts) == 0 or all(a["severity"] == "low" for a in alerts)

            return {
                "safe": safe,
                "nearby_units": unit_distances,
                "minimum_distance": minimum_distance if minimum_distance != float('inf') else None,
                "alerts": alerts,
                "check_radius_meters": radius_meters
            }

        except Exception as e:
            logger.error(f"Blue-on-blue check failed: {e}")
            raise

    def detect_proximity_alerts(
        self,
        db: Session,
        threshold_meters: float = 1000
    ) -> List[ProximityAlert]:
        """
        Detect all proximity alerts between friendly units

        Args:
            db: Database session
            threshold_meters: Distance threshold for alerts

        Returns:
            List of proximity alerts
        """
        try:
            alerts = []

            # Get all active units
            units = db.query(FriendlyForceDB).filter(
                FriendlyForceDB.active == True
            ).all()

            # Check each pair of units
            for i, unit1 in enumerate(units):
                for unit2 in units[i+1:]:
                    distance_m = self.calculate_distance(
                        unit1.latitude, unit1.longitude,
                        unit2.latitude, unit2.longitude
                    ) * 1000

                    if distance_m < threshold_meters:
                        # Check if on collision course
                        time_to_closest = None
                        if unit1.speed and unit2.speed and unit1.heading and unit2.heading:
                            time_to_closest = self._calculate_time_to_closest(
                                unit1, unit2, distance_m
                            )

                        severity = "high" if distance_m < self.PROXIMITY_DANGER else \
                                   "medium" if distance_m < self.PROXIMITY_ALERT else "low"

                        alerts.append({
                            "alert_type": "proximity",
                            "unit1_id": unit1.unit_id,
                            "unit2_id": unit2.unit_id,
                            "distance": distance_m,
                            "time_to_closest": time_to_closest,
                            "severity": severity,
                            "message": f"Units {unit1.callsign or unit1.unit_name} and {unit2.callsign or unit2.unit_name} within {distance_m:.0f}m"
                        })

            logger.info(f"Detected {len(alerts)} proximity alerts")
            return alerts

        except Exception as e:
            logger.error(f"Proximity alert detection failed: {e}")
            return []

    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in km

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def calculate_bearing(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate bearing between two points

        Returns:
            Bearing in degrees (0-360)
        """
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlon = lon2 - lon1

        x = sin(dlon) * cos(lat2)
        y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

        bearing = atan2(x, y)
        bearing = degrees(bearing)
        bearing = (bearing + 360) % 360

        return bearing

    def _calculate_time_to_closest(
        self,
        unit1: FriendlyForceDB,
        unit2: FriendlyForceDB,
        current_distance_m: float
    ) -> Optional[float]:
        """
        Calculate time to closest point of approach

        Returns:
            Time in seconds, or None if not converging
        """
        try:
            # Convert headings to vectors
            heading1_rad = radians(unit1.heading)
            heading2_rad = radians(unit2.heading)

            # Velocity vectors (m/s)
            v1x = unit1.speed * sin(heading1_rad)
            v1y = unit1.speed * cos(heading1_rad)

            v2x = unit2.speed * sin(heading2_rad)
            v2y = unit2.speed * cos(heading2_rad)

            # Relative velocity
            vrelx = v2x - v1x
            vrely = v2y - v1y

            # Relative position (approximate as planar for short distances)
            bearing = self.calculate_bearing(
                unit1.latitude, unit1.longitude,
                unit2.latitude, unit2.longitude
            )
            bearing_rad = radians(bearing)

            dx = current_distance_m * sin(bearing_rad)
            dy = current_distance_m * cos(bearing_rad)

            # Time to closest approach
            # t = -(dx * vrelx + dy * vrely) / (vrelx^2 + vrely^2)
            denominator = vrelx**2 + vrely**2

            if denominator > 0:
                t = -(dx * vrelx + dy * vrely) / denominator
                if t > 0:
                    return t

            return None

        except Exception as e:
            logger.warning(f"Could not calculate time to closest: {e}")
            return None

    def optimize_deployment(
        self,
        db: Session,
        available_unit_ids: List[str],
        objective_lat: float,
        objective_lon: float,
        mission_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Optimize unit deployment for mission

        Args:
            db: Database session
            available_unit_ids: List of available unit IDs
            objective_lat: Objective latitude
            objective_lon: Objective longitude
            mission_type: Type of mission

        Returns:
            List of deployment recommendations
        """
        try:
            recommendations = []

            # Get available units
            units = db.query(FriendlyForceDB).filter(
                and_(
                    FriendlyForceDB.unit_id.in_(available_unit_ids),
                    FriendlyForceDB.active == True
                )
            ).all()

            # Calculate distances and sort by proximity
            unit_distances = []
            for unit in units:
                distance = self.calculate_distance(
                    unit.latitude, unit.longitude,
                    objective_lat, objective_lon
                )
                unit_distances.append((unit, distance))

            unit_distances.sort(key=lambda x: x[1])

            # Generate recommendations
            for i, (unit, distance) in enumerate(unit_distances):
                # Estimate time (assuming average speed of 30 km/h)
                estimated_time_hours = distance / 30

                # Simple direct route (in practice, would use routing API)
                bearing = self.calculate_bearing(
                    unit.latitude, unit.longitude,
                    objective_lat, objective_lon
                )

                recommendation = {
                    "unit_id": unit.unit_id,
                    "unit_name": unit.unit_name,
                    "callsign": unit.callsign,
                    "current_position": {
                        "latitude": unit.latitude,
                        "longitude": unit.longitude
                    },
                    "distance_km": distance,
                    "estimated_time_hours": estimated_time_hours,
                    "bearing": bearing,
                    "recommended_route": [
                        {"latitude": unit.latitude, "longitude": unit.longitude},
                        {"latitude": objective_lat, "longitude": objective_lon}
                    ],
                    "priority": i + 1,
                    "reasoning": f"Closest available unit, {distance:.1f}km from objective, ETA {estimated_time_hours:.1f} hours"
                }

                recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            logger.error(f"Deployment optimization failed: {e}")
            return []


# Create singleton instance
gps_service = GPSService()
