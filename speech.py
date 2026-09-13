"""
Project FRIDAY
Speech Engine
"""

import asyncio
import os
import tempfile
import threading

import edge_tts
import pygame

from gui import gui


class SpeechEngine:

    def __init__(self):

        # ========================================
        # AUDIO INITIALIZATION
        # ========================================

        pygame.mixer.init()

        pygame.mixer.music.set_volume(
            1.0
        )

        # ========================================
        # VOICE
        # ========================================

        self.voice = "en-US-AriaNeural"

        self.is_speaking = False

        # ========================================
        # THREAD / AUDIO CONTROL
        # ========================================

        self.speech_lock = threading.Lock()

        self.stop_event = threading.Event()

        # ========================================
        # NETWORK RETRY SETTINGS
        # ========================================

        self.max_retries = 3

        self.retry_delay = 1.5

    # ========================================
    # INTERNAL SPEECH ENGINE
    # ========================================

    async def _speak(
        self,
        text
    ):

        filename = None

        try:

            # ====================================
            # CREATE TEMPORARY AUDIO FILE
            # ====================================

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            ) as f:

                filename = f.name

            # ====================================
            # EDGE TTS WITH RETRIES
            # ====================================

            last_error = None

            for attempt in range(
                1,
                self.max_retries + 1
            ):

                if self.stop_event.is_set():

                    return

                try:

                    print(
                        f"[Speech] TTS attempt "
                        f"{attempt}/{self.max_retries}"
                    )

                    communicate = edge_tts.Communicate(
                        text=text,
                        voice=self.voice,
                        rate="-5%"
                    )

                    await communicate.save(
                        filename
                    )

                    # --------------------------------
                    # Validate generated audio
                    # --------------------------------

                    if (
                        not os.path.exists(
                            filename
                        )
                        or os.path.getsize(
                            filename
                        ) == 0
                    ):

                        raise RuntimeError(
                            "Edge TTS created an "
                            "empty audio file."
                        )

                    print(
                        "[Speech] TTS audio created."
                    )

                    break

                except Exception as e:

                    last_error = e

                    print(
                        "[Speech] TTS attempt "
                        f"{attempt} failed:",
                        repr(e)
                    )

                    # ----------------------------
                    # Don't retry after final try
                    # ----------------------------

                    if attempt >= self.max_retries:

                        raise last_error

                    await asyncio.sleep(
                        self.retry_delay
                    )

            # ====================================
            # CHECK STOP
            # ====================================

            if self.stop_event.is_set():

                return

            # ====================================
            # PLAY AUDIO
            # ====================================

            with self.speech_lock:

                pygame.mixer.music.load(
                    filename
                )

                pygame.mixer.music.set_volume(
                    1.0
                )

                self.is_speaking = True

                pygame.mixer.music.play()

            # ====================================
            # WAIT FOR PLAYBACK
            # ====================================

            while pygame.mixer.music.get_busy():

                if self.stop_event.is_set():

                    pygame.mixer.music.stop()

                    break

                await asyncio.sleep(
                    0.05
                )

        except Exception as e:

            print(
                "[Speech Error]",
                repr(e)
            )

            print(
                "[Speech] Unable to generate "
                "voice audio. The command itself "
                "is not affected."
            )

        finally:

            self.is_speaking = False

            # ====================================
            # RELEASE AUDIO
            # ====================================

            try:

                pygame.mixer.music.stop()

                pygame.mixer.music.unload()

            except Exception:

                pass

            # ====================================
            # DELETE TEMP FILE
            # ====================================

            if filename:

                for _ in range(10):

                    try:

                        if os.path.exists(
                            filename
                        ):

                            os.remove(
                                filename
                            )

                        break

                    except PermissionError:

                        await asyncio.sleep(
                            0.2
                        )

                    except Exception:

                        break

    # ========================================
    # PUBLIC SPEAK
    # ========================================

    def speak(
        self,
        text
    ):

        if not text:

            return

        text = str(
            text
        ).strip()

        if not text:

            return

        # ====================================
        # SHOW FRIDAY RESPONSE IN GUI
        # ====================================

        # IMPORTANT:
        #
        # SpeechEngine is the single place where
        # spoken FRIDAY responses are displayed.
        #
        # Do NOT also add the same response from
        # assistant.py or it will appear twice.
        #

        try:

            gui.add_message_threadsafe(
                "🤖 FRIDAY",
                text
            )

        except Exception:

            # Keep speech working even if
            # the GUI is unavailable.
            pass

        # ====================================
        # STOP PREVIOUS SPEECH
        # ====================================

        self.stop()

        self.stop_event.clear()

        # ====================================
        # RUN SPEECH
        # ====================================

        def run_speech():
            try:
                asyncio.run(self._speak(text))
            except Exception as e:
                print(
                    "[Speech Error]",
                    repr(e)
                )
            finally:
                self.is_speaking = False

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            run_speech()
        else:
            threading.Thread(
                target=run_speech,
                name="FRIDAY-Speech",
                daemon=True,
            ).start()

    # ========================================
    # STOP SPEECH
    # ========================================

    def stop(self):

        try:

            self.stop_event.set()

            if pygame.mixer.music.get_busy():

                pygame.mixer.music.stop()

            self.is_speaking = False

        except Exception as e:

            print(
                "[Speech Stop Error]",
                repr(e)
            )


# ========================================
# GLOBAL SPEECH INSTANCE
# ========================================

speaker = SpeechEngine()