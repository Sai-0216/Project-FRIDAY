"""
Project FRIDAY
Plugin Loader
"""

import importlib
import os


class PluginLoader:

    def __init__(self):

        self.loaded = False
        self.loaded_plugins = []

    # ========================================
    # LOAD PLUGINS
    # ========================================

    def load_plugins(self):

        if self.loaded:

            return

        self.loaded = True

        folder = "modules"

        # ----------------------------------------
        # Check modules folder
        # ----------------------------------------

        if not os.path.isdir(folder):

            print(
                "[FRIDAY] Plugin folder not found."
            )

            return

        # ----------------------------------------
        # Load modules
        # ----------------------------------------

        for file in sorted(
            os.listdir(folder)
        ):

            if not file.endswith(".py"):

                continue

            if file == "__init__.py":

                continue

            module_name = (
                f"modules.{file[:-3]}"
            )

            try:

                importlib.import_module(
                    module_name
                )

                self.loaded_plugins.append(
                    module_name
                )

            except Exception as e:

                print(
                    f"[Plugin Error] "
                    f"{module_name}: {e}"
                )

        # ----------------------------------------
        # Clean startup message
        # ----------------------------------------

        print(
            f"[FRIDAY] "
            f"{len(self.loaded_plugins)} plugins loaded."
        )


# ========================================
# GLOBAL LOADER
# ========================================

loader = PluginLoader()