"""FRIDAY V3 - Phase 34.4 OCR / Text Extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytesseract
from PIL import Image

from proactive.multimodal_intelligence import multimodal_intelligence


class OCR:

    TESSERACT_PATH = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    def extract(
        self,
        image_path: str | Path,
        language: str = "eng",
    ) -> dict[str, Any]:
        """Extract readable text from an image using Tesseract."""

        if not isinstance(image_path, (str, Path)):
            raise TypeError("image_path must be a string or Path")

        if not isinstance(language, str):
            raise TypeError("language must be a string")

        path = Path(image_path)

        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")

        if not language.strip():
            raise ValueError("language must not be empty")

        if not self.TESSERACT_PATH.is_file():
            raise FileNotFoundError(
                f"Tesseract executable not found: {self.TESSERACT_PATH}"
            )

        pytesseract.pytesseract.tesseract_cmd = str(
            self.TESSERACT_PATH
        )

        with Image.open(path) as image:
            text = pytesseract.image_to_string(
                image,
                lang=language.strip(),
            )

        return multimodal_intelligence.normalize(
            modality="image",
            content={
                "type": "ocr",
                "path": str(path),
                "text": text.strip(),
            },
            source="tesseract_ocr",
            metadata={
                "ocr_engine": "tesseract",
                "ocr_version": str(
                    pytesseract.get_tesseract_version()
                ),
                "language": language.strip(),
            },
        )

    def validate(self, result: Any) -> bool:
        """Validate an OCR observation."""

        if not multimodal_intelligence.validate(result):
            return False

        if result.get("source") != "tesseract_ocr":
            return False

        content = result.get("content")

        if not isinstance(content, dict):
            return False

        if content.get("type") != "ocr":
            return False

        if not isinstance(content.get("text"), str):
            return False

        return True


ocr = OCR()
