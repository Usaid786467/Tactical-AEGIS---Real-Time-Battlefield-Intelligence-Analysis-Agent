"""
Friendly Force Tracking API Routes
Endpoints for GPS tracking and blue-on-blue prevention
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database.database import get_db
from app.database.schemas import FriendlyForceDB
from app.models.tracking import (
    FriendlyForce, FriendlyForceCreate, FriendlyForceUpdate,
    TrackingUpdate, BlueonBlueCheck, BlueonBlueResponse,
    DeploymentOptimization, DeploymentRecommendation
)
from app.services.gps_service import gps_service
from app.utils.validators import validate_coordinates, validate_unit_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/units", response_model=FriendlyForce)
async def create_unit(unit: FriendlyForceCreate, db: Session = Depends(get_db)):
    """
    Register new friendly force unit for tracking

    Creates a new unit entry in the tracking system
    """
    try:
        # Validate unit ID
        valid, error = validate_unit_id(unit.unit_id)
        if not valid:
            raise HTTPException(status_code=400, detail=error)

        # Validate coordinates
        valid, error = validate_coordinates(unit.latitude, unit.longitude)
        if not valid:
            raise HTTPException(status_code=400, detail=error)

        # Check if unit already exists
        existing = db.query(FriendlyForceDB).filter(
            FriendlyForceDB.unit_id == unit.unit_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Unit ID already exists")

        # Create unit
        unit_db = FriendlyForceDB(
            unit_id=unit.unit_id,
            unit_name=unit.unit_name,
            unit_type=unit.unit_type.value if unit.unit_type else None,
            callsign=unit.callsign,
            latitude=unit.latitude,
            longitude=unit.longitude,
            altitude=unit.altitude,
            heading=unit.heading,
            speed=unit.speed,
            status=unit.status.value,
            personnel_count=unit.personnel_count,
            equipment=unit.equipment
        )

        db.add(unit_db)
        db.commit()
        db.refresh(unit_db)

        logger.info(f"Created new unit: {unit.unit_id}")
        return FriendlyForce.model_validate(unit_db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create unit: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create unit")


@router.get("/units", response_model=List[FriendlyForce])
async def get_units(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    status: Optional[str] = None,
    unit_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of friendly force units

    Query parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    - active_only: Only return active units
    - status: Filter by status (green/amber/red/black)
    - unit_type: Filter by unit type
    """
    try:
        query = db.query(FriendlyForceDB)

        if active_only:
            query = query.filter(FriendlyForceDB.active == True)

        if status:
            query = query.filter(FriendlyForceDB.status == status)

        if unit_type:
            query = query.filter(FriendlyForceDB.unit_type == unit_type)

        units = query.order_by(FriendlyForceDB.last_contact.desc()).offset(skip).limit(limit).all()

        return [FriendlyForce.model_validate(u) for u in units]

    except Exception as e:
        logger.error(f"Failed to retrieve units: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve units")


@router.get("/units/{unit_id}", response_model=FriendlyForce)
async def get_unit(unit_id: str, db: Session = Depends(get_db)):
    """Get specific unit by ID"""
    try:
        unit = db.query(FriendlyForceDB).filter(FriendlyForceDB.unit_id == unit_id).first()

        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")

        return FriendlyForce.model_validate(unit)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve unit: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve unit")


