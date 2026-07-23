import threading
import ctypes
import sys

from assistant import assistant
from gui import gui

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        "main.py",
        None,
        1
    )
    sys.exit()
def start_assistant():
    assistant.start()


threading.Thread(
    target=start_assistant,
    daemon=True
).start()

gui.run()