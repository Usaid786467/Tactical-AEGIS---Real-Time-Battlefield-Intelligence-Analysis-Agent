"""
Data Fusion Utilities
Combines data from multiple sources into coherent tactical picture
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class DataFusionEngine:
    """Engine for fusing multi-source intelligence data"""

    def __init__(self):
        """Initialize data fusion engine"""
        self.source_weights = {
            "satellite": 0.8,
            "drone": 0.9,
            "sensor": 0.7,
            "radio": 0.6,
            "manual": 0.5
        }
        logger.info("Data fusion engine initialized")

    def fuse_threat_data(
        self,
        threats: List[Dict[str, Any]],
        correlation_radius_km: float = 0.5,
        time_window_hours: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Fuse threat detections from multiple sources

        Args:
            threats: List of threat detections
            correlation_radius_km: Radius for spatial correlation
            time_window_hours: Time window for temporal correlation

        Returns:
            Fused threat data
        """
        try:
            if not threats:
                return []

            # Sort by time
            threats_sorted = sorted(
                threats,
                key=lambda t: t.get("detected_at", datetime.utcnow())
            )

            fused_threats = []
            processed_indices = set()

            for i, threat in enumerate(threats_sorted):
                if i in processed_indices:
                    continue

                # Find correlated threats
                correlated = [threat]
                correlated_indices = {i}

                for j, other_threat in enumerate(threats_sorted[i+1:], start=i+1):
                    if j in processed_indices:
                        continue

                    if self._are_threats_correlated(
                        threat,
                        other_threat,
                        correlation_radius_km,
                        time_window_hours
                    ):
                        correlated.append(other_threat)
                        correlated_indices.add(j)

                # Fuse correlated threats
                fused_threat = self._fuse_correlated_threats(correlated)
                fused_threats.append(fused_threat)

                processed_indices.update(correlated_indices)

            logger.info(f"Fused {len(threats)} threats into {len(fused_threats)} correlated detections")
            return fused_threats

        except Exception as e:
            logger.error(f"Threat data fusion failed: {e}")
            return threats

    def _are_threats_correlated(
        self,
        threat1: Dict[str, Any],
        threat2: Dict[str, Any],
        radius_km: float,
        time_window_hours: float
    ) -> bool:
        """Check if two threats are correlated"""
        # Check threat type
        if threat1.get("threat_type") != threat2.get("threat_type"):
            return False

        # Check spatial proximity
        distance = self._calculate_distance(
            threat1.get("latitude", 0),
            threat1.get("longitude", 0),
            threat2.get("latitude", 0),
            threat2.get("longitude", 0)
        )

        if distance > radius_km:
            return False

        # Check temporal proximity
        time1 = threat1.get("detected_at", datetime.utcnow())
        time2 = threat2.get("detected_at", datetime.utcnow())

        if isinstance(time1, str):
            time1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
        if isinstance(time2, str):
            time2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))

        time_diff = abs((time2 - time1).total_seconds() / 3600)

        return time_diff <= time_window_hours

    def _fuse_correlated_threats(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fuse multiple correlated threat detections"""
        if len(threats) == 1:
            threats[0]["correlation_count"] = 1
            threats[0]["sources"] = [threats[0].get("source", "unknown")]
            return threats[0]

        # Calculate weighted average position
        total_weight = 0
        weighted_lat = 0
        weighted_lon = 0
        sources = []
        max_confidence = 0

        for threat in threats:
            source = threat.get("source", "unknown")
            weight = self.source_weights.get(source, 0.5)
            confidence = threat.get("confidence", 0.5)

            sources.append(source)
            total_weight += weight * confidence
            weighted_lat += threat.get("latitude", 0) * weight * confidence
            weighted_lon += threat.get("longitude", 0) * weight * confidence
            max_confidence = max(max_confidence, confidence)

        # Average position
        avg_lat = weighted_lat / total_weight if total_weight > 0 else threats[0].get("latitude", 0)
        avg_lon = weighted_lon / total_weight if total_weight > 0 else threats[0].get("longitude", 0)

        # Boost confidence due to multiple sources
        fused_confidence = min(1.0, max_confidence + 0.1 * (len(threats) - 1))

        # Select highest threat level
        threat_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        max_level = max(
            (threat_levels.get(t.get("threat_level", "low"), 1) for t in threats),
            default=1
        )
        threat_level = [k for k, v in threat_levels.items() if v == max_level][0]

        # Combine descriptions
        descriptions = [t.get("description", "") for t in threats if t.get("description")]
        combined_description = " | ".join(set(descriptions))

        fused = {
            **threats[0],  # Start with first threat's data
            "latitude": avg_lat,
            "longitude": avg_lon,
            "confidence": fused_confidence,
            "threat_level": threat_level,
            "description": combined_description,
            "correlation_count": len(threats),
            "sources": list(set(sources)),
            "fused": True
        }

        return fused

    def create_tactical_picture(
        self,
        threats: List[Dict[str, Any]],
        friendly_forces: List[Dict[str, Any]],
        area_bounds: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive tactical picture

        Args:
            threats: List of threat data
            friendly_forces: List of friendly force data
            area_bounds: Optional area bounds

        Returns:
            Comprehensive tactical picture
        """
        try:
            # Fuse threats
            fused_threats = self.fuse_threat_data(threats)

            # Analyze threat distribution
            threat_analysis = self._analyze_threat_distribution(fused_threats)

            # Analyze force positioning
            force_analysis = self._analyze_force_positioning(friendly_forces, fused_threats)

            # Assess overall situation
            situation_assessment = self._assess_situation(
                fused_threats,
                friendly_forces,
                threat_analysis,
                force_analysis
            )

            tactical_picture = {
                "timestamp": datetime.utcnow().isoformat(),
                "area_bounds": area_bounds,
                "threats": {
                    "total": len(fused_threats),
                    "by_type": threat_analysis["by_type"],
                    "by_level": threat_analysis["by_level"],
                    "data": fused_threats
                },
                "friendly_forces": {
                    "total": len(friendly_forces),
                    "by_status": self._count_by_status(friendly_forces),
                    "data": friendly_forces
                },
                "situation_assessment": situation_assessment,
                "recommendations": self._generate_recommendations(situation_assessment)
            }

            return tactical_picture

        except Exception as e:
            logger.error(f"Failed to create tactical picture: {e}")
            raise

    def _analyze_threat_distribution(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of threats"""
        by_type = defaultdict(int)
        by_level = defaultdict(int)

        for threat in threats:
            by_type[threat.get("threat_type", "unknown")] += 1
            by_level[threat.get("threat_level", "unknown")] += 1

        return {
            "by_type": dict(by_type),
            "by_level": dict(by_level)
        }

    def _analyze_force_positioning(
        self,
        forces: List[Dict[str, Any]],
        threats: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze friendly force positioning relative to threats"""
        at_risk_units = []

        for force in forces:
            nearest_threat_dist = float('inf')
            nearest_threat = None

            for threat in threats:
                distance = self._calculate_distance(
                    force.get("latitude", 0),
                    force.get("longitude", 0),
                    threat.get("latitude", 0),
                    threat.get("longitude", 0)
                )

                if distance < nearest_threat_dist:
                    nearest_threat_dist = distance
                    nearest_threat = threat

            # Consider at risk if within 5km of high/critical threat
            if nearest_threat and nearest_threat_dist < 5.0:
                threat_level = nearest_threat.get("threat_level", "low")
                if threat_level in ["high", "critical"]:
                    at_risk_units.append({
                        "unit_id": force.get("unit_id"),
                        "unit_name": force.get("unit_name"),
                        "threat_distance_km": nearest_threat_dist,
                        "threat_type": nearest_threat.get("threat_type"),
                        "threat_level": threat_level
                    })

        return {
            "at_risk_units": at_risk_units,
            "at_risk_count": len(at_risk_units)
        }

    def _assess_situation(
        self,
        threats: List[Dict[str, Any]],
        forces: List[Dict[str, Any]],
        threat_analysis: Dict[str, Any],
        force_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess overall tactical situation"""
        # Calculate threat score
        threat_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        total_threat_score = sum(
            threat_scores.get(t.get("threat_level", "low"), 1)
            for t in threats
        )

        avg_threat_level = total_threat_score / max(len(threats), 1)

        # Determine overall status
        if avg_threat_level >= 3 or force_analysis["at_risk_count"] > len(forces) * 0.3:
            status = "critical"
        elif avg_threat_level >= 2.5 or force_analysis["at_risk_count"] > 0:
            status = "elevated"
        elif avg_threat_level >= 2:
            status = "moderate"
        else:
            status = "low"

        return {
            "status": status,
            "avg_threat_level": avg_threat_level,
            "threat_count": len(threats),
            "units_at_risk": force_analysis["at_risk_count"],
            "summary": self._generate_situation_summary(status, threats, forces)
        }

    def _generate_situation_summary(
        self,
        status: str,
        threats: List[Dict[str, Any]],
        forces: List[Dict[str, Any]]
    ) -> str:
        """Generate situation summary text"""
        critical_threats = sum(1 for t in threats if t.get("threat_level") == "critical")
        high_threats = sum(1 for t in threats if t.get("threat_level") == "high")

        summary = f"Tactical situation: {status.upper()}. "
        summary += f"{len(threats)} threat(s) detected. "

        if critical_threats > 0:
            summary += f"{critical_threats} CRITICAL threat(s). "
        if high_threats > 0:
            summary += f"{high_threats} HIGH priority threat(s). "

        summary += f"{len(forces)} friendly unit(s) tracked."

        return summary

    def _generate_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate tactical recommendations"""
        recommendations = []
        status = assessment.get("status", "low")

        if status == "critical":
            recommendations.append("IMMEDIATE ACTION REQUIRED: Multiple high-priority threats detected")
            recommendations.append("Recommend force protection measures")
            recommendations.append("Consider repositioning at-risk units")
            recommendations.append("Increase surveillance and intelligence gathering")
        elif status == "elevated":
            recommendations.append("Enhanced vigilance recommended")
            recommendations.append("Monitor threat developments closely")
            recommendations.append("Prepare contingency responses")
        elif status == "moderate":
            recommendations.append("Maintain current posture")
            recommendations.append("Continue routine monitoring")
        else:
            recommendations.append("Situation favorable")
            recommendations.append("Maintain situational awareness")

        if assessment.get("units_at_risk", 0) > 0:
            recommendations.append(f"WARNING: {assessment['units_at_risk']} unit(s) in proximity to threats")

        return recommendations

    def _count_by_status(self, forces: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count forces by status"""
        status_counts = defaultdict(int)
        for force in forces:
            status_counts[force.get("status", "unknown")] += 1
        return dict(status_counts)

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km between two points"""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c


# Create singleton instance
data_fusion_engine = DataFusionEngine()
