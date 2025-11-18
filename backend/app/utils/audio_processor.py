"""
Audio Processing Utilities
Handles audio signature analysis and speech-to-text
"""

import logging
import base64
from io import BytesIO
from typing import Dict, Any, Optional
import numpy as np

try:
    import librosa
    import soundfile as sf
    from pydub import AudioSegment
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logging.warning("Audio processing libraries not available")

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Processor for audio analysis and transcription"""

    def __init__(self):
        """Initialize audio processor"""
        if not AUDIO_LIBS_AVAILABLE:
            logger.warning("Audio processing features will be limited")
        logger.info("Audio processor initialized")

    async def transcribe_audio(
        self,
        audio_data: str,
        audio_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text

        Args:
            audio_data: Base64 encoded audio data
            audio_format: Audio format (wav, mp3, ogg)

        Returns:
            Transcription results
        """
        try:
            # For now, return mock transcription
            # In production, would use Google Speech-to-Text or Web Speech API
            logger.info("Audio transcription requested")

            # Decode audio
            audio_bytes = base64.b64decode(audio_data)

            # Mock transcription (replace with actual STT service)
            mock_transcript = """
            This is Alpha Two-One. We're at checkpoint Bravo.
            Observed three vehicles heading north on Route 7.
            Approximately 2 kilometers from our position.
            No hostile activity at this time.
            Request permission to continue patrol.
            """

            return {
                "transcript": mock_transcript.strip(),
                "confidence": 0.85,
                "language": "en-US",
                "duration_seconds": self._estimate_duration(audio_bytes),
                "format": audio_format,
                "word_count": len(mock_transcript.split())
            }

        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise

    def analyze_audio_signature(
        self,
        audio_data: str
    ) -> Dict[str, Any]:
        """
        Analyze audio for weapon fire, explosions, etc.

        Args:
            audio_data: Base64 encoded audio data

        Returns:
            Audio signature analysis results
        """
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return self._mock_audio_analysis()

            # Decode audio
            audio_bytes = base64.b64decode(audio_data)

            # Load audio
            audio_io = BytesIO(audio_bytes)
            y, sr = librosa.load(audio_io)

            # Extract features
            features = self._extract_audio_features(y, sr)

            # Classify signatures
            signatures = self._classify_audio_signatures(features)

            return {
                "signatures_detected": signatures,
                "features": features,
                "duration": len(y) / sr,
                "sample_rate": sr
            }

        except Exception as e:
            logger.error(f"Audio signature analysis failed: {e}")
            return self._mock_audio_analysis()

    def _extract_audio_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract audio features for analysis"""
        try:
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

            # Rhythm features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

            # Energy features
            rms = librosa.feature.rms(y=y)[0]

            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]

            return {
                "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                "tempo": float(tempo),
                "rms_mean": float(np.mean(rms)),
                "rms_max": float(np.max(rms)),
                "zcr_mean": float(np.mean(zcr))
            }

        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}

    def _classify_audio_signatures(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Classify audio signatures based on features"""
        signatures = []

        # Simple rule-based classification (in production, use ML model)
        rms_max = features.get("rms_max", 0)
        spectral_centroid = features.get("spectral_centroid_mean", 0)

        # Gunfire detection (high energy, high frequency)
        if rms_max > 0.5 and spectral_centroid > 2000:
            signatures.append({
                "type": "gunfire",
                "confidence": 0.75,
                "description": "Possible weapon fire signature detected"
            })

        # Explosion detection (very high energy, broad spectrum)
        if rms_max > 0.8:
            signatures.append({
                "type": "explosion",
                "confidence": 0.65,
                "description": "Possible explosion signature detected"
            })

        # Vehicle detection (low frequency, continuous)
        if spectral_centroid < 1000 and rms_max > 0.3:
            signatures.append({
                "type": "vehicle",
                "confidence": 0.60,
                "description": "Possible vehicle engine signature detected"
            })

        return signatures

    def _mock_audio_analysis(self) -> Dict[str, Any]:
        """Return mock audio analysis when libraries unavailable"""
        return {
            "signatures_detected": [
                {
                    "type": "gunfire",
                    "confidence": 0.70,
                    "description": "Possible weapon fire signature (mock)"
                }
            ],
            "features": {
                "spectral_centroid_mean": 2500.0,
                "rms_max": 0.65
            },
            "duration": 3.5,
            "sample_rate": 44100,
            "note": "Mock analysis - audio libraries not available"
        }

    def _estimate_duration(self, audio_bytes: bytes) -> float:
        """Estimate audio duration from byte size"""
        # Rough estimate: 44100 Hz * 16 bit * 1 channel = ~88KB per second
        size_kb = len(audio_bytes) / 1024
        estimated_seconds = size_kb / 88
        return max(1.0, estimated_seconds)

    def convert_audio_format(
        self,
        audio_data: str,
        from_format: str,
        to_format: str = "wav"
    ) -> str:
        """
        Convert audio between formats

        Args:
            audio_data: Base64 encoded audio
            from_format: Source format
            to_format: Target format

        Returns:
            Base64 encoded converted audio
        """
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return audio_data  # Return original if can't convert

            # Decode audio
            audio_bytes = base64.b64decode(audio_data)

            # Load with pydub
            audio = AudioSegment.from_file(BytesIO(audio_bytes), format=from_format)

            # Export to target format
            output_io = BytesIO()
            audio.export(output_io, format=to_format)

            # Encode back to base64
            output_io.seek(0)
            converted_data = base64.b64encode(output_io.read()).decode()

            return converted_data

        except Exception as e:
            logger.error(f"Audio format conversion failed: {e}")
            return audio_data


# Create singleton instance
audio_processor = AudioProcessor()
