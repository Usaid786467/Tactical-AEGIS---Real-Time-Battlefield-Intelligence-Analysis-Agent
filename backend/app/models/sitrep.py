"""
SITREP data models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SitrepPriority(str, Enum):
    """SITREP priority levels"""
    ROUTINE = "routine"
    PRIORITY = "priority"
    IMMEDIATE = "immediate"
    FLASH = "flash"


class SitrepClassification(str, Enum):
    """SITREP classification levels"""
    UNCLASSIFIED = "unclassified"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class SitrepSource(str, Enum):
    """SITREP source types"""
    VOICE = "voice"
    MANUAL = "manual"
    AUTO = "auto"


class Entity(BaseModel):
    """Extracted entity from SITREP"""
    type: str  # location, unit, equipment, personnel, time, etc.
    value: str
    confidence: float = Field(ge=0.0, le=1.0)


class SitrepBase(BaseModel):
    """Base SITREP model"""
    title: str
    location: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    unit: Optional[str] = None
    reporter: Optional[str] = None

    # SITREP sections
    situation: Optional[str] = None
    mission: Optional[str] = None
    execution: Optional[str] = None
    admin_logistics: Optional[str] = None
    command_signal: Optional[str] = None

    priority: SitrepPriority = SitrepPriority.ROUTINE
    classification: SitrepClassification = SitrepClassification.UNCLASSIFIED


class SitrepCreate(SitrepBase):
    """Model for creating a new SITREP"""
    source: SitrepSource = SitrepSource.MANUAL
    audio_transcript: Optional[str] = None


class SitrepUpdate(BaseModel):
    """Model for updating a SITREP"""
    title: Optional[str] = None
    situation: Optional[str] = None
    mission: Optional[str] = None
    execution: Optional[str] = None
    admin_logistics: Optional[str] = None
    command_signal: Optional[str] = None
    priority: Optional[SitrepPriority] = None


class Sitrep(SitrepBase):
    """Complete SITREP model with database fields"""
    id: int
    report_time: datetime
    source: str
    entities: Optional[List[Dict[str, Any]]] = None
    audio_transcript: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VoiceDebriefingRequest(BaseModel):
    """Request model for voice debriefing"""
    audio_data: str  # Base64 encoded audio
    audio_format: str = "wav"  # wav, mp3, ogg
    reporter: Optional[str] = None
    location: Optional[str] = None


class VoiceDebriefingResponse(BaseModel):
    """Response model for voice debriefing"""
    sitrep: Sitrep
    transcript: str
    entities: List[Entity]
    processing_time: float
    confidence: float


class SitrepGenerationRequest(BaseModel):
    """Request model for automated SITREP generation"""
    text_input: str
    include_entities: bool = True
    auto_classify: bool = True


class SitrepGenerationResponse(BaseModel):
    """Response model for automated SITREP generation"""
    sitrep: Sitrep
    entities: List[Entity]
    processing_time: float
