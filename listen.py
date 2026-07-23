import speech_recognition as sr


class Listener:

    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Microphone sensitivity
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

        # Wait a little longer before deciding you're done speaking
        self.recognizer.pause_threshold = 1.0
        self.recognizer.non_speaking_duration = 0.8

    def listen(self):

        try:
            with sr.Microphone(device_index=1) as source:

                print("🎤 Listening...")

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                )

            print("Recognizing...")

            command = self.recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            print(f"You: {command}")

            return command.lower().strip()

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

        except sr.UnknownValueError:
            print("Couldn't understand.")
            return ""

        except sr.RequestError as e:
            print("Google Error:", e)
            return ""

        except Exception as e:
            print("Error:", e)
            return ""


listener = Listener()