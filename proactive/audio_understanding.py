"""FRIDAY V3 - Phase 34.6 Audio Understanding."""

from __future__ import annotations

from typing import Any

from listen import listener
from proactive.multimodal_intelligence import multimodal_intelligence


class AudioUnderstanding:
    """Convert speech input into normalized multimodal observations."""

    def from_text(
        self,
        text: str,
        source: str = "speech_recognition",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create an audio observation from already-recognized speech."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not isinstance(source, str):
            raise TypeError("source must be a string")

        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError("text must not be empty")

        return multimodal_intelligence.normalize(
            modality="audio",
            content={
                "type": "speech",
                "text": normalized_text,
            },
            source=source.strip().lower() or "speech_recognition",
            metadata=metadata or {},
        )

    def listen(self) -> dict[str, Any] | None:
        """Listen through FRIDAY's existing microphone listener."""

        text = listener.listen()

        if not isinstance(text, str):
            raise TypeError("listener returned a non-string result")

        text = text.strip()

        if not text:
            return None

        return self.from_text(text)

    def validate(self, result: Any) -> bool:
        """Validate an audio observation."""

        if not multimodal_intelligence.validate(result):
            return False

        if result.get("source") != "speech_recognition":
            return False

        content = result.get("content")

        if not isinstance(content, dict):
            return False

        if content.get("type") != "speech":
            return False

        if not isinstance(content.get("text"), str):
            return False

        return True


audio_understanding = AudioUnderstanding()
