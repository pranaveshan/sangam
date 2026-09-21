"""Translation service — UI uses locale files; dynamic content may use this later."""
from __future__ import annotations

from typing import Optional


class TranslationService:
    """
    Do not LLM-translate the whole UI on every request.
    Preserve original citizen language; optional pass-through for dynamic content.
    """

    def __init__(self):
        self.provider = "passthrough_local"

    def translate(
        self,
        text: str,
        *,
        source_lang: Optional[str] = None,
        target_lang: str = "en",
    ) -> dict:
        # Honest: without an external MT model we do not invent translations.
        if not text:
            return {
                "text": "",
                "source_lang": source_lang or "unknown",
                "target_lang": target_lang,
                "translated": False,
                "provider": self.provider,
            }
        if source_lang and source_lang.split("-")[0] == target_lang.split("-")[0]:
            return {
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "translated": False,
                "provider": self.provider,
            }
        return {
            "text": text,
            "source_lang": source_lang or "unknown",
            "target_lang": target_lang,
            "translated": False,
            "provider": self.provider,
            "note": "Original language preserved. Machine translation provider not configured.",
        }


translation_service = TranslationService()
