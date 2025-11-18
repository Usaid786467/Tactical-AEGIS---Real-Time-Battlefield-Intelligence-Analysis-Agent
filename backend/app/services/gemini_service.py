"""
Gemini AI Service
Handles integration with Google Gemini API for vision and NLP analysis
"""

import google.generativeai as genai
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO
from PIL import Image
import logging
import time

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI"""

    def __init__(self):
        """Initialize Gemini service"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.vision_model = genai.GenerativeModel('gemini-1.5-pro')
            self.text_model = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI service: {e}")
            raise

    async def analyze_image(
        self,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        prompt: str = "Analyze this tactical image for threats, vehicles, personnel, and equipment. Provide detailed analysis.",
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze image using Gemini Vision

        Args:
            image_data: Base64 encoded image data
            image_url: URL to image
            prompt: Analysis prompt
            confidence_threshold: Minimum confidence threshold

        Returns:
            Dictionary containing analysis results
        """
        try:
            start_time = time.time()

            # Prepare image
            if image_data:
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
            elif image_url:
                # Download image from URL
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content))
            else:
                raise ValueError("Either image_data or image_url must be provided")

            # Enhance prompt for tactical analysis
            enhanced_prompt = f"""
{prompt}

Analyze this image from a tactical/military perspective and provide:
1. Detected objects (vehicles, personnel, weapons, equipment)
2. Threat assessment (threat level: low/medium/high/critical)
3. Confidence score for each detection (0.0 to 1.0)
4. Location/position of threats in the image
5. Any unusual or concerning activity
6. Recommendations for command

Format your response as JSON with the following structure:
{{
    "threats": [
        {{
            "type": "vehicle/personnel/weapon/etc",
            "description": "detailed description",
            "threat_level": "low/medium/high/critical",
            "confidence": 0.0-1.0,
            "position": "location in image",
            "reasoning": "why this is considered a threat"
        }}
    ],
    "overall_assessment": "summary of the tactical situation",
    "recommendations": ["list of recommendations"]
}}
"""

            # Generate content
            response = self.vision_model.generate_content([enhanced_prompt, image])

            # Parse response
            analysis_time = time.time() - start_time

            result = {
                "raw_response": response.text,
                "analysis_time": analysis_time,
                "model": "gemini-1.5-pro-vision",
                "confidence_threshold": confidence_threshold
            }

            # Try to parse JSON from response
            try:
                import json
                # Extract JSON from markdown code blocks if present
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                parsed_data = json.loads(text)
                result["parsed_analysis"] = parsed_data
            except Exception as e:
                logger.warning(f"Could not parse JSON response: {e}")
                result["parsed_analysis"] = None

            logger.info(f"Image analysis completed in {analysis_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise

    async def analyze_text(
        self,
        text: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze text using Gemini NLP

        Args:
            text: Text to analyze
            analysis_type: Type of analysis (general, threat, sitrep, communication)

        Returns:
            Dictionary containing analysis results
        """
        try:
            start_time = time.time()

            # Create analysis prompt based on type
            if analysis_type == "threat":
                prompt = f"""
Analyze the following communication for potential threats and tactical intelligence:

{text}

Provide:
1. Identified threats or hostile activities
2. Locations mentioned
3. Unit designations
4. Equipment or weapons mentioned
5. Threat level assessment
6. Confidence in the analysis

Format as JSON.
"""
            elif analysis_type == "sitrep":
                prompt = f"""
Convert the following text into a structured military SITREP (Situation Report):

{text}

Extract and structure into:
1. SITUATION: Current tactical situation
2. MISSION: Mission or objective
3. EXECUTION: Actions taken or planned
4. ADMIN/LOGISTICS: Administrative and logistics notes
5. COMMAND/SIGNAL: Command and communications info

Also extract:
- Locations (with coordinates if mentioned)
- Unit designations
- Personnel counts
- Equipment/vehicles
- Times/dates

Format as JSON.
"""
            else:
                prompt = f"""
Analyze the following text for tactical intelligence:

{text}

Extract:
1. Key entities (locations, units, personnel, equipment)
2. Actions or events
3. Times and dates
4. Any intelligence value
5. Confidence in extracted information

Format as JSON.
"""

            # Generate content
            response = self.text_model.generate_content(prompt)

            # Parse response
            analysis_time = time.time() - start_time

            result = {
                "raw_response": response.text,
                "analysis_time": analysis_time,
                "model": "gemini-1.5-pro",
                "analysis_type": analysis_type
            }

            # Try to parse JSON from response
            try:
                import json
                text_response = response.text
                if "```json" in text_response:
                    text_response = text_response.split("```json")[1].split("```")[0].strip()
                elif "```" in text_response:
                    text_response = text_response.split("```")[1].split("```")[0].strip()

                parsed_data = json.loads(text_response)
                result["parsed_analysis"] = parsed_data
            except Exception as e:
                logger.warning(f"Could not parse JSON response: {e}")
                result["parsed_analysis"] = None

            logger.info(f"Text analysis completed in {analysis_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            raise

    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text

        Args:
            text: Text to analyze

        Returns:
            List of extracted entities
        """
        try:
            prompt = f"""
Extract all named entities from the following text:

{text}

Identify and extract:
- LOCATION: Places, coordinates, grid references
- UNIT: Military unit designations
- PERSONNEL: Names, ranks, positions
- EQUIPMENT: Vehicles, weapons, equipment
- TIME: Dates, times, durations
- QUANTITY: Numbers, counts, amounts
- EVENT: Actions, incidents, operations

Format as JSON array:
[
    {{"type": "LOCATION", "value": "Hill 227", "confidence": 0.95}},
    {{"type": "UNIT", "value": "Bravo Company", "confidence": 0.90}},
    ...
]
"""

            response = self.text_model.generate_content(prompt)

            # Parse response
            try:
                import json
                text_response = response.text
                if "```json" in text_response:
                    text_response = text_response.split("```json")[1].split("```")[0].strip()
                elif "```" in text_response:
                    text_response = text_response.split("```")[1].split("```")[0].strip()

                entities = json.loads(text_response)
                return entities if isinstance(entities, list) else []
            except Exception as e:
                logger.warning(f"Could not parse entities: {e}")
                return []

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    async def generate_sitrep(
        self,
        input_text: str,
        location: Optional[str] = None,
        unit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured SITREP from unstructured input

        Args:
            input_text: Raw input text (voice transcript, notes, etc.)
            location: Optional location context
            unit: Optional unit context

        Returns:
            Structured SITREP data
        """
        try:
            context = ""
            if location:
                context += f"\nLocation: {location}"
            if unit:
                context += f"\nUnit: {unit}"

            prompt = f"""
Generate a formal military SITREP (Situation Report) from the following information:
{context}

Input:
{input_text}

Create a structured SITREP with these sections:
1. SITUATION: Describe the current tactical situation
2. MISSION: State the mission or objective (if mentioned)
3. EXECUTION: Detail actions taken, in progress, or planned
4. ADMIN/LOGISTICS: Note administrative and logistical matters
5. COMMAND/SIGNAL: Include command relationships and communications info

Also provide:
- A clear, concise title for the SITREP
- Priority level (ROUTINE/PRIORITY/IMMEDIATE/FLASH)
- Recommended classification level
- List of extracted entities (locations, units, equipment, personnel)

Format as JSON with this structure:
{{
    "title": "SITREP title",
    "priority": "priority level",
    "classification": "classification level",
    "situation": "situation text",
    "mission": "mission text",
    "execution": "execution text",
    "admin_logistics": "admin/logistics text",
    "command_signal": "command/signal text",
    "entities": [
        {{"type": "entity type", "value": "entity value", "confidence": 0.0-1.0}}
    ],
    "key_points": ["list of key points"]
}}
"""

            response = self.text_model.generate_content(prompt)

            # Parse response
            try:
                import json
                text_response = response.text
                if "```json" in text_response:
                    text_response = text_response.split("```json")[1].split("```")[0].strip()
                elif "```" in text_response:
                    text_response = text_response.split("```")[1].split("```")[0].strip()

                sitrep_data = json.loads(text_response)
                return sitrep_data
            except Exception as e:
                logger.warning(f"Could not parse SITREP: {e}")
                return {
                    "raw_response": response.text,
                    "error": str(e)
                }

        except Exception as e:
            logger.error(f"SITREP generation failed: {e}")
            raise


# Create singleton instance
gemini_service = GeminiService()
