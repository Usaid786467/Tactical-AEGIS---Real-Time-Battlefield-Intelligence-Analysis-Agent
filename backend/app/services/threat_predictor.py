"""
Threat Prediction Service
Analyzes patterns and predicts potential threats
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.database.schemas import ThreatDB
from app.models.threat import ThreatType, ThreatLevel, PredictedThreat
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class ThreatPredictorService:
    """Service for threat prediction and pattern analysis"""

    def __init__(self):
        """Initialize threat predictor service"""
        self.gemini = gemini_service
        logger.info("Threat predictor service initialized")

    async def predict_threats(
        self,
        db: Session,
        area_bounds: Dict[str, float],
        time_horizon_hours: int = 24,
        historical_days: int = 7,
        threat_types: Optional[List[ThreatType]] = None
    ) -> Dict[str, Any]:
        """
        Predict potential threats based on historical data and patterns

        Args:
            db: Database session
            area_bounds: Geographic bounds {north, south, east, west}
            time_horizon_hours: Hours to predict ahead
            historical_days: Days of historical data to analyze
            threat_types: Optional filter for specific threat types

        Returns:
            Threat predictions with confidence scores
        """
        try:
            start_time = time.time()

            # Get historical threats
            historical_threats = self._get_historical_threats(
                db,
                area_bounds,
                historical_days,
                threat_types
            )

            # Analyze patterns
            patterns = self._analyze_patterns(historical_threats)

            # Generate predictions using pattern analysis
            predictions = self._generate_predictions(
                patterns,
                area_bounds,
                time_horizon_hours
            )

            # Use AI for enhanced prediction reasoning
            if predictions:
                ai_enhanced = await self._enhance_predictions_with_ai(
                    historical_threats,
                    patterns,
                    predictions,
                    area_bounds
                )
                predictions = ai_enhanced

            analysis_time = time.time() - start_time

            return {
                "predictions": predictions,
                "analysis_time": analysis_time,
                "historical_threat_count": len(historical_threats),
                "patterns_detected": len(patterns),
                "confidence": self._calculate_overall_confidence(predictions),
                "factors_considered": [
                    "historical threat locations",
                    "temporal patterns",
                    "threat type clustering",
                    "geographic terrain features",
                    "recent threat activity"
                ],
                "model_version": "v1.0"
            }

        except Exception as e:
            logger.error(f"Threat prediction failed: {e}")
            raise

    def _get_historical_threats(
        self,
        db: Session,
        area_bounds: Dict[str, float],
        days: int,
        threat_types: Optional[List[ThreatType]] = None
    ) -> List[ThreatDB]:
        """Get historical threats from database"""
        try:
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(days=days)

            # Build query
            query = db.query(ThreatDB).filter(
                and_(
                    ThreatDB.latitude >= area_bounds["south"],
                    ThreatDB.latitude <= area_bounds["north"],
                    ThreatDB.longitude >= area_bounds["west"],
                    ThreatDB.longitude <= area_bounds["east"],
                    ThreatDB.detected_at >= time_threshold,
                    ThreatDB.active == True
                )
            )

            # Filter by threat types if specified
            if threat_types:
                type_values = [t.value if isinstance(t, ThreatType) else t for t in threat_types]
                query = query.filter(ThreatDB.threat_type.in_(type_values))

            threats = query.all()
            logger.info(f"Retrieved {len(threats)} historical threats")
            return threats

        except Exception as e:
            logger.error(f"Failed to retrieve historical threats: {e}")
            return []

    def _analyze_patterns(self, threats: List[ThreatDB]) -> List[Dict[str, Any]]:
        """Analyze patterns in historical threats"""
        patterns = []

        if not threats:
            return patterns

        # Pattern 1: Geographic clustering
        clusters = self._find_geographic_clusters(threats)
        for cluster in clusters:
            patterns.append({
                "type": "geographic_cluster",
                "threat_type": cluster["dominant_type"],
                "center_lat": cluster["center_lat"],
                "center_lon": cluster["center_lon"],
                "radius": cluster["radius"],
                "threat_count": cluster["count"],
                "confidence": cluster["confidence"]
            })

        # Pattern 2: Temporal patterns (time of day)
        temporal_pattern = self._find_temporal_patterns(threats)
        if temporal_pattern:
            patterns.append(temporal_pattern)

        # Pattern 3: Threat type frequency
        type_frequency = self._calculate_threat_type_frequency(threats)
        patterns.append({
            "type": "threat_frequency",
            "frequencies": type_frequency
        })

        # Pattern 4: Escalation pattern
        escalation = self._detect_escalation_pattern(threats)
        if escalation:
            patterns.append(escalation)

        return patterns

    def _find_geographic_clusters(
        self,
        threats: List[ThreatDB],
        min_cluster_size: int = 3
    ) -> List[Dict[str, Any]]:
        """Find geographic clusters of threats"""
        clusters = []

        # Simple clustering: group threats within 1km radius
        processed = set()

        for i, threat in enumerate(threats):
            if i in processed:
                continue

            cluster_threats = [threat]
            processed.add(i)

            # Find nearby threats
            for j, other_threat in enumerate(threats):
                if j in processed or i == j:
                    continue

                distance = self._calculate_distance(
                    threat.latitude, threat.longitude,
                    other_threat.latitude, other_threat.longitude
                )

                if distance <= 1.0:  # Within 1km
                    cluster_threats.append(other_threat)
                    processed.add(j)

            if len(cluster_threats) >= min_cluster_size:
                # Calculate cluster center
                center_lat = sum(t.latitude for t in cluster_threats) / len(cluster_threats)
                center_lon = sum(t.longitude for t in cluster_threats) / len(cluster_threats)

                # Find dominant threat type
                type_counts = {}
                for t in cluster_threats:
                    type_counts[t.threat_type] = type_counts.get(t.threat_type, 0) + 1

                dominant_type = max(type_counts, key=type_counts.get)

                clusters.append({
                    "center_lat": center_lat,
                    "center_lon": center_lon,
                    "radius": 1.0,
                    "count": len(cluster_threats),
                    "dominant_type": dominant_type,
                    "confidence": min(0.9, len(cluster_threats) / 10)
                })

        return clusters

    def _find_temporal_patterns(self, threats: List[ThreatDB]) -> Optional[Dict[str, Any]]:
        """Find temporal patterns (time of day)"""
        if len(threats) < 5:
            return None

        # Group by hour of day
        hour_counts = {}
        for threat in threats:
            hour = threat.detected_at.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        # Find peak hours
        if not hour_counts:
            return None

        peak_hour = max(hour_counts, key=hour_counts.get)
        peak_count = hour_counts[peak_hour]

        if peak_count >= len(threats) * 0.3:  # At least 30% in one hour
            return {
                "type": "temporal_pattern",
                "peak_hour": peak_hour,
                "peak_count": peak_count,
                "total_threats": len(threats),
                "confidence": min(0.8, peak_count / len(threats))
            }

        return None

    def _calculate_threat_type_frequency(self, threats: List[ThreatDB]) -> Dict[str, float]:
        """Calculate frequency of each threat type"""
        if not threats:
            return {}

        type_counts = {}
        for threat in threats:
            type_counts[threat.threat_type] = type_counts.get(threat.threat_type, 0) + 1

        total = len(threats)
        return {k: v / total for k, v in type_counts.items()}

    def _detect_escalation_pattern(self, threats: List[ThreatDB]) -> Optional[Dict[str, Any]]:
        """Detect escalation in threat levels over time"""
        if len(threats) < 10:
            return None

        # Sort by time
        sorted_threats = sorted(threats, key=lambda t: t.detected_at)

        # Split into two periods
        mid_point = len(sorted_threats) // 2
        early_threats = sorted_threats[:mid_point]
        recent_threats = sorted_threats[mid_point:]

        # Calculate average threat level (low=1, medium=2, high=3, critical=4)
        level_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}

        early_avg = sum(level_map.get(t.threat_level, 2) for t in early_threats) / len(early_threats)
        recent_avg = sum(level_map.get(t.threat_level, 2) for t in recent_threats) / len(recent_threats)

        if recent_avg > early_avg * 1.2:  # 20% increase
            return {
                "type": "escalation",
                "early_avg_level": early_avg,
                "recent_avg_level": recent_avg,
                "increase_factor": recent_avg / early_avg,
                "confidence": min(0.9, (recent_avg - early_avg) / 2)
            }

        return None

    def _generate_predictions(
        self,
        patterns: List[Dict[str, Any]],
        area_bounds: Dict[str, float],
        time_horizon_hours: int
    ) -> List[Dict[str, Any]]:
        """Generate predictions based on patterns"""
        predictions = []

        for pattern in patterns:
            if pattern["type"] == "geographic_cluster":
                # Predict continued activity in cluster area
                prediction = {
                    "threat_type": pattern["dominant_type"],
                    "latitude": pattern["center_lat"],
                    "longitude": pattern["center_lon"],
                    "probability": pattern["confidence"],
                    "confidence": pattern["confidence"],
                    "reasoning": f"Historical clustering of {pattern['count']} {pattern['dominant_type']} threats in this area",
                    "predicted_time": datetime.utcnow() + timedelta(hours=time_horizon_hours/2)
                }
                predictions.append(prediction)

            elif pattern["type"] == "escalation":
                # Predict continued escalation
                # Add prediction for highest threat areas
                pass  # Handled by cluster predictions

        return predictions

    async def _enhance_predictions_with_ai(
        self,
        historical_threats: List[ThreatDB],
        patterns: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]],
        area_bounds: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Use AI to enhance and refine predictions"""
        try:
            # Create summary of historical data
            summary = self._create_threat_summary(historical_threats, patterns)

            # Use Gemini for enhanced reasoning
            prompt = f"""
Analyze this tactical threat data and enhance the predictions:

Historical Summary:
{summary}

Current Predictions:
{predictions}

Provide enhanced reasoning for each prediction, considering:
1. Terrain and tactical advantages
2. Historical patterns and enemy behavior
3. Potential counter-measures and vulnerabilities
4. Risk factors and force protection implications

Return predictions in JSON array format with enhanced reasoning.
"""

            response = await self.gemini.text_model.generate_content(prompt)

            # Parse and merge enhanced reasoning
            import json
            try:
                enhanced_text = response.text
                if "```json" in enhanced_text:
                    enhanced_text = enhanced_text.split("```json")[1].split("```")[0].strip()
                elif "```" in enhanced_text:
                    enhanced_text = enhanced_text.split("```")[1].split("```")[0].strip()

                enhanced = json.loads(enhanced_text)

                # Merge with original predictions
                for i, pred in enumerate(predictions):
                    if i < len(enhanced):
                        pred["reasoning"] = enhanced[i].get("reasoning", pred["reasoning"])

            except Exception as e:
                logger.warning(f"Could not parse AI enhancement: {e}")

            return predictions

        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            return predictions

    def _create_threat_summary(
        self,
        threats: List[ThreatDB],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Create summary of threat data"""
        summary = f"Total threats analyzed: {len(threats)}\n"
        summary += f"Patterns detected: {len(patterns)}\n\n"

        # Threat type distribution
        type_counts = {}
        for threat in threats:
            type_counts[threat.threat_type] = type_counts.get(threat.threat_type, 0) + 1

        summary += "Threat Type Distribution:\n"
        for threat_type, count in type_counts.items():
            summary += f"  - {threat_type}: {count}\n"

        # Pattern summary
        summary += "\nKey Patterns:\n"
        for pattern in patterns:
            summary += f"  - {pattern['type']}: {pattern}\n"

        return summary

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km between two points using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth's radius in km

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def _calculate_overall_confidence(self, predictions: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in predictions"""
        if not predictions:
            return 0.0

        confidences = [p.get("confidence", 0.5) for p in predictions]
        return sum(confidences) / len(confidences)


# Create singleton instance
threat_predictor_service = ThreatPredictorService()
