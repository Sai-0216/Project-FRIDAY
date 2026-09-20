"""FRIDAY V3 - Phase 34.5 Visual Context Extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from proactive.image_understanding import image_understanding
from proactive.ocr import ocr
from proactive.multimodal_intelligence import multimodal_intelligence


class VisualContext:

    def extract(
        self,
        image_path: str | Path,
    ) -> dict[str, Any]:
        """Combine visual understanding and OCR into one context."""

        if not isinstance(image_path, (str, Path)):
            raise TypeError("image_path must be a string or Path")

        path = Path(image_path)

        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")

        visual = image_understanding.analyze(path)
        text = ocr.extract(path)

        return multimodal_intelligence.normalize(
            modality="image",
            content={
                "type": "visual_context",
                "path": str(path),
                "description": visual["content"]["description"],
                "text": text["content"]["text"],
            },
            source="visual_context",
            metadata={
                "vision_model": visual["metadata"]["vision_model"],
                "ocr_engine": text["metadata"]["ocr_engine"],
                "ocr_version": text["metadata"]["ocr_version"],
                "language": text["metadata"]["language"],
            },
        )

    def validate(self, result: Any) -> bool:
        """Validate a visual-context observation."""

        if not multimodal_intelligence.validate(result):
            return False

        if result.get("source") != "visual_context":
            return False

        content = result.get("content")

        if not isinstance(content, dict):
            return False

        if content.get("type") != "visual_context":
            return False

        if not isinstance(content.get("description"), str):
            return False

        if not isinstance(content.get("text"), str):
            return False

        return True


visual_context = VisualContext()
