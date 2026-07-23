"""
Project FRIDAY
Speech Engine
"""

import asyncio
import edge_tts
import pygame
import tempfile
import os
import threading

from gui import gui


class SpeechEngine:

    def __init__(self):
        pygame.mixer.init()

        self.voice = "en-US-AriaNeural"
        self.is_speaking = False

    async def _speak(self, text):

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            filename = f.name

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate="-5%"
        )
        try:

            await communicate.save(filename)
        
        except Exception as e:
            print("Speech Error:",e)
            return

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        self.is_speaking = True

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        self.is_speaking = False

        pygame.mixer.music.unload()
        os.remove(filename)

    def speak(self, text):

        gui.add_message("🤖 FRIDAY", text)

        threading.Thread(
            target=lambda: asyncio.run(self._speak(text)),
            daemon=True
        ).start()

    def stop(self):

        if self.is_speaking:
            pygame.mixer.music.stop()
            self.is_speaking = False


speaker = SpeechEngine()