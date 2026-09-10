"""
Project FRIDAY
Screenshot Module
"""

from PIL import Image, ImageGrab
from datetime import datetime
import os
import ollama

from config import config


class Screenshot:

    def __init__(self):

        self.folder = "screenshots"

        os.makedirs(
            self.folder,
            exist_ok=True
        )

    # ----------------------------------------
    # Take Screenshot
    # ----------------------------------------

    def take(self):

        filename = (
            datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            + ".png"
        )

        path = os.path.join(
            self.folder,
            filename
        )

        image = ImageGrab.grab(
            all_screens=True
        )

        # Reduce screenshot size
        image.thumbnail(
            (1280, 720),
            Image.Resampling.LANCZOS
        )

        image.save(
            path,
            optimize=True
        )

        return "Screenshot saved successfully."

    # ----------------------------------------
    # Analyze Screen
    # ----------------------------------------

    def analyze(self):

        filename = (
            datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            + "_vision.jpg"
        )

        path = os.path.join(
            self.folder,
            filename
        )

        try:

            # Capture screen
            image = ImageGrab.grab(
                all_screens=True
            )

            # --------------------------------
            # Resize before sending to Vision
            # --------------------------------

            image.thumbnail(
                (1024, 576),
                Image.Resampling.LANCZOS
            )

            # --------------------------------
            # Save compressed JPEG
            # --------------------------------

            image.save(
                path,
                "JPEG",
                quality=70,
                optimize=True
            )

            print(
                "[VISION] Screenshot captured."
            )

            print(
                f"[VISION] Sending image to "
                f"{config.VISION_MODEL}..."
            )

            # --------------------------------
            # Send image to Vision model
            # --------------------------------

            response = ollama.chat(

                model=config.VISION_MODEL,

                messages=[
                    {
                        "role": "user",

                        "content": (
                            "Look at this computer screen. "
                            "Briefly tell me what is visible. "
                            "Mention the main application and "
                            "important visible content. "
                            "Use no more than 2 short sentences."
                        ),

                        "images": [path],
                    }
                ],

                options={
                    "num_predict": 40,
                    "temperature": 0.1,
                },

                # Keep the vision model loaded
                # so the next request starts faster.
                keep_alive="10m",
            )

            print(
                f"[VISION] {config.VISION_MODEL} finished."
            )

            return response["message"]["content"]

        except Exception as e:

            print(
                f"[VISION] Error: {e}"
            )

            return (
                f"Sorry Sir. Vision failed: {e}"
            )

        finally:

            # Remove temporary vision image
            if os.path.exists(path):

                try:

                    os.remove(path)

                except Exception:

                    pass


screenshot = Screenshot()