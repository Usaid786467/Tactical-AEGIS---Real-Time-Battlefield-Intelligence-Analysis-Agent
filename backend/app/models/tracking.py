"""
Friendly force tracking data models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class UnitType(str, Enum):
    """Unit type enumeration"""
    INFANTRY = "infantry"
    ARMOR = "armor"
    AVIATION = "aviation"
    ARTILLERY = "artillery"
    LOGISTICS = "logistics"
    COMMAND = "command"
    SPECIAL_FORCES = "special_forces"
    OTHER = "other"


class UnitStatus(str, Enum):
    """Unit status enumeration"""
    GREEN = "green"  # Fully operational
    AMBER = "amber"  # Reduced capability
    RED = "red"  # Significantly degraded
    BLACK = "black"  # Combat ineffective


class FriendlyForceBase(BaseModel):
    """Base friendly force model"""
    unit_id: str
    unit_name: str
    unit_type: Optional[UnitType] = None
    callsign: Optional[str] = None

    # Position
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude: Optional[float] = None
    heading: Optional[float] = Field(None, ge=0, le=360)
    speed: Optional[float] = Field(None, ge=0)

    # Status
    status: UnitStatus = UnitStatus.GREEN
    personnel_count: Optional[int] = None
    equipment: Optional[Dict[str, Any]] = None


class FriendlyForceCreate(FriendlyForceBase):
    """Model for creating/updating a friendly force"""
    pass


class FriendlyForceUpdate(BaseModel):
    """Model for updating friendly force position/status"""
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    altitude: Optional[float] = None
    heading: Optional[float] = Field(None, ge=0, le=360)
    speed: Optional[float] = Field(None, ge=0)
    status: Optional[UnitStatus] = None
    personnel_count: Optional[int] = None
    equipment: Optional[Dict[str, Any]] = None


class FriendlyForce(FriendlyForceBase):
    """Complete friendly force model with database fields"""
    id: int
    last_contact: datetime
    metadata: Optional[Dict[str, Any]] = None
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrackingUpdate(BaseModel):
    """Real-time tracking update"""
    unit_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    heading: Optional[float] = None
    speed: Optional[float] = None


class ProximityAlert(BaseModel):
    """Proximity alert for blue-on-blue prevention"""
    alert_type: str  # "proximity", "crossing", "collision_course"
    unit1_id: str
    unit2_id: str
    distance: float  # meters
    time_to_closest: Optional[float] = None  # seconds
    severity: str  # "low", "medium", "high"
    message: str


class BlueonBlueCheck(BaseModel):
    """Blue-on-blue incident check"""
    target_latitude: float
    target_longitude: float
    radius: float = Field(default=1000, ge=0)  # meters


class BlueonBlueResponse(BaseModel):
    """Response for blue-on-blue check"""
    safe: bool
    nearby_units: List[Dict[str, Any]]
    minimum_distance: float
    alerts: List[ProximityAlert]


class DeploymentOptimization(BaseModel):
    """Request for deployment optimization"""
    available_units: List[str]  # unit_ids
    objective_location: Dict[str, float]  # {latitude, longitude}
    mission_type: str
    time_critical: bool = False


class DeploymentRecommendation(BaseModel):
    """Deployment recommendation"""
    unit_id: str
    recommended_route: List[Dict[str, float]]  # waypoints
    estimated_time: float  # minutes
    reasoning: str
    priority: int