@router.patch("/units/{unit_id}", response_model=FriendlyForce)
async def update_unit_position(
    unit_id: str,
    update: FriendlyForceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update unit position and status

    Real-time position updates for GPS tracking
    """
    try:
        # Validate coordinates if provided
        if update.latitude is not None and update.longitude is not None:
            valid, error = validate_coordinates(update.latitude, update.longitude)
            if not valid:
                raise HTTPException(status_code=400, detail=error)

        # Update unit
        unit = gps_service.update_unit_position(
            db=db,
            unit_id=unit_id,
            latitude=update.latitude,
            longitude=update.longitude,
            altitude=update.altitude,
            heading=update.heading,
            speed=update.speed,
            status=update.status
        )

        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")

        return FriendlyForce.model_validate(unit)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update unit: {e}")
        raise HTTPException(status_code=500, detail="Failed to update unit")


@router.post("/tracking/update")
async def tracking_update(update: TrackingUpdate, db: Session = Depends(get_db)):
    """
    Real-time tracking update endpoint

    For high-frequency position updates from GPS devices
    """
    try:
        # Validate coordinates
        valid, error = validate_coordinates(update.latitude, update.longitude)
        if not valid:
            raise HTTPException(status_code=400, detail=error)

        # Update position
        unit = gps_service.update_unit_position(
            db=db,
            unit_id=update.unit_id,
            latitude=update.latitude,
            longitude=update.longitude,
            heading=update.heading,
            speed=update.speed
        )

        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")

        return {
            "status": "updated",
            "unit_id": update.unit_id,
            "timestamp": update.timestamp
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tracking update failed: {e}")
        raise HTTPException(status_code=500, detail="Tracking update failed")


@router.post("/blue-on-blue/check", response_model=BlueonBlueResponse)
async def check_blue_on_blue(request: BlueonBlueCheck, db: Session = Depends(get_db)):
    """
    Check for blue-on-blue (friendly fire) risk

    Checks if there are friendly units near a target location
    Critical for preventing friendly fire incidents

    Returns:
    - safe: Boolean indicating if area is safe to engage
    - nearby_units: List of units within radius
    - minimum_distance: Distance to nearest unit
    - alerts: List of proximity alerts
    """
    try:
        # Validate coordinates
        valid, error = validate_coordinates(
            request.target_latitude,
            request.target_longitude
        )
        if not valid:
            raise HTTPException(status_code=400, detail=error)

        # Perform check
        result = gps_service.check_blue_on_blue(
            db=db,
            target_latitude=request.target_latitude,
            target_longitude=request.target_longitude,
            radius_meters=request.radius
        )

        return BlueonBlueResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Blue-on-blue check failed: {e}")
        raise HTTPException(status_code=500, detail="Blue-on-blue check failed")


@router.get("/proximity-alerts")
async def get_proximity_alerts(
    threshold_meters: float = 1000,
    db: Session = Depends(get_db)
):
    """
    Get all proximity alerts between friendly units

    Detects units that are too close together
    Useful for deconfliction and coordination
    """
    try:
        alerts = gps_service.detect_proximity_alerts(
            db=db,
            threshold_meters=threshold_meters
        )

        return {
            "alerts": alerts,
            "total": len(alerts),
            "threshold_meters": threshold_meters
        }

    except Exception as e:
        logger.error(f"Proximity alert detection failed: {e}")
        raise HTTPException(status_code=500, detail="Proximity alert detection failed")


@router.post("/deployment/optimize")
async def optimize_deployment(
    request: DeploymentOptimization,
    db: Session = Depends(get_db)
):
    """
    Optimize unit deployment for mission

    Analyzes available units and recommends optimal deployment:
    - Best units to deploy based on proximity
    - Estimated time of arrival
    - Recommended routes
    - Priority ranking
    """
    try:
        # Validate objective coordinates
        valid, error = validate_coordinates(
            request.objective_location["latitude"],
            request.objective_location["longitude"]
        )
        if not valid:
            raise HTTPException(status_code=400, detail=error)

        # Optimize deployment
        recommendations = gps_service.optimize_deployment(
            db=db,
            available_unit_ids=request.available_units,
            objective_lat=request.objective_location["latitude"],
            objective_lon=request.objective_location["longitude"],
            mission_type=request.mission_type
        )

        return {
            "recommendations": recommendations,
            "total_units": len(recommendations),
            "mission_type": request.mission_type,
            "time_critical": request.time_critical
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deployment optimization failed: {e}")
        raise HTTPException(status_code=500, detail="Deployment optimization failed")


@router.get("/nearby")
async def get_nearby_units(
    latitude: float,
    longitude: float,
    radius_km: float = 10.0,
    db: Session = Depends(get_db)
):
    """
    Get friendly units within radius of a location

    Useful for situational awareness and coordination
    """
    try:
        # Validate coordinates
        valid, error = validate_coordinates(latitude, longitude)
        if not valid:
            raise HTTPException(status_code=400, detail=error)

        # Get nearby units
        units = gps_service.get_nearby_units(
            db=db,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )

        return {
            "units": [FriendlyForce.model_validate(u) for u in units],
            "total": len(units),
            "radius_km": radius_km,
            "center": {"latitude": latitude, "longitude": longitude}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Nearby units query failed: {e}")
        raise HTTPException(status_code=500, detail="Nearby units query failed")


@router.delete("/units/{unit_id}")
async def delete_unit(unit_id: str, db: Session = Depends(get_db)):
    """
    Deactivate unit (soft delete)

    Marks unit as inactive but preserves historical data
    """
    try:
        unit = db.query(FriendlyForceDB).filter(FriendlyForceDB.unit_id == unit_id).first()

        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")

        # Soft delete
        unit.active = False
        db.commit()

        return {"message": "Unit deactivated successfully", "unit_id": unit_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete unit: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete unit")
