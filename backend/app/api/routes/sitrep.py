"""
SITREP API Routes
Endpoints for situation report generation and management
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.database.database import get_db
from app.database.schemas import SitrepDB
from app.models.sitrep import (
    Sitrep, SitrepCreate, SitrepUpdate,
    VoiceDebriefingRequest, VoiceDebriefingResponse,
    SitrepGenerationRequest, SitrepGenerationResponse
)
from app.services.nlp_service import nlp_service
from app.utils.audio_processor import audio_processor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=SitrepGenerationResponse)
async def generate_sitrep(
    request: SitrepGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate structured SITREP from unstructured text

    Automatically structures raw text input into a formal SITREP format:
    - SITUATION: Current tactical situation
    - MISSION: Mission or objective
    - EXECUTION: Actions taken or planned
    - ADMIN/LOGISTICS: Administrative notes
    - COMMAND/SIGNAL: Command and communications info

    Also extracts entities (locations, units, equipment, etc.)
    """
    try:
        logger.info("Generating SITREP from text input")

        # Generate SITREP using NLP service
        sitrep_data = await nlp_service.generate_sitrep_from_text(
            input_text=request.text_input,
            location=None,
            unit=None,
            reporter=None
        )

        # Create database record
        sitrep_db = SitrepDB(
            title=sitrep_data.get("title"),
            situation=sitrep_data.get("situation"),
            mission=sitrep_data.get("mission"),
            execution=sitrep_data.get("execution"),
            admin_logistics=sitrep_data.get("admin_logistics"),
            command_signal=sitrep_data.get("command_signal"),
            priority=sitrep_data.get("priority"),
            classification=sitrep_data.get("classification"),
            source="auto",
            entities=sitrep_data.get("entities"),
            metadata={
                "key_points": sitrep_data.get("key_points"),
                "processing_time": sitrep_data.get("processing_time")
            }
        )

        db.add(sitrep_db)
        db.commit()
        db.refresh(sitrep_db)

        return SitrepGenerationResponse(
            sitrep=Sitrep.model_validate(sitrep_db),
            entities=sitrep_data.get("entities", []),
            processing_time=sitrep_data.get("processing_time", 0)
        )

    except Exception as e:
        logger.error(f"SITREP generation failed: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"SITREP generation failed: {str(e)}")


@router.post("/voice-debrief", response_model=VoiceDebriefingResponse)
async def voice_debriefing(
    request: VoiceDebriefingRequest,
    db: Session = Depends(get_db)
):
    """
    Process voice debriefing and generate SITREP

    Workflow:
    1. Transcribe audio to text
    2. Process transcript with NLP
    3. Extract entities and key information
    4. Generate structured SITREP
    5. Store in database

    Supports audio formats: WAV, MP3, OGG
    """
    try:
        logger.info(f"Processing voice debriefing from {request.reporter or 'unknown'}")

        # Transcribe audio
        transcription = await audio_processor.transcribe_audio(
            audio_data=request.audio_data,
            audio_format=request.audio_format
        )

        transcript = transcription.get("transcript")
        logger.info(f"Transcription complete: {len(transcript)} characters")

        # Process transcript and generate SITREP
        sitrep_data = await nlp_service.process_voice_debriefing(
            transcript=transcript,
            reporter=request.reporter,
            location=request.location
        )

        # Create database record
        sitrep_db = SitrepDB(
            title=sitrep_data.get("title"),
            location=request.location or sitrep_data.get("location"),
            reporter=request.reporter,
            situation=sitrep_data.get("situation"),
            mission=sitrep_data.get("mission"),
            execution=sitrep_data.get("execution"),
            admin_logistics=sitrep_data.get("admin_logistics"),
            command_signal=sitrep_data.get("command_signal"),
            priority=sitrep_data.get("priority"),
            classification=sitrep_data.get("classification"),
            source="voice",
            audio_transcript=transcript,
            entities=sitrep_data.get("entities"),
            metadata={
                "key_points": sitrep_data.get("key_points"),
                "confidence": sitrep_data.get("confidence"),
                "processing_time": sitrep_data.get("processing_time"),
                "transcription_confidence": transcription.get("confidence")
            }
        )

        db.add(sitrep_db)
        db.commit()
        db.refresh(sitrep_db)

        return VoiceDebriefingResponse(
            sitrep=Sitrep.model_validate(sitrep_db),
            transcript=transcript,
            entities=sitrep_data.get("entities", []),
            processing_time=sitrep_data.get("processing_time", 0),
            confidence=sitrep_data.get("confidence", 0.8)
        )

    except Exception as e:
        logger.error(f"Voice debriefing failed: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Voice debriefing failed: {str(e)}")


@router.get("/sitreps", response_model=List[Sitrep])
async def get_sitreps(
    skip: int = 0,
    limit: int = 50,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of SITREPs

    Query parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    - priority: Filter by priority (routine/priority/immediate/flash)
    - source: Filter by source (voice/manual/auto)
    """
    try:
        query = db.query(SitrepDB)

        if priority:
            query = query.filter(SitrepDB.priority == priority)

        if source:
            query = query.filter(SitrepDB.source == source)

        sitreps = query.order_by(SitrepDB.report_time.desc()).offset(skip).limit(limit).all()

        return [Sitrep.model_validate(s) for s in sitreps]

    except Exception as e:
        logger.error(f"Failed to retrieve SITREPs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SITREPs")


@router.get("/sitreps/{sitrep_id}", response_model=Sitrep)
async def get_sitrep(sitrep_id: int, db: Session = Depends(get_db)):
    """Get specific SITREP by ID"""
    try:
        sitrep = db.query(SitrepDB).filter(SitrepDB.id == sitrep_id).first()

        if not sitrep:
            raise HTTPException(status_code=404, detail="SITREP not found")

        return Sitrep.model_validate(sitrep)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve SITREP: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SITREP")


@router.post("/sitreps", response_model=Sitrep)
async def create_sitrep(sitrep: SitrepCreate, db: Session = Depends(get_db)):
    """
    Manually create SITREP

    For manually entered situation reports
    """
    try:
        sitrep_db = SitrepDB(
            title=sitrep.title,
            location=sitrep.location,
            latitude=sitrep.latitude,
            longitude=sitrep.longitude,
            unit=sitrep.unit,
            reporter=sitrep.reporter,
            situation=sitrep.situation,
            mission=sitrep.mission,
            execution=sitrep.execution,
            admin_logistics=sitrep.admin_logistics,
            command_signal=sitrep.command_signal,
            priority=sitrep.priority.value,
            classification=sitrep.classification.value,
            source=sitrep.source.value,
            audio_transcript=sitrep.audio_transcript
        )

        db.add(sitrep_db)
        db.commit()
        db.refresh(sitrep_db)

        return Sitrep.model_validate(sitrep_db)

    except Exception as e:
        logger.error(f"Failed to create SITREP: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create SITREP")


@router.patch("/sitreps/{sitrep_id}", response_model=Sitrep)
async def update_sitrep(
    sitrep_id: int,
    update: SitrepUpdate,
    db: Session = Depends(get_db)
):
    """
    Update SITREP information

    Allows updating any SITREP field
    """
    try:
        sitrep = db.query(SitrepDB).filter(SitrepDB.id == sitrep_id).first()

        if not sitrep:
            raise HTTPException(status_code=404, detail="SITREP not found")

        # Update fields
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(sitrep, field):
                setattr(sitrep, field, value)

        db.commit()
        db.refresh(sitrep)

        return Sitrep.model_validate(sitrep)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update SITREP: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update SITREP")


@router.delete("/sitreps/{sitrep_id}")
async def delete_sitrep(sitrep_id: int, db: Session = Depends(get_db)):
    """Delete SITREP"""
    try:
        sitrep = db.query(SitrepDB).filter(SitrepDB.id == sitrep_id).first()

        if not sitrep:
            raise HTTPException(status_code=404, detail="SITREP not found")

        db.delete(sitrep)
        db.commit()

        return {"message": "SITREP deleted successfully", "sitrep_id": sitrep_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete SITREP: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete SITREP")
