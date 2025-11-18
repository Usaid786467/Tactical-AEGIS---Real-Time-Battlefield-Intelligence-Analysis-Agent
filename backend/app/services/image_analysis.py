"""
Image Analysis Service
Analyzes satellite and drone imagery for threat detection
"""

import logging
from typing import Dict, Any, List, Optional
import time
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np

from app.services.gemini_service import gemini_service
from app.models.threat import ThreatType, ThreatLevel, ThreatSource

logger = logging.getLogger(__name__)


class ImageAnalysisService:
    """Service for analyzing tactical imagery"""

    def __init__(self):
        """Initialize image analysis service"""
        self.gemini = gemini_service
        logger.info("Image analysis service initialized")

    async def analyze_tactical_image(
        self,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        source: ThreatSource = ThreatSource.SATELLITE,
        location: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze tactical image for threats

        Args:
            image_data: Base64 encoded image
            image_url: URL to image
            source: Source of image (satellite, drone, etc.)
            location: Optional location data {latitude, longitude}

        Returns:
            Analysis results with detected threats
        """
        try:
            start_time = time.time()

            # Pre-process image if needed
            if image_data:
                processed_image = await self._preprocess_image(image_data)
            else:
                processed_image = image_data

            # Analyze with Gemini
            analysis = await self.gemini.analyze_image(
                image_data=processed_image,
                image_url=image_url,
                prompt=self._get_analysis_prompt(source)
            )

            # Process and structure results
            threats = await self._extract_threats(
                analysis,
                source,
                location
            )

            analysis_time = time.time() - start_time

            return {
                "threats": threats,
                "analysis_time": analysis_time,
                "source": source,
                "raw_analysis": analysis.get("parsed_analysis"),
                "confidence": self._calculate_overall_confidence(threats)
            }

        except Exception as e:
            logger.error(f"Tactical image analysis failed: {e}")
            raise

    def _get_analysis_prompt(self, source: ThreatSource) -> str:
        """Get appropriate analysis prompt based on source"""
        base_prompt = """
Analyze this tactical image for military threats and intelligence.

Identify and report:
1. VEHICLES: Military vehicles, trucks, armor, artillery
   - Type and approximate count
   - Activity/status (moving, stationary, deployed)
   - Threat level

2. PERSONNEL: Groups of people, formations
   - Approximate count
   - Activity (patrolling, stationary, moving)
   - Armed/unarmed if visible

3. EQUIPMENT: Weapons, installations, structures
   - Type of equipment
   - Deployment status

4. SUSPICIOUS ACTIVITY:
   - IED indicators (disturbed earth, unusual objects)
   - Ambush positions
   - Defensive positions

5. INFRASTRUCTURE:
   - Buildings
   - Roads and bridges
   - Checkpoints

For each detection, provide:
- Type (vehicle/personnel/weapon/ied/artillery/aircraft)
- Description
- Threat level (low/medium/high/critical)
- Confidence (0.0 to 1.0)
- Position in image (approximate coordinates or description)
- Reasoning for threat assessment
"""

        if source == ThreatSource.SATELLITE:
            return base_prompt + """
\nNote: This is satellite imagery. Focus on larger features and patterns.
Look for vehicle convoys, troop concentrations, equipment staging areas.
"""
        elif source == ThreatSource.DRONE:
            return base_prompt + """
\nNote: This is drone imagery. Analyze with higher detail.
Can identify individual vehicles, personnel, and smaller equipment.
"""
        else:
            return base_prompt

    async def _preprocess_image(self, image_data: str) -> str:
        """
        Pre-process image for better analysis

        Args:
            image_data: Base64 encoded image

        Returns:
            Processed base64 encoded image
        """
        try:
            # Decode image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))

            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)

            # Apply enhancements
            # 1. Contrast enhancement
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

            # 2. Sharpening
            kernel = np.array([[-1, -1, -1],
                               [-1, 9, -1],
                               [-1, -1, -1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)

            # Convert back to PIL Image
            processed_image = Image.fromarray(sharpened)

            # Encode back to base64
            buffered = BytesIO()
            processed_image.save(buffered, format="PNG")
            processed_data = base64.b64encode(buffered.getvalue()).decode()

            return processed_data

        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image_data

    async def _extract_threats(
        self,
        analysis: Dict[str, Any],
        source: ThreatSource,
        location: Optional[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """
        Extract structured threat data from analysis

        Args:
            analysis: Gemini analysis result
            source: Image source
            location: Optional location data

        Returns:
            List of threat dictionaries
        """
        threats = []

        try:
            parsed = analysis.get("parsed_analysis")
            if not parsed or "threats" not in parsed:
                logger.warning("No structured threats found in analysis")
                return threats

            for threat_data in parsed["threats"]:
                threat = {
                    "threat_type": self._normalize_threat_type(threat_data.get("type")),
                    "threat_level": self._normalize_threat_level(threat_data.get("threat_level")),
                    "confidence": float(threat_data.get("confidence", 0.5)),
                    "description": threat_data.get("description", ""),
                    "reasoning": threat_data.get("reasoning", ""),
                    "position": threat_data.get("position", ""),
                    "source": source
                }

                # Add location if provided
                if location:
                    threat["latitude"] = location.get("latitude")
                    threat["longitude"] = location.get("longitude")

                # Only include threats above confidence threshold
                if threat["confidence"] >= 0.3:
                    threats.append(threat)

        except Exception as e:
            logger.error(f"Failed to extract threats: {e}")

        return threats

    def _normalize_threat_type(self, threat_type: str) -> str:
        """Normalize threat type string to enum value"""
        if not threat_type:
            return ThreatType.UNKNOWN.value

        threat_type_lower = threat_type.lower()

        if "vehicle" in threat_type_lower or "truck" in threat_type_lower or "armor" in threat_type_lower:
            return ThreatType.VEHICLE.value
        elif "person" in threat_type_lower or "personnel" in threat_type_lower or "troop" in threat_type_lower:
            return ThreatType.PERSONNEL.value
        elif "weapon" in threat_type_lower or "gun" in threat_type_lower or "rifle" in threat_type_lower:
            return ThreatType.WEAPON.value
        elif "ied" in threat_type_lower or "explosive" in threat_type_lower or "bomb" in threat_type_lower:
            return ThreatType.IED.value
        elif "artillery" in threat_type_lower or "mortar" in threat_type_lower or "launcher" in threat_type_lower:
            return ThreatType.ARTILLERY.value
        elif "aircraft" in threat_type_lower or "helicopter" in threat_type_lower or "drone" in threat_type_lower:
            return ThreatType.AIRCRAFT.value
        else:
            return ThreatType.UNKNOWN.value

    def _normalize_threat_level(self, threat_level: str) -> str:
        """Normalize threat level string to enum value"""
        if not threat_level:
            return ThreatLevel.MEDIUM.value

        threat_level_lower = threat_level.lower()

        if "critical" in threat_level_lower:
            return ThreatLevel.CRITICAL.value
        elif "high" in threat_level_lower:
            return ThreatLevel.HIGH.value
        elif "medium" in threat_level_lower or "moderate" in threat_level_lower:
            return ThreatLevel.MEDIUM.value
        elif "low" in threat_level_lower:
            return ThreatLevel.LOW.value
        else:
            return ThreatLevel.MEDIUM.value

    def _calculate_overall_confidence(self, threats: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence from threat list"""
        if not threats:
            return 0.0

        confidences = [t.get("confidence", 0.0) for t in threats]
        return sum(confidences) / len(confidences)

    async def detect_changes(
        self,
        image1_data: str,
        image2_data: str,
        time_delta: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Detect changes between two images (before/after analysis)

        Args:
            image1_data: Base64 encoded first image
            image2_data: Base64 encoded second image
            time_delta: Time between images in hours

        Returns:
            Change detection results
        """
        try:
            # Decode images
            img1_bytes = base64.b64decode(image1_data)
            img2_bytes = base64.b64decode(image2_data)

            img1 = cv2.imdecode(np.frombuffer(img1_bytes, np.uint8), cv2.IMREAD_COLOR)
            img2 = cv2.imdecode(np.frombuffer(img2_bytes, np.uint8), cv2.IMREAD_COLOR)

            # Resize to same dimensions if needed
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            # Compute difference
            diff = cv2.absdiff(gray1, gray2)

            # Threshold to get binary difference
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

            # Find contours of changes
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Calculate change percentage
            total_pixels = img1.shape[0] * img1.shape[1]
            changed_pixels = np.sum(thresh > 0)
            change_percentage = (changed_pixels / total_pixels) * 100

            # Filter significant changes
            significant_changes = [c for c in contours if cv2.contourArea(c) > 100]

            return {
                "change_detected": change_percentage > 1.0,
                "change_percentage": change_percentage,
                "num_changed_regions": len(significant_changes),
                "time_delta_hours": time_delta,
                "significant": change_percentage > 5.0
            }

        except Exception as e:
            logger.error(f"Change detection failed: {e}")
            return {
                "change_detected": False,
                "error": str(e)
            }


# Create singleton instance
image_analysis_service = ImageAnalysisService()
