"""
NLP Service
Handles natural language processing for communication analysis and SITREP generation
"""

import logging
from typing import Dict, Any, List, Optional
import time
import re

from app.services.gemini_service import gemini_service
from app.models.sitrep import SitrepPriority, SitrepClassification

logger = logging.getLogger(__name__)


class NLPService:
    """Service for natural language processing tasks"""

    def __init__(self):
        """Initialize NLP service"""
        self.gemini = gemini_service
        logger.info("NLP service initialized")

    async def analyze_communication(
        self,
        text: str,
        source: str = "radio"
    ) -> Dict[str, Any]:
        """
        Analyze military communication for intelligence

        Args:
            text: Communication text to analyze
            source: Source of communication (radio, message, etc.)

        Returns:
            Analysis results with extracted intelligence
        """
        try:
            start_time = time.time()

            # Use Gemini for threat-focused text analysis
            analysis = await self.gemini.analyze_text(text, analysis_type="threat")

            # Extract entities
            entities = await self.gemini.extract_entities(text)

            # Assess urgency and priority
            priority = self._assess_priority(text)

            analysis_time = time.time() - start_time

            return {
                "analyzed_text": text,
                "source": source,
                "entities": entities,
                "priority": priority,
                "analysis": analysis.get("parsed_analysis"),
                "raw_analysis": analysis.get("raw_response"),
                "analysis_time": analysis_time,
                "contains_threat": self._contains_threat_keywords(text)
            }

        except Exception as e:
            logger.error(f"Communication analysis failed: {e}")
            raise

    async def generate_sitrep_from_text(
        self,
        input_text: str,
        location: Optional[str] = None,
        unit: Optional[str] = None,
        reporter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured SITREP from unstructured text

        Args:
            input_text: Raw input text
            location: Optional location context
            unit: Optional unit context
            reporter: Optional reporter name

        Returns:
            Structured SITREP data
        """
        try:
            start_time = time.time()

            # Generate SITREP using Gemini
            sitrep_data = await self.gemini.generate_sitrep(
                input_text,
                location=location,
                unit=unit
            )

            # Extract entities
            entities = sitrep_data.get("entities", [])
            if not entities:
                entities = await self.gemini.extract_entities(input_text)

            # Process and structure
            structured_sitrep = {
                "title": sitrep_data.get("title", "Situation Report"),
                "situation": sitrep_data.get("situation", ""),
                "mission": sitrep_data.get("mission", ""),
                "execution": sitrep_data.get("execution", ""),
                "admin_logistics": sitrep_data.get("admin_logistics", ""),
                "command_signal": sitrep_data.get("command_signal", ""),
                "priority": self._normalize_priority(sitrep_data.get("priority", "ROUTINE")),
                "classification": self._normalize_classification(sitrep_data.get("classification", "UNCLASSIFIED")),
                "entities": entities,
                "key_points": sitrep_data.get("key_points", []),
                "location": location,
                "unit": unit,
                "reporter": reporter,
                "audio_transcript": input_text,
                "processing_time": time.time() - start_time
            }

            # Extract coordinates if mentioned
            coords = self._extract_coordinates(input_text)
            if coords:
                structured_sitrep["latitude"] = coords.get("latitude")
                structured_sitrep["longitude"] = coords.get("longitude")

            return structured_sitrep

        except Exception as e:
            logger.error(f"SITREP generation failed: {e}")
            raise

    async def process_voice_debriefing(
        self,
        transcript: str,
        reporter: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process voice debriefing transcript into structured SITREP

        Args:
            transcript: Voice-to-text transcript
            reporter: Name of reporter
            location: Location of report

        Returns:
            Structured SITREP with confidence scores
        """
        try:
            # Clean transcript
            cleaned_transcript = self._clean_transcript(transcript)

            # Generate SITREP
            sitrep = await self.generate_sitrep_from_text(
                cleaned_transcript,
                location=location,
                reporter=reporter
            )

            # Calculate confidence based on transcript quality
            confidence = self._calculate_transcript_confidence(transcript, sitrep)

            sitrep["confidence"] = confidence
            sitrep["source"] = "voice"

            return sitrep

        except Exception as e:
            logger.error(f"Voice debriefing processing failed: {e}")
            raise

    def _assess_priority(self, text: str) -> str:
        """Assess priority level from text content"""
        text_lower = text.lower()

        # Critical keywords
        if any(word in text_lower for word in [
            "flash", "emergency", "immediate threat", "under attack",
            "casualties", "sos", "urgent", "mayday"
        ]):
            return SitrepPriority.FLASH.value

        # High priority keywords
        if any(word in text_lower for word in [
            "immediate", "contact", "engaged", "hostile",
            "taking fire", "wounded", "priority"
        ]):
            return SitrepPriority.IMMEDIATE.value

        # Medium priority keywords
        if any(word in text_lower for word in [
            "priority", "suspicious", "possible threat",
            "movement", "activity"
        ]):
            return SitrepPriority.PRIORITY.value

        return SitrepPriority.ROUTINE.value

    def _contains_threat_keywords(self, text: str) -> bool:
        """Check if text contains threat-related keywords"""
        threat_keywords = [
            "hostile", "enemy", "threat", "weapon", "armed",
            "attack", "ambush", "ied", "explosive", "fire",
            "engagement", "contact", "casualties", "wounded"
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in threat_keywords)

    def _extract_coordinates(self, text: str) -> Optional[Dict[str, float]]:
        """Extract coordinates from text"""
        # Pattern for decimal coordinates
        pattern = r"(-?\d+\.?\d*)\s*[,°]\s*(-?\d+\.?\d*)"
        matches = re.findall(pattern, text)

        if matches:
            try:
                lat, lon = float(matches[0][0]), float(matches[0][1])
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return {"latitude": lat, "longitude": lon}
            except ValueError:
                pass

        # Pattern for MGRS (Military Grid Reference System)
        mgrs_pattern = r"\b\d{1,2}[A-Z]{3}\d{4,10}\b"
        mgrs_matches = re.findall(mgrs_pattern, text)
        if mgrs_matches:
            # Would need MGRS to lat/lon converter
            # For now, just note that MGRS was found
            logger.info(f"MGRS coordinate found: {mgrs_matches[0]}")

        return None

    def _clean_transcript(self, transcript: str) -> str:
        """Clean and normalize voice transcript"""
        # Remove filler words
        fillers = ["um", "uh", "er", "ah", "like", "you know"]
        cleaned = transcript

        for filler in fillers:
            cleaned = re.sub(r'\b' + filler + r'\b', '', cleaned, flags=re.IGNORECASE)

        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)

        # Capitalize sentences
        sentences = cleaned.split('. ')
        sentences = [s.capitalize() for s in sentences]
        cleaned = '. '.join(sentences)

        return cleaned.strip()

    def _calculate_transcript_confidence(
        self,
        transcript: str,
        sitrep: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for transcript processing"""
        confidence = 1.0

        # Reduce confidence for very short transcripts
        word_count = len(transcript.split())
        if word_count < 20:
            confidence -= 0.3

        # Reduce confidence if no entities extracted
        if not sitrep.get("entities"):
            confidence -= 0.2

        # Reduce confidence if no location information
        if not sitrep.get("latitude") and not sitrep.get("location"):
            confidence -= 0.1

        # Check for incomplete sections
        sections = ["situation", "mission", "execution"]
        empty_sections = sum(1 for s in sections if not sitrep.get(s))
        confidence -= (empty_sections * 0.1)

        return max(0.0, min(1.0, confidence))

    def _normalize_priority(self, priority: str) -> str:
        """Normalize priority string to enum value"""
        priority_upper = priority.upper()

        if "FLASH" in priority_upper:
            return SitrepPriority.FLASH.value
        elif "IMMEDIATE" in priority_upper:
            return SitrepPriority.IMMEDIATE.value
        elif "PRIORITY" in priority_upper:
            return SitrepPriority.PRIORITY.value
        else:
            return SitrepPriority.ROUTINE.value

    def _normalize_classification(self, classification: str) -> str:
        """Normalize classification string to enum value"""
        classification_lower = classification.lower()

        if "top" in classification_lower and "secret" in classification_lower:
            return SitrepClassification.TOP_SECRET.value
        elif "secret" in classification_lower:
            return SitrepClassification.SECRET.value
        elif "confidential" in classification_lower:
            return SitrepClassification.CONFIDENTIAL.value
        else:
            return SitrepClassification.UNCLASSIFIED.value


# Create singleton instance
nlp_service = NLPService()
