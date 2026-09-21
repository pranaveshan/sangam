"""Speech service abstraction — local path uses client transcript; Whisper optional later."""
from __future__ import annotations

from typing import Any, Optional


class SpeechService:
    """
    Responsibilities: STT, language hint, transcript packaging, confidence metadata.
    Default: accept browser/client transcript (Web Speech API). No fake transcription.
    """

    def __init__(self):
        self.provider = "client_web_speech"

    def transcribe(
        self,
        *,
        client_transcript: Optional[str] = None,
        language_hint: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
    ) -> dict[str, Any]:
        text = (client_transcript or "").strip()
        if text:
            return {
                "transcript": text,
                "language": language_hint or "unknown",
                "confidence": 0.85,
                "provider": self.provider,
                "audio_received": bool(audio_bytes),
                "filename": filename,
                "status": "ok",
                "note": "Transcript provided by client speech recognition. Server did not invent text.",
            }

        if audio_bytes:
            return {
                "transcript": "",
                "language": language_hint or "unknown",
                "confidence": 0.0,
                "provider": self.provider,
                "audio_received": True,
                "filename": filename,
                "status": "unavailable",
                "note": (
                    "Audio was received but server-side speech-to-text is not configured. "
                    "Use browser speech recognition or type the report."
                ),
            }

        return {
            "transcript": "",
            "language": language_hint or "unknown",
            "confidence": 0.0,
            "provider": self.provider,
            "audio_received": False,
            "status": "empty",
            "note": "No transcript or audio provided.",
        }


speech_service = SpeechService()
