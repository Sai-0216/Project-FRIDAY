"""
Project FRIDAY
Logger Module
"""

from pathlib import Path
import logging


class Logger:
    """
    Handles application logging.
    """

    def __init__(self):

        self.log_folder = Path("logs")
        self.log_folder.mkdir(exist_ok=True)

        self.logger = logging.getLogger("FRIDAY")

        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler = logging.FileHandler(
            self.log_folder / "friday.log",
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)


logger = Logger()