"""
Data Fusion API Routes
Endpoints for multi-source intelligence fusion and tactical picture generation
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from app.database.database import get_db
from app.database.schemas import ThreatDB, FriendlyForceDB
from app.models.threat import Threat
from app.models.tracking import FriendlyForce
from app.utils.data_fusion import data_fusion_engine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tactical-picture")
async def get_tactical_picture(
    north: Optional[float] = None,
    south: Optional[float] = None,
    east: Optional[float] = None,
    west: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive tactical picture

    Fuses data from multiple sources to create a unified view:
    - Threat detections (all sources)
    - Friendly force positions
    - Situation assessment
    - Tactical recommendations

    Optional area bounds filtering (north, south, east, west coordinates)
    """
    try:
        logger.info("Generating tactical picture")

        # Build query for threats
        threat_query = db.query(ThreatDB).filter(ThreatDB.active == True)

        # Apply area bounds if provided
        if all([north, south, east, west]):
            threat_query = threat_query.filter(
                ThreatDB.latitude >= south,
                ThreatDB.latitude <= north,
                ThreatDB.longitude >= west,
                ThreatDB.longitude <= east
            )

        threats = threat_query.all()

        # Build query for friendly forces
        force_query = db.query(FriendlyForceDB).filter(FriendlyForceDB.active == True)

        if all([north, south, east, west]):
            force_query = force_query.filter(
                FriendlyForceDB.latitude >= south,
                FriendlyForceDB.latitude <= north,
                FriendlyForceDB.longitude >= west,
                FriendlyForceDB.longitude <= east
            )

        forces = force_query.all()

        # Convert to dictionaries for fusion engine
        threat_dicts = [
            {
                "id": t.id,
                "threat_type": t.threat_type,
                "threat_level": t.threat_level,
                "confidence": t.confidence,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "description": t.description,
                "source": t.source,
                "detected_at": t.detected_at,
                "verified": t.verified
            }
            for t in threats
        ]

        force_dicts = [
            {
                "unit_id": f.unit_id,
                "unit_name": f.unit_name,
                "unit_type": f.unit_type,
                "callsign": f.callsign,
                "latitude": f.latitude,
                "longitude": f.longitude,
                "status": f.status,
                "last_contact": f.last_contact
            }
            for f in forces
        ]

        # Create area bounds if provided
        area_bounds = None
        if all([north, south, east, west]):
            area_bounds = {
                "north": north,
                "south": south,
                "east": east,
                "west": west
            }

        # Generate tactical picture
        tactical_picture = data_fusion_engine.create_tactical_picture(
            threats=threat_dicts,
            friendly_forces=force_dicts,
            area_bounds=area_bounds
        )

        logger.info(f"Tactical picture generated with {len(threat_dicts)} threats and {len(force_dicts)} forces")

        return tactical_picture

    except Exception as e:
        logger.error(f"Failed to generate tactical picture: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate tactical picture: {str(e)}")


@router.post("/fuse-threats")
async def fuse_threat_data(
    correlation_radius_km: float = 0.5,
    time_window_hours: float = 1.0,
    db: Session = Depends(get_db)
):
    """
    Fuse threat detections from multiple sources

    Correlates threats that are:
    - Spatially close (within correlation_radius_km)
    - Temporally close (within time_window_hours)
    - Of the same type

    Returns fused threat data with increased confidence
    """
    try:
        logger.info(f"Fusing threats with {correlation_radius_km}km radius, {time_window_hours}h window")

        # Get all active threats
        threats = db.query(ThreatDB).filter(ThreatDB.active == True).all()

        # Convert to dictionaries
        threat_dicts = [
            {
                "id": t.id,
                "threat_type": t.threat_type,
                "threat_level": t.threat_level,
                "confidence": t.confidence,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "description": t.description,
                "source": t.source,
                "detected_at": t.detected_at
            }
            for t in threats
        ]

        # Fuse threats
        fused_threats = data_fusion_engine.fuse_threat_data(
            threats=threat_dicts,
            correlation_radius_km=correlation_radius_km,
            time_window_hours=time_window_hours
        )

        logger.info(f"Fused {len(threat_dicts)} threats into {len(fused_threats)} correlated detections")

        return {
            "original_count": len(threat_dicts),
            "fused_count": len(fused_threats),
            "reduction": len(threat_dicts) - len(fused_threats),
            "fused_threats": fused_threats
        }

    except Exception as e:
        logger.error(f"Threat fusion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Threat fusion failed: {str(e)}")


