"""FRIDAY V3 - Phase 34.2 Image Understanding."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import ollama
from PIL import Image

from config import config
from proactive.multimodal_intelligence import multimodal_intelligence


class ImageUnderstanding:

    def inspect(self, image_path: str | Path) -> dict[str, Any]:
        if not isinstance(image_path, (str, Path)):
            raise TypeError("image_path must be a string or Path")

        path = Path(image_path)

        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")

        with Image.open(path) as image:
            width, height = image.size
            image_format = image.format
            mode = image.mode

        metadata = {
            "path": str(path),
            "filename": path.name,
            "format": image_format,
            "mode": mode,
            "width": width,
            "height": height,
        }

        return multimodal_intelligence.normalize(
            modality="image",
            content={
                "type": "image",
                "path": str(path),
            },
            source="image_file",
            metadata=metadata,
        )

    def analyze(
        self,
        image_path: str | Path,
        prompt: str = (
            "Describe the important visible content in this image "
            "briefly and clearly."
        ),
    ) -> dict[str, Any]:
        if not isinstance(image_path, (str, Path)):
            raise TypeError("image_path must be a string or Path")

        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        path = Path(image_path)

        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")

        if not prompt.strip():
            raise ValueError("prompt must not be empty")

        observation = self.inspect(path)

        response = ollama.chat(
            model=config.VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                    "images": [str(path)],
                }
            ],
            options={
                "num_predict": 120,
                "temperature": 0.1,
            },
            keep_alive="10m",
        )

        message = response.get("message", {})
        description = message.get("content")

        if not isinstance(description, str):
            raise ValueError("Vision model returned no text response")

        result = multimodal_intelligence.normalize(
            modality="image",
            content={
                "type": "image_understanding",
                "path": str(path),
                "description": description.strip(),
            },
            source="vision_model",
            metadata={
                **observation["metadata"],
                "vision_model": config.VISION_MODEL,
                "prompt": prompt.strip(),
            },
        )

        return result


image_understanding = ImageUnderstanding()
