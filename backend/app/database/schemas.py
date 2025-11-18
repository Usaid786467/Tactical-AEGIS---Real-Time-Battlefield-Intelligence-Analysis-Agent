"""
Database Schema Definitions
SQLAlchemy ORM models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database.database import Base


class ThreatLevel(str, enum.Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(str, enum.Enum):
    """Threat type enumeration"""
    VEHICLE = "vehicle"
    PERSONNEL = "personnel"
    WEAPON = "weapon"
    IED = "ied"
    ARTILLERY = "artillery"
    AIRCRAFT = "aircraft"
    UNKNOWN = "unknown"


class ThreatDB(Base):
    """Threat detection database model"""
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    threat_type = Column(String, nullable=False)
    threat_level = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    grid_reference = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=False)  # satellite, drone, sensor, radio
    metadata = Column(JSON, nullable=True)
    image_url = Column(String, nullable=True)
    detected_at = Column(DateTime, default=func.now())
    verified = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SitrepDB(Base):
    """Situation Report database model"""
    __tablename__ = "sitreps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    report_time = Column(DateTime, default=func.now())
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    reporter = Column(String, nullable=True)

    # SITREP sections
    situation = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    execution = Column(Text, nullable=True)
    admin_logistics = Column(Text, nullable=True)
    command_signal = Column(Text, nullable=True)

    # Extracted entities
    entities = Column(JSON, nullable=True)  # locations, units, equipment, etc.

    # Metadata
    source = Column(String, default="voice")  # voice, manual, auto
    audio_transcript = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    priority = Column(String, default="routine")  # routine, priority, immediate, flash
    classification = Column(String, default="unclassified")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class FriendlyForceDB(Base):
    """Friendly force tracking database model"""
    __tablename__ = "friendly_forces"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(String, unique=True, nullable=False, index=True)
    unit_name = Column(String, nullable=False)
    unit_type = Column(String, nullable=True)  # infantry, armor, aviation, etc.
    callsign = Column(String, nullable=True)

    # Position
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)

    # Status
    status = Column(String, default="green")  # green, amber, red, black
    personnel_count = Column(Integer, nullable=True)
    equipment = Column(JSON, nullable=True)

    # Metadata
    last_contact = Column(DateTime, default=func.now())
    metadata = Column(JSON, nullable=True)

    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class DataSourceDB(Base):
    """Data source tracking model"""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, unique=True, nullable=False, index=True)
    source_type = Column(String, nullable=False)  # satellite, drone, sensor, radio
    source_name = Column(String, nullable=False)

    # Status
    status = Column(String, default="active")  # active, inactive, error
    last_update = Column(DateTime, default=func.now())

    # Coverage area
    coverage_area = Column(JSON, nullable=True)  # GeoJSON polygon

    # Metadata
    metadata = Column(JSON, nullable=True)

    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AnalysisJobDB(Base):
    """Analysis job tracking model"""
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, nullable=False, index=True)
    job_type = Column(String, nullable=False)  # image, audio, text, prediction

    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)

    # Input/Output
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Metadata
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
