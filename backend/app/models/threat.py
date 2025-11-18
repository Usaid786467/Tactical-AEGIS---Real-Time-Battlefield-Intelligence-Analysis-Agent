"""
Threat data models for API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ThreatLevel(str, Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(str, Enum):
    """Threat type enumeration"""
    VEHICLE = "vehicle"
    PERSONNEL = "personnel"
    WEAPON = "weapon"
    IED = "ied"
    ARTILLERY = "artillery"
    AIRCRAFT = "aircraft"
    UNKNOWN = "unknown"


class ThreatSource(str, Enum):
    """Data source enumeration"""
    SATELLITE = "satellite"
    DRONE = "drone"
    SENSOR = "sensor"
    RADIO = "radio"
    MANUAL = "manual"


class ThreatBase(BaseModel):
    """Base threat model"""
    threat_type: ThreatType
    threat_level: ThreatLevel
    confidence: float = Field(ge=0.0, le=1.0)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    grid_reference: Optional[str] = None
    description: Optional[str] = None
    source: ThreatSource
    metadata: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None


class ThreatCreate(ThreatBase):
    """Model for creating a new threat"""
    pass


class ThreatUpdate(BaseModel):
    """Model for updating a threat"""
    threat_level: Optional[ThreatLevel] = None
    verified: Optional[bool] = None
    active: Optional[bool] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Threat(ThreatBase):
    """Complete threat model with database fields"""
    id: int
    detected_at: datetime
    verified: bool
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ThreatAnalysisRequest(BaseModel):
    """Request model for threat analysis"""
    image_data: Optional[str] = None  # Base64 encoded image
    image_url: Optional[str] = None
    text_data: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: ThreatSource

    @validator('image_data', 'image_url')
    def check_image_provided(cls, v, values):
        """Ensure at least one data source is provided"""
        if not any([v, values.get('text_data'), values.get('audio_data')]):
            raise ValueError("At least one data source must be provided")
        return v


class ThreatAnalysisResponse(BaseModel):
    """Response model for threat analysis"""
    threats: List[Threat]
    analysis_time: float
    confidence: float
    raw_analysis: Optional[Dict[str, Any]] = None


class ThreatPredictionRequest(BaseModel):
    """Request model for threat prediction"""
    area_bounds: Dict[str, float]  # {north, south, east, west}
    time_horizon_hours: int = Field(ge=1, le=72, default=24)
    historical_days: int = Field(ge=1, le=90, default=7)
    threat_types: Optional[List[ThreatType]] = None


class PredictedThreat(BaseModel):
    """Predicted threat model"""
    threat_type: ThreatType
    latitude: float
    longitude: float
    probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    predicted_time: Optional[datetime] = None


class ThreatPredictionResponse(BaseModel):
    """Response model for threat prediction"""
    predictions: List[PredictedThreat]
    analysis_time: float
    model_version: str
    factors_considered: List[str]
