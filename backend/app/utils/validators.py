"""
Input Validation Utilities
"""

import re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
    """
    Validate latitude and longitude coordinates

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(latitude, (int, float)):
        return False, "Latitude must be a number"

    if not isinstance(longitude, (int, float)):
        return False, "Longitude must be a number"

    if not -90 <= latitude <= 90:
        return False, f"Latitude must be between -90 and 90, got {latitude}"

    if not -180 <= longitude <= 180:
        return False, f"Longitude must be between -180 and 180, got {longitude}"

    return True, None


def validate_mgrs(mgrs: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Military Grid Reference System coordinate

    Args:
        mgrs: MGRS coordinate string

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Basic MGRS pattern: 2-digit zone, letter, 2-letter square, 10 digits
    pattern = r'^\d{1,2}[A-Z]{3}\d{4,10}$'

    if not isinstance(mgrs, str):
        return False, "MGRS must be a string"

    mgrs_clean = mgrs.replace(' ', '').upper()

    if not re.match(pattern, mgrs_clean):
        return False, "Invalid MGRS format"

    return True, None


def validate_confidence(confidence: float) -> Tuple[bool, Optional[str]]:
    """
    Validate confidence score

    Args:
        confidence: Confidence value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(confidence, (int, float)):
        return False, "Confidence must be a number"

    if not 0 <= confidence <= 1:
        return False, f"Confidence must be between 0 and 1, got {confidence}"

    return True, None


def validate_unit_id(unit_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate unit ID format

    Args:
        unit_id: Unit identifier

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(unit_id, str):
        return False, "Unit ID must be a string"

    if len(unit_id) < 3:
        return False, "Unit ID must be at least 3 characters"

    if len(unit_id) > 50:
        return False, "Unit ID must be at most 50 characters"

    # Allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[A-Za-z0-9_-]+$', unit_id):
        return False, "Unit ID can only contain letters, numbers, hyphens, and underscores"

    return True, None


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text input

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""

    # Remove null bytes
    text = text.replace('\x00', '')

    # Limit length
    text = text[:max_length]

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def validate_time_range(hours: int, min_hours: int = 1, max_hours: int = 168) -> Tuple[bool, Optional[str]]:
    """
    Validate time range in hours

    Args:
        hours: Number of hours
        min_hours: Minimum allowed hours
        max_hours: Maximum allowed hours

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(hours, int):
        return False, "Hours must be an integer"

    if hours < min_hours:
        return False, f"Hours must be at least {min_hours}"

    if hours > max_hours:
        return False, f"Hours must be at most {max_hours}"

    return True, None


def validate_area_bounds(bounds: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate geographic area bounds

    Args:
        bounds: Dictionary with north, south, east, west keys

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_keys = ["north", "south", "east", "west"]

    for key in required_keys:
        if key not in bounds:
            return False, f"Missing required key: {key}"

    # Validate coordinates
    valid, error = validate_coordinates(bounds["north"], bounds["east"])
    if not valid:
        return False, f"Invalid north-east corner: {error}"

    valid, error = validate_coordinates(bounds["south"], bounds["west"])
    if not valid:
        return False, f"Invalid south-west corner: {error}"

    # Check bounds make sense
    if bounds["north"] <= bounds["south"]:
        return False, "North boundary must be greater than south boundary"

    # East-West is more complex due to wrapping, but basic check
    if bounds["east"] == bounds["west"]:
        return False, "East and west boundaries cannot be the same"

    return True, None


def validate_threat_level(level: str) -> Tuple[bool, Optional[str]]:
    """
    Validate threat level

    Args:
        level: Threat level string

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_levels = ["low", "medium", "high", "critical"]

    if not isinstance(level, str):
        return False, "Threat level must be a string"

    if level.lower() not in valid_levels:
        return False, f"Threat level must be one of: {', '.join(valid_levels)}"

    return True, None


def validate_threat_type(threat_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate threat type

    Args:
        threat_type: Threat type string

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_types = ["vehicle", "personnel", "weapon", "ied", "artillery", "aircraft", "unknown"]

    if not isinstance(threat_type, str):
        return False, "Threat type must be a string"

    if threat_type.lower() not in valid_types:
        return False, f"Threat type must be one of: {', '.join(valid_types)}"

    return True, None
