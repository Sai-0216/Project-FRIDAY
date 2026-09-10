"""
Project FRIDAY
Camera Controller
"""

import cv2
import threading
from datetime import datetime
from pathlib import Path

from command_manager import manager


class Camera:

    def __init__(self):

        self.cap = None
        self.running = False
        self.thread = None

        # Protect camera state
        self.lock = threading.Lock()

        # Latest frame from camera
        self.latest_frame = None

    # ----------------------------------------
    # Open Camera
    # ----------------------------------------

    def open_camera(self):

        with self.lock:

            if self.running:

                return "Camera is already open."

            self.cap = cv2.VideoCapture(
                0,
                cv2.CAP_DSHOW
            )

            if not self.cap.isOpened():

                self.cap.release()

                self.cap = None

                return "Couldn't open the camera."

            self.running = True

            self.latest_frame = None

        self.thread = threading.Thread(
            target=self._camera_loop,
            daemon=True
        )

        self.thread.start()

        return "Camera opened."

    # ----------------------------------------
    # Camera Loop
    # ----------------------------------------

    def _camera_loop(self):

        window_name = "FRIDAY Camera"

        try:

            while self.running:

                # --------------------------------
                # Get camera frame
                # --------------------------------

                with self.lock:

                    if self.cap is None:

                        break

                    ret, frame = self.cap.read()

                    if ret:

                        self.latest_frame = (
                            frame.copy()
                        )

                # --------------------------------
                # Camera read failed
                # --------------------------------

                if not ret:

                    print(
                        "[CAMERA] Couldn't grab frame."
                    )

                    break

                # --------------------------------
                # Show camera
                # --------------------------------

                cv2.imshow(
                    window_name,
                    frame
                )

                # --------------------------------
                # Process window events
                # --------------------------------

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                # --------------------------------
                # Q closes camera
                # --------------------------------

                if key == ord("q"):

                    print(
                        "[CAMERA] Q pressed."
                    )

                    self.running = False

                    break

                # --------------------------------
                # X button closes camera
                # --------------------------------

                try:

                    visible = cv2.getWindowProperty(
                        window_name,
                        cv2.WND_PROP_VISIBLE
                    )

                    if visible < 1:

                        print(
                            "[CAMERA] Window closed."
                        )

                        self.running = False

                        break

                except cv2.error:

                    self.running = False

                    break

        except Exception as e:

            print(
                f"[CAMERA] Error: {e}"
            )

            self.running = False

        finally:

            self._cleanup()

    # ----------------------------------------
    # Close Camera
    # ----------------------------------------

    def close_camera(self):

        with self.lock:

            if not self.running:

                return "Camera is already closed."

            self.running = False

        # ----------------------------------------
        # Wait for camera thread
        # ----------------------------------------

        if (
            self.thread
            and self.thread.is_alive()
            and self.thread != threading.current_thread()
        ):

            self.thread.join(
                timeout=1
            )

        self._cleanup()

        return "Camera closed."

    # ----------------------------------------
    # Cleanup
    # ----------------------------------------

    def _cleanup(self):

        with self.lock:

            cap = self.cap

            self.cap = None

            self.latest_frame = None

        # ----------------------------------------
        # Release camera
        # ----------------------------------------

        if cap is not None:

            try:

                cap.release()

            except Exception:

                pass

        # ----------------------------------------
        # Close OpenCV windows
        # ----------------------------------------

        try:

            cv2.destroyWindow(
                "FRIDAY Camera"
            )

        except cv2.error:

            pass

        try:

            cv2.destroyAllWindows()

        except cv2.error:

            pass

    # ----------------------------------------
    # Take Photo
    # ----------------------------------------

    def take_photo(self):

        frame = None

        # ========================================
        # CAMERA ALREADY OPEN
        # ========================================

        with self.lock:

            if (
                self.running
                and self.cap is not None
            ):

                # --------------------------------
                # Use latest preview frame
                #
                # IMPORTANT:
                # Do NOT open another VideoCapture.
                # --------------------------------

                if self.latest_frame is not None:

                    frame = (
                        self.latest_frame.copy()
                    )

                else:

                    # If the preview hasn't received
                    # a frame yet, capture one using
                    # the existing camera.
                    ret, captured = (
                        self.cap.read()
                    )

                    if ret:

                        frame = captured.copy()

        # ========================================
        # CAMERA WAS NOT OPEN
        # ========================================

        if frame is None:

            temp_cap = cv2.VideoCapture(
                0,
                cv2.CAP_DSHOW
            )

            if not temp_cap.isOpened():

                temp_cap.release()

                return (
                    "Couldn't open the camera."
                )

            try:

                ret, captured = (
                    temp_cap.read()
                )

                if not ret:

                    return (
                        "Couldn't capture the photo."
                    )

                frame = captured.copy()

            finally:

                temp_cap.release()

        # ========================================
        # SAVE PHOTO
        # ========================================

        try:

            photos_dir = (
                Path(__file__)
                .resolve()
                .parent.parent
                / "data"
                / "photos"
            )

            photos_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            filename = datetime.now().strftime(
                "photo_%Y%m%d_%H%M%S.jpg"
            )

            filepath = (
                photos_dir
                / filename
            )

            success = cv2.imwrite(
                str(filepath),
                frame
            )

            if not success:

                return (
                    "I couldn't save the photo."
                )

            return (
                f"Photo saved as {filepath}"
            )

        except Exception as e:

            print(
                f"[CAMERA] Photo error: {e}"
            )

            return (
                "Couldn't save the photo."
            )


# ----------------------------------------
# Camera Instance
# ----------------------------------------

camera = Camera()


# ----------------------------------------
# Command Manager
# ----------------------------------------

manager.register_exact(
    "open camera",
    camera.open_camera
)

manager.register_exact(
    "close camera",
    camera.close_camera
)

manager.register_exact(
    "take photo",
    camera.take_photo
)

manager.register_exact(
    "capture photo",
    camera.take_photo
)