@router.get("/situation-assessment")
async def get_situation_assessment(
    north: Optional[float] = None,
    south: Optional[float] = None,
    east: Optional[float] = None,
    west: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get situation assessment for area of operations

    Provides:
    - Overall threat status (low/moderate/elevated/critical)
    - Threat distribution analysis
    - Force positioning analysis
    - Units at risk
    - Tactical recommendations
    """
    try:
        # Get tactical picture
        tactical_picture = await get_tactical_picture(
            north=north,
            south=south,
            east=east,
            west=west,
            db=db
        )

        # Extract situation assessment
        situation = tactical_picture.get("situation_assessment", {})

        return {
            "status": situation.get("status"),
            "summary": situation.get("summary"),
            "threat_count": situation.get("threat_count"),
            "units_at_risk": situation.get("units_at_risk"),
            "avg_threat_level": situation.get("avg_threat_level"),
            "recommendations": tactical_picture.get("recommendations", []),
            "timestamp": tactical_picture.get("timestamp")
        }

    except Exception as e:
        logger.error(f"Situation assessment failed: {e}")
        raise HTTPException(status_code=500, detail="Situation assessment failed")


@router.get("/threat-distribution")
async def get_threat_distribution(db: Session = Depends(get_db)):
    """
    Analyze threat distribution

    Provides statistics on:
    - Threats by type
    - Threats by level
    - Source reliability
    - Geographic distribution
    """
    try:
        threats = db.query(ThreatDB).filter(ThreatDB.active == True).all()

        # Analyze distribution
        by_type = {}
        by_level = {}
        by_source = {}

        for threat in threats:
            # By type
            by_type[threat.threat_type] = by_type.get(threat.threat_type, 0) + 1

            # By level
            by_level[threat.threat_level] = by_level.get(threat.threat_level, 0) + 1

            # By source
            by_source[threat.source] = by_source.get(threat.source, 0) + 1

        # Calculate averages
        total = len(threats)
        avg_confidence = sum(t.confidence for t in threats) / total if total > 0 else 0

        return {
            "total_threats": total,
            "by_type": by_type,
            "by_level": by_level,
            "by_source": by_source,
            "avg_confidence": avg_confidence,
            "verified_count": sum(1 for t in threats if t.verified),
            "unverified_count": sum(1 for t in threats if not t.verified)
        }

    except Exception as e:
        logger.error(f"Threat distribution analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Threat distribution analysis failed")


@router.get("/force-disposition")
async def get_force_disposition(db: Session = Depends(get_db)):
    """
    Analyze friendly force disposition

    Provides statistics on:
    - Units by status
    - Units by type
    - Geographic distribution
    - Combat readiness
    """
    try:
        forces = db.query(FriendlyForceDB).filter(FriendlyForceDB.active == True).all()

        # Analyze disposition
        by_status = {}
        by_type = {}

        for force in forces:
            # By status
            by_status[force.status] = by_status.get(force.status, 0) + 1

            # By type
            if force.unit_type:
                by_type[force.unit_type] = by_type.get(force.unit_type, 0) + 1

        # Calculate totals
        total = len(forces)
        total_personnel = sum(f.personnel_count or 0 for f in forces)

        # Combat readiness (based on status)
        green_count = by_status.get("green", 0)
        readiness_percentage = (green_count / total * 100) if total > 0 else 0

        return {
            "total_units": total,
            "total_personnel": total_personnel,
            "by_status": by_status,
            "by_type": by_type,
            "combat_readiness": readiness_percentage,
            "units_at_full_strength": green_count,
            "units_degraded": by_status.get("amber", 0) + by_status.get("red", 0)
        }

    except Exception as e:
        logger.error(f"Force disposition analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Force disposition analysis failed")


@router.get("/intelligence-summary")
async def get_intelligence_summary(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Generate intelligence summary for time period

    Provides comprehensive intelligence overview:
    - Recent threat activity
    - Trends and patterns
    - Force movements
    - Key events
    """
    try:
        from datetime import datetime, timedelta

        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)

        # Get recent threats
        recent_threats = db.query(ThreatDB).filter(
            ThreatDB.detected_at >= time_threshold,
            ThreatDB.active == True
        ).all()

        # Get force updates
        recent_force_updates = db.query(FriendlyForceDB).filter(
            FriendlyForceDB.last_contact >= time_threshold,
            FriendlyForceDB.active == True
        ).all()

        # Analyze trends
        threat_trend = "increasing" if len(recent_threats) > 10 else "stable" if len(recent_threats) > 5 else "decreasing"

        # High priority items
        critical_threats = [t for t in recent_threats if t.threat_level == "critical"]
        high_threats = [t for t in recent_threats if t.threat_level == "high"]

        return {
            "period_hours": hours,
            "summary": {
                "total_threats_detected": len(recent_threats),
                "critical_threats": len(critical_threats),
                "high_priority_threats": len(high_threats),
                "threat_trend": threat_trend,
                "force_updates": len(recent_force_updates)
            },
            "key_events": [
                {
                    "type": "threat",
                    "level": t.threat_level,
                    "description": t.description,
                    "detected_at": t.detected_at,
                    "source": t.source
                }
                for t in (critical_threats + high_threats)[:10]  # Top 10 priority threats
            ],
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Intelligence summary generation failed: {e}")
        raise HTTPException(status_code=500, detail="Intelligence summary generation failed")
