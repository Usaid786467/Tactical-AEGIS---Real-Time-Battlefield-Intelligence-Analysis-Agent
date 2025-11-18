"""
Threat Analysis API Routes
Endpoints for threat detection, analysis, and prediction
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database.database import get_db
from app.database.schemas import ThreatDB
from app.models.threat import (
    Threat, ThreatCreate, ThreatUpdate, ThreatAnalysisRequest,
    ThreatAnalysisResponse, ThreatPredictionRequest, ThreatPredictionResponse
)
from app.services.image_analysis import image_analysis_service
from app.services.threat_predictor import threat_predictor_service
from app.utils.validators import validate_coordinates

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze/image", response_model=dict)
async def analyze_tactical_image(
    request: ThreatAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze tactical image for threats

    Processes satellite or drone imagery to detect threats such as:
    - Vehicles and convoys
    - Personnel and formations
    - Weapons and equipment
    - IED indicators
    - Defensive positions
    """
    try:
        logger.info(f"Analyzing tactical image from {request.source}")

        # Validate location if provided
        if request.latitude and request.longitude:
            valid, error = validate_coordinates(request.latitude, request.longitude)
            if not valid:
                raise HTTPException(status_code=400, detail=error)

        # Analyze image
        location = None
        if request.latitude and request.longitude:
            location = {
                "latitude": request.latitude,
                "longitude": request.longitude
            }

        analysis_result = await image_analysis_service.analyze_tactical_image(
            image_data=request.image_data,
            image_url=request.image_url,
            source=request.source,
            location=location
        )

        # Save detected threats to database
        saved_threats = []
        for threat_data in analysis_result.get("threats", []):
            try:
                # Create database record
                threat_db = ThreatDB(
                    threat_type=threat_data.get("threat_type"),
                    threat_level=threat_data.get("threat_level"),
                    confidence=threat_data.get("confidence"),
                    latitude=threat_data.get("latitude") or request.latitude or 0.0,
                    longitude=threat_data.get("longitude") or request.longitude or 0.0,
                    description=threat_data.get("description"),
                    source=threat_data.get("source"),
                    metadata={
                        "reasoning": threat_data.get("reasoning"),
                        "position": threat_data.get("position"),
                        "analysis_result": analysis_result.get("raw_analysis")
                    }
                )
                db.add(threat_db)
                db.commit()
                db.refresh(threat_db)
                saved_threats.append(Threat.model_validate(threat_db))

            except Exception as e:
                logger.error(f"Failed to save threat: {e}")
                db.rollback()

        return {
            "threats": saved_threats,
            "analysis_time": analysis_result.get("analysis_time"),
            "confidence": analysis_result.get("confidence"),
            "source": request.source,
            "total_detected": len(saved_threats)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/predict", response_model=ThreatPredictionResponse)
async def predict_threats(
    request: ThreatPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict potential threats based on historical data and patterns

    Analyzes historical threat data to predict:
    - Likely threat locations
    - Threat types and probabilities
    - Temporal patterns
    - Escalation indicators
    """
    try:
        logger.info(f"Predicting threats for {request.time_horizon_hours}h horizon")

        # Predict threats
        predictions = await threat_predictor_service.predict_threats(
            db=db,
            area_bounds=request.area_bounds,
            time_horizon_hours=request.time_horizon_hours,
            historical_days=request.historical_days,
            threat_types=request.threat_types
        )

        return ThreatPredictionResponse(
            predictions=predictions.get("predictions", []),
            analysis_time=predictions.get("analysis_time"),
            model_version=predictions.get("model_version"),
            factors_considered=predictions.get("factors_considered", [])
        )

    except Exception as e:
        logger.error(f"Threat prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/threats", response_model=List[Threat])
async def get_threats(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    threat_level: Optional[str] = None,
    threat_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of detected threats

    Query parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    - active_only: Only return active threats
    - threat_level: Filter by threat level (low/medium/high/critical)
    - threat_type: Filter by threat type
    """
    try:
        query = db.query(ThreatDB)

        if active_only:
            query = query.filter(ThreatDB.active == True)

        if threat_level:
            query = query.filter(ThreatDB.threat_level == threat_level)

        if threat_type:
            query = query.filter(ThreatDB.threat_type == threat_type)

        threats = query.order_by(ThreatDB.detected_at.desc()).offset(skip).limit(limit).all()

        return [Threat.model_validate(t) for t in threats]

    except Exception as e:
        logger.error(f"Failed to retrieve threats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve threats")


@router.get("/threats/{threat_id}", response_model=Threat)
async def get_threat(threat_id: int, db: Session = Depends(get_db)):
    """Get specific threat by ID"""
    try:
        threat = db.query(ThreatDB).filter(ThreatDB.id == threat_id).first()

        if not threat:
            raise HTTPException(status_code=404, detail="Threat not found")

        return Threat.model_validate(threat)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve threat: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve threat")


@router.patch("/threats/{threat_id}", response_model=Threat)
async def update_threat(
    threat_id: int,
    update: ThreatUpdate,
    db: Session = Depends(get_db)
):
    """
    Update threat information

    Allows updating:
    - Threat level (escalation/de-escalation)
    - Verification status
    - Active status (for resolved threats)
    - Description and metadata
    """
    try:
        threat = db.query(ThreatDB).filter(ThreatDB.id == threat_id).first()

        if not threat:
            raise HTTPException(status_code=404, detail="Threat not found")

        # Update fields
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(threat, field, value)

        db.commit()
        db.refresh(threat)

        return Threat.model_validate(threat)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update threat: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update threat")


@router.delete("/threats/{threat_id}")
async def delete_threat(threat_id: int, db: Session = Depends(get_db)):
    """
    Delete threat (soft delete - marks as inactive)
    """
    try:
        threat = db.query(ThreatDB).filter(ThreatDB.id == threat_id).first()

        if not threat:
            raise HTTPException(status_code=404, detail="Threat not found")

        # Soft delete
        threat.active = False
        db.commit()

        return {"message": "Threat deleted successfully", "threat_id": threat_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete threat: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete threat")


@router.post("/threats", response_model=Threat)
async def create_threat(threat: ThreatCreate, db: Session = Depends(get_db)):
    """
    Manually create threat entry

    For manually reported threats or integration with other systems
    """
    try:
        # Validate coordinates
        valid, error = validate_coordinates(threat.latitude, threat.longitude)
        if not valid:
            raise HTTPException(status_code=400, detail=error)

        # Create threat
        threat_db = ThreatDB(
            threat_type=threat.threat_type.value,
            threat_level=threat.threat_level.value,
            confidence=threat.confidence,
            latitude=threat.latitude,
            longitude=threat.longitude,
            grid_reference=threat.grid_reference,
            description=threat.description,
            source=threat.source.value,
            metadata=threat.metadata,
            image_url=threat.image_url
        )

        db.add(threat_db)
        db.commit()
        db.refresh(threat_db)

        return Threat.model_validate(threat_db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create threat: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create threat")
