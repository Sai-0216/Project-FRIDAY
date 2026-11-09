"""FRIDAY V3 - Phase 34.7 Speech Context."""

from __future__ import annotations

from typing import Any


class SpeechContext:

    def extract(
        self,
        observation: dict[str, Any],
    ) -> dict[str, Any]:
        """Extract lightweight conversational context from speech."""

        if not isinstance(observation, dict):
            raise TypeError("observation must be a dictionary")

        content = observation.get("content")

        if not isinstance(content, dict):
            raise ValueError("observation content must be a dictionary")

        text = content.get("text")

        if not isinstance(text, str):
            raise ValueError("speech text must be a string")

        normalized = " ".join(text.strip().split())

        if not normalized:
            raise ValueError("speech text must not be empty")

        return {
            "text": normalized,
            "speech_type": content.get("type", "speech"),
            "signals": self._signals(normalized),
            "confidence": self._confidence(observation),
        }

    def _signals(self, text: str) -> dict[str, bool]:
        """Extract lightweight speech-level signals."""

        value = text.lower().strip()

        affirmative = value in {
            "yes",
            "yeah",
            "yep",
            "sure",
            "okay",
            "ok",
            "alright",
        } or value.startswith(
            (
                "yes ",
                "yeah ",
                "yep ",
                "sure ",
                "okay ",
                "ok ",
                "alright ",
            )
        )

        negative = value in {
            "no",
            "nope",
            "nah",
            "not now",
        } or value.startswith(
            (
                "no ",
                "nope ",
                "nah ",
            )
        )

        return {
            "question": value.endswith("?"),
            "affirmative": affirmative,
            "negative": negative,
            "correction": value.startswith(
                (
                    "correct",
                    "actually",
                    "no,",
                )
            ),
            "continuation": value.endswith(
                (
                    "again",
                    "that",
                    "this",
                )
            ),
        }

    def _confidence(self, observation: dict[str, Any]) -> float:
        """Read an optional confidence value without inventing one."""

        metadata = observation.get("metadata")

        if not isinstance(metadata, dict):
            return 1.0

        confidence = metadata.get("confidence")

        if isinstance(confidence, (int, float)):
            return float(confidence)

        return 1.0

    def validate(self, result: Any) -> bool:
        """Validate a SpeechContext result."""

        if not isinstance(result, dict):
            return False

        if not isinstance(result.get("text"), str):
            return False

        if not result.get("text").strip():
            return False

        if not isinstance(result.get("speech_type"), str):
            return False

        signals = result.get("signals")

        if not isinstance(signals, dict):
            return False

        expected = {
            "question",
            "affirmative",
            "negative",
            "correction",
            "continuation",
        }

        if set(signals) != expected:
            return False

        if not all(
            isinstance(value, bool)
            for value in signals.values()
        ):
            return False

        confidence = result.get("confidence")

        return isinstance(confidence, (int, float))


speech_context = SpeechContext()
