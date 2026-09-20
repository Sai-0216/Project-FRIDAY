"""FRIDAY V3 - Phase 34.1 Multimodal Intelligence Foundation."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


class MultimodalIntelligence:
    """Normalize multimodal observations into a common representation."""

    SUPPORTED_MODALITIES = frozenset({
        "text",
        "image",
        "screen",
        "audio",
    })

    def normalize(
        self,
        modality: str,
        content: Any = None,
        source: str = "unknown",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(modality, str):
            raise TypeError("modality must be a string")

        normalized_modality = modality.strip().lower()

        if normalized_modality not in self.SUPPORTED_MODALITIES:
            raise ValueError(
                f"Unsupported modality: {normalized_modality}"
            )

        if not isinstance(source, str):
            raise TypeError("source must be a string")

        normalized_source = source.strip().lower() or "unknown"

        if metadata is None:
            normalized_metadata = {}
        elif isinstance(metadata, dict):
            normalized_metadata = deepcopy(metadata)
        else:
            raise TypeError("metadata must be a dictionary")

        return {
            "modality": normalized_modality,
            "source": normalized_source,
            "content": deepcopy(content),
            "metadata": normalized_metadata,
            "created_at": datetime.now().isoformat(),
        }

    def validate(self, observation: Any) -> bool:
        if not isinstance(observation, dict):
            return False

        if observation.get("modality") not in self.SUPPORTED_MODALITIES:
            return False

        if not isinstance(observation.get("source"), str):
            return False

        if not isinstance(observation.get("metadata"), dict):
            return False

        if not isinstance(observation.get("created_at"), str):
            return False

        return True


multimodal_intelligence = MultimodalIntelligence()
