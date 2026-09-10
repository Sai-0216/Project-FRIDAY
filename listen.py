"""
Project FRIDAY
Speech Listener
"""

import re
import speech_recognition as sr


class Listener:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        # ========================================
        # MICROPHONE SETTINGS
        # ========================================

        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0
        self.recognizer.non_speaking_duration = 0.8
        self.recognizer.phrase_threshold = 0.3

        # ========================================
        # MICROPHONE
        # ========================================

        self.device_index = 1

    # ========================================
    # LIST MICROPHONES
    # ========================================

    def list_microphones(self):

        try:

            microphones = (
                sr.Microphone.list_microphone_names()
            )

            for index, name in enumerate(
                microphones
            ):

                print(
                    f"[{index}] {name}"
                )

            return microphones

        except Exception as e:

            print(
                "[Microphone Error]",
                repr(e)
            )

            return []

    # ========================================
    # TEST MICROPHONE
    # ========================================

    def test_microphone(self):

        try:

            microphones = (
                sr.Microphone.list_microphone_names()
            )

            if not microphones:

                print(
                    "[Microphone Error] "
                    "No microphones detected."
                )

                return False

            if (
                self.device_index is not None
                and self.device_index >= len(
                    microphones
                )
            ):

                print(
                    "[Microphone Error] "
                    f"Invalid microphone index: "
                    f"{self.device_index}"
                )

                return False

            return True

        except Exception as e:

            print(
                "[Microphone Error]",
                repr(e)
            )

            return False

    # ========================================
    # NORMALIZE SPEECH
    # ========================================

    def normalize_speech(self, command):

        command = str(
            command
        ).lower().strip()

        if not command:
            return ""

        original = command

        # ========================================
        # BASIC SPEECH NORMALIZATION
        # ========================================

        command = re.sub(
            r"\s+",
            " ",
            command
        )

        command = command.replace(
            "p.m.",
            "pm"
        )

        command = command.replace(
            "a.m.",
            "am"
        )

        command = command.replace(
            "p.m",
            "pm"
        )

        command = command.replace(
            "a.m",
            "am"
        )

        # ========================================
        # FRIDAY-SPECIFIC RECOGNITION ERRORS
        # ========================================

        replacements = {

            # GitHub
            "guit hub": "github",
            "git hub": "github",
            "git hubb": "github",
            "gith hub": "github",
            "guitar": "github",

            # VS Code
            "vs code": "vscode",
            "vs-code": "vscode",
            "visual studio code": "vscode",
            "visual studio": "vscode",

            # Chrome
            "google chrome": "chrome",

            # Python
            "pie thon": "python",
            "pie-thon": "python",

            # Enter
            "the enter": "enter",
            "and enter": "enter",

            # Wait
            "waits": "wait",
            "waited": "wait",
            "weights": "wait",
        }

        for wrong, correct in replacements.items():

            command = command.replace(
                wrong,
                correct
            )

        # ========================================
        # WORKFLOW PHRASE NORMALIZATION
        # ========================================

        command = re.sub(
            r"\bprocess\s+enter\b",
            "press enter",
            command
        )

        command = re.sub(
            r"\bpress\s+the\s+enter\b",
            "press enter",
            command
        )

        command = re.sub(
            r"\bpush\s+enter\b",
            "press enter",
            command
        )

        # ========================================
        # WAIT COMMANDS
        # ========================================

        command = re.sub(
            r"\boperates?\s+(?:to|two)\s+second[s]?\b",
            "wait 2 seconds",
            command
        )

        command = re.sub(
            r"\bwaits?\s+(?:to|two)\s+second[s]?\b",
            "wait 2 seconds",
            command
        )

        command = re.sub(
            r"\bwait\s+(?:to|two)\s+second[s]?\b",
            "wait 2 seconds",
            command
        )

        # ========================================
        # NUMBER RECOGNITION
        # ========================================

        number_words = {

            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
        }

        for word, number in number_words.items():

            command = re.sub(
                rf"\b{word}\s+seconds?\b",
                f"{number} seconds",
                command
            )

        # ========================================
        # WORKFLOW "THEN"
        # ========================================

        command = re.sub(
            r"\bthen\s+open\b",
            "then open",
            command
        )

        command = re.sub(
            r"\bthen\s+type\b",
            "then type",
            command
        )

        command = re.sub(
            r"\bthen\s+press\b",
            "then press",
            command
        )

        # ========================================
        # CLEAN UP
        # ========================================

        command = re.sub(
            r"\s+",
            " ",
            command
        ).strip()

        # ========================================
        # NORMALIZATION DEBUG
        # ========================================

        if command != original:

            print(
                f"Normalized: {command}"
            )

        return command

    # ========================================
    # LISTEN FOR SHORT CONFIRMATION
    # ========================================

    def listen_confirmation(self):

        try:

            # --------------------------------
            # Check microphone
            # --------------------------------

            if not self.test_microphone():

                return ""

            # --------------------------------
            # Open microphone
            # --------------------------------

            with sr.Microphone(
                device_index=self.device_index
            ) as source:

                # Short responses such as:
                # yes / no / yep / nope

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.3
                )

                # Save normal settings so confirmation
                # mode does not permanently change them.

                old_pause = self.recognizer.pause_threshold
                old_phrase = self.recognizer.phrase_threshold
                old_non_speaking = (
                    self.recognizer.non_speaking_duration
                )

                try:

                    self.recognizer.pause_threshold = 0.35
                    self.recognizer.phrase_threshold = 0.05
                    self.recognizer.non_speaking_duration = 0.2

                    audio = self.recognizer.listen(
                        source,
                        timeout=10,
                        phrase_time_limit=3
                    )

                finally:

                    self.recognizer.pause_threshold = old_pause
                    self.recognizer.phrase_threshold = old_phrase
                    self.recognizer.non_speaking_duration = old_non_speaking

            # --------------------------------
            # Recognition
            # --------------------------------

            command = self.recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            print(
                f"Confirmation heard: {command}"
            )

            # --------------------------------
            # Normalize
            # --------------------------------

            return self.normalize_speech(
                command
            )

        except sr.WaitTimeoutError:

            return ""

        except sr.UnknownValueError:

            print(
                "[Confirmation] Google could not understand the audio."
            )

            return ""

        except sr.RequestError as e:

            print(
                "[Confirmation Recognition Error]",
                repr(e)
            )

            return ""

        except Exception as e:

            print(
                "[Confirmation Listener Error]",
                repr(e)
            )

            return ""

    # ========================================
    # LISTEN
    # ========================================

    def listen(self):

        try:

            # --------------------------------
            # Check microphone
            # --------------------------------

            if not self.test_microphone():

                return ""

            # --------------------------------
            # Open microphone
            # --------------------------------

            with sr.Microphone(
                device_index=self.device_index
            ) as source:

                # No noisy "Listening..." logs.

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=15
                )

            # --------------------------------
            # Recognition
            # --------------------------------

            command = self.recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            print(
                f"You: {command}"
            )

            # --------------------------------
            # Normalize
            # --------------------------------

            command = self.normalize_speech(
                command
            )

            if not command:

                return ""

            return command

        # ====================================
        # NO SPEECH
        # ====================================

        except sr.WaitTimeoutError:

            return ""

        # ====================================
        # SPEECH NOT UNDERSTOOD
        # ====================================

        except sr.UnknownValueError:

            return ""

        # ====================================
        # GOOGLE ERROR
        # ====================================

        except sr.RequestError as e:

            print(
                "[Speech Recognition Error]",
                repr(e)
            )

            return ""

        # ====================================
        # OTHER ERROR
        # ====================================

        except Exception as e:

            print(
                "[Listener Error]",
                repr(e)
            )

            return ""


# ========================================
# GLOBAL LISTENER
# ========================================

listener = Listener()