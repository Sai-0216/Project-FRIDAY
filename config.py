"""
Project FRIDAY
Configuration
"""

from pathlib import Path


class Config:

    APP_NAME = "FRIDAY"
    VERSION = "1.0.0"

    ROOT_DIR = Path(__file__).parent

    DATA_DIR = ROOT_DIR / "data"
    LOG_DIR = ROOT_DIR / "logs"
    ASSETS_DIR = ROOT_DIR / "assets"

    SPEECH_RATE = 180
    SPEECH_VOLUME = 1.0

    WAKE_WORD = "friday"

    # -----------------------------
    # AI Models
    # -----------------------------

    CONVERSATION_MODEL = "llama3.2:latest"
    VISION_MODEL = "moondream"


config = Config()