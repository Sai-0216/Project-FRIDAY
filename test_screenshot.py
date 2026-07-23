from modules.screenshot import screenshot

try:
    path = screenshot.take()
    print("Screenshot saved at:", path)
except Exception as e:
    print("Error:", e)