"""FRIDAY V3 - Phase 34.3 Screen Understanding."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageGrab

from proactive.image_understanding import image_understanding
from proactive.multimodal_intelligence import multimodal_intelligence
from proactive.screen_awareness import screen_awareness


class ScreenUnderstanding:

    def capture(self) -> dict[str, Any]:
        """Capture and structurally describe the current screen."""

        image = ImageGrab.grab(all_screens=True)

        width, height = image.size

        return screen_awareness.capture(
            width=width,
            height=height,
            applications=[],
            elements=[],
        )

    def analyze(
        self,
        prompt: str = (
            "Look at this computer screen. "
            "Briefly describe the main application and the "
            "important visible content."
        ),
    ) -> dict[str, Any]:
        """Capture the screen and analyze it with the vision model."""

        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        if not prompt.strip():
            raise ValueError("prompt must not be empty")

        folder = Path("screenshots")
        folder.mkdir(parents=True, exist_ok=True)

        filename = (
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
            + "_screen_understanding.jpg"
        )

        path = folder / filename

        try:
            image = ImageGrab.grab(all_screens=True)

            image.thumbnail(
                (1024, 576),
                Image.Resampling.LANCZOS,
            )

            image.save(
                path,
                "JPEG",
                quality=70,
                optimize=True,
            )

            observation = image_understanding.analyze(
                path,
                prompt=prompt,
            )

            screen_state = screen_awareness.capture(
                width=image.width,
                height=image.height,
                applications=[],
                elements=[],
            )

            return {
                "screen": screen_state,
                "observation": observation,
                "aware": True,
            }

        finally:
            if path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass

    def validate(self, state: Any) -> bool:
        """Validate a structured screen observation."""

        if not isinstance(state, dict):
            return False

        if not isinstance(state.get("screen"), dict):
            return False

        if not isinstance(state.get("observation"), dict):
            return False

        if not isinstance(state.get("aware"), bool):
            return False

        if not screen_awareness.validate(state["screen"]):
            return False

        return multimodal_intelligence.validate(state["observation"])


screen_understanding = ScreenUnderstanding()
