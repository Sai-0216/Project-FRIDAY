"""
Project FRIDAY
Screenshot Module
"""

from PIL import ImageGrab
from datetime import datetime
import os


class Screenshot:

    def take(self):

        folder = "screenshots"

        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"

        path = os.path.join(folder, filename)

        image = ImageGrab.grab(all_screens=True)

        image.save(path)

        return f"Screenshot saved successfully."

        
screenshot = Screenshot()

from command_manager import manager

manager.register_exact(
    "take screenshot",
    screenshot.take
)