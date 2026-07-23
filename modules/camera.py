"""
Project FRIDAY
Camera Controller
"""

import cv2
from datetime import datetime
from command_manager import manager


class Camera:

    def open_camera(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return "Couldn't open the camera."

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            cv2.imshow("FRIDAY Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        return "Camera closed."

    def take_photo(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return "Couldn't open the camera."

        ret, frame = cap.read()

        if ret:

            filename = datetime.now().strftime(
                "photo_%Y%m%d_%H%M%S.jpg"
            )

            cv2.imwrite(filename, frame)

            cap.release()
            cv2.destroyAllWindows()

            return f"Photo saved as {filename}"

        cap.release()
        cv2.destroyAllWindows()

        return "Couldn't take photo."


camera = Camera()

manager.register_exact(
    "open camera",
    camera.open_camera
)

manager.register_exact(
    "take photo",
    camera.take_photo
)

manager.register_exact(
    "capture photo",
    camera.take_photo
)