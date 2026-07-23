from command_manager import manager
from pycaw.pycaw import AudioUtilities


class Volume:

    def __init__(self):
        self.volume = AudioUtilities.GetSpeakers().EndpointVolume

    def volume_up(self):
        current = self.volume.GetMasterVolumeLevelScalar()
        self.volume.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None)
        return "Volume increased."

    def volume_down(self):
        current = self.volume.GetMasterVolumeLevelScalar()
        self.volume.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None)
        return "Volume decreased."

    def mute(self):
        self.volume.SetMute(1, None)
        return "Muted."

    def unmute(self):
        self.volume.SetMute(0, None)
        return "Unmuted."

    def set_volume(self, level):
        try:
            level = int(level)

            if not 0 <= level <= 100:
                return "Volume should be between 0 and 100."

            self.volume.SetMasterVolumeLevelScalar(level / 100, None)
            return f"Volume set to {level} percent."

        except ValueError:
            return "Please provide a valid number."


volume = Volume()

manager.register_exact("volume up", volume.volume_up)
manager.register_exact("volume down", volume.volume_down)
manager.register_exact("mute", volume.mute)
manager.register_exact("unmute", volume.unmute)

manager.register_prefix("set volume ", volume.set_volume)