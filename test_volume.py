from pycaw.pycaw import AudioUtilities

devices = AudioUtilities.GetSpeakers()

print(type(devices))
print("=" * 50)
print(dir(devices))