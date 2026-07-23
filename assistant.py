from speech import speaker
from listen import listener
from brain import brain
from logger import logger
from gui import gui
from utils import processor
import time

class Assistant:

    def start(self):

        speaker.speak("Hello Sir. I am FRIDAY.")

        speaker.speak("Testing voice")

        while True:

            gui.set_status("Listening")

            command = listener.listen()

            if command == "":
                continue

            # Wake word required
            if not command.startswith("friday"):
                continue

            gui.add_message("🧑 You", command)

            # Remove wake word
            command = command.replace("friday", "", 1).strip()

            # User only said "Friday"
            if command == "":

                print("DEBUG: Entered wake-word block")

                speaker.speak("Yes Sir?")

                print("DEBUG: Finished speaking")

                time.sleep(1)

                gui.set_status("Listening")

                while True:

                    command = listener.listen()

                    print("Assistant received:", command)

                    if command != "":
                        break

                gui.add_message("🧑 You", command)

            logger.info(f"User: {command}")

            if command in [
                "exit",
                "quit",
                "shutdown friday",
                "goodbye",
                "stop listening"
            ]:
                speaker.speak("Goodbye Sir.")
                break

            gui.set_status("Thinking")

            command = processor.clean(command)

            running = brain.process(command)

            gui.set_status("Idle")

            if not running:
                break


assistant = Assistant()