import pyttsx3
import time

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    engine.setProperty("volume", 1.0)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

speak("Hello Sir")
time.sleep(1)

speak("Testing voice")
time.sleep(1)

speak("Yes Sir")