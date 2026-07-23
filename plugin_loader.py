import importlib
import os


class PluginLoader:

    def __init__(self):
        self.loaded = False

    def load_plugins(self):

        if self.loaded:
            return

        self.loaded = True

        print("Loading plugins...")

        folder = "modules"

        for file in os.listdir(folder):

            if file.endswith(".py") and file != "__init__.py":

                module = f"modules.{file[:-3]}"

                importlib.import_module(module)

                print(f"✅ Loaded: {module}")


loader = PluginLoader()