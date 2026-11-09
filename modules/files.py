"""
Project FRIDAY
File & Folder Controller
"""

import os
from pathlib import Path


class FileManager:

    # ========================================
    # WINDOWS USER DIRECTORIES
    # ========================================

    HOME = Path.home()

    ONEDRIVE = Path(
        os.environ.get(
            "OneDrive",
            ""
        )
    )

    # ========================================
    # LOCATION BUILDER
    # ========================================

    @classmethod
    def _location_paths(
        cls,
        name
    ):

        paths = []

        # ----------------------------------------
        # Normal Windows location
        # ----------------------------------------

        normal = cls.HOME / name

        paths.append(
            normal
        )

        # ----------------------------------------
        # OneDrive location
        # ----------------------------------------

        if cls.ONEDRIVE:

            onedrive_path = (
                cls.ONEDRIVE / name
            )

            if onedrive_path not in paths:

                paths.append(
                    onedrive_path
                )

        return paths

    # ========================================
    # STANDARD LOCATIONS
    # ========================================

    LOCATIONS = {

        "desktop": "Desktop",

        "documents": "Documents",

        "downloads": "Downloads",

        "pictures": "Pictures",

        "videos": "Videos",

        "music": "Music",
    }

    # ========================================
    # RESOLVE LOCATION
    # ========================================

    def resolve_location(
        self,
        location
    ):

        location = str(
            location
        ).strip()

        if not location:

            return None

        normalized = (
            location
            .lower()
            .strip()
        )

        # ----------------------------------------
        # Standard location aliases
        # ----------------------------------------

        aliases = {

            "desktop": "desktop",
            "my desktop": "desktop",

            "documents": "documents",
            "document": "documents",
            "my documents": "documents",

            "downloads": "downloads",
            "download": "downloads",
            "my downloads": "downloads",

            "pictures": "pictures",
            "picture": "pictures",
            "photos": "pictures",

            "videos": "videos",
            "video": "videos",

            "music": "music",
            "songs": "music",
        }

        key = aliases.get(
            normalized
        )

        # ----------------------------------------
        # Search standard Windows locations
        # ----------------------------------------

        if key:

            folder_name = self.LOCATIONS.get(
                key
            )

            if folder_name:

                for path in self._location_paths(
                    folder_name
                ):

                    if path.exists():

                        print(
                            f"[Files] Resolved "
                            f"{location} -> {path}"
                        )

                        return path

                return None

        # ========================================
        # DIRECT PATH
        # ========================================

        expanded = os.path.expandvars(
            os.path.expanduser(
                location
            )
        )

        path = Path(
            expanded
        )

        if path.exists():

            return path

        # ========================================
        # RELATIVE PATH
        # ========================================

        relative = Path.cwd() / location

        if relative.exists():

            return relative

        return None

    # ========================================
    # OPEN FOLDER
    # ========================================

    def open_folder(
        self,
        location
    ):

        path = self.resolve_location(
            location
        )

        if path is None:

            return (
                f"Sorry Sir, I couldn't find "
                f"{location}."
            )

        try:

            os.startfile(
                str(path)
            )

            return (
                f"Opening {location}, Sir."
            )

        except Exception as e:

            print(
                "[Files] Open folder error:",
                repr(e)
            )

            return (
                f"Sorry Sir, I couldn't open "
                f"{location}."
            )

    # ========================================
    # CREATE FOLDER
    # ========================================

    def create_folder(
        self,
        name,
        location="desktop"
    ):

        name = str(
            name
        ).strip()

        if not name:

            return (
                "Please tell me the folder name, Sir."
            )

        base = self.resolve_location(
            location
        )

        if base is None:

            return (
                f"Sorry Sir, I couldn't find "
                f"{location}."
            )

        folder = base / name

        try:

            if folder.exists():

                return (
                    f"The folder {name} "
                    "already exists, Sir."
                )

            folder.mkdir(
                parents=True,
                exist_ok=False
            )

            return (
                f"Created the folder "
                f"{name}, Sir."
            )

        except Exception as e:

            print(
                "[Files] Create folder error:",
                repr(e)
            )

            return (
                f"Sorry Sir, I couldn't create "
                f"the folder {name}."
            )

    # ========================================
    # CREATE FILE
    # ========================================

    def create_file(
        self,
        name,
        location="desktop"
    ):

        name = str(
            name
        ).strip()

        if not name:

            return (
                "Please tell me the file name, Sir."
            )

        base = self.resolve_location(
            location
        )

        if base is None:

            return (
                f"Sorry Sir, I couldn't find "
                f"{location}."
            )

        file_path = base / name

        try:

            if file_path.exists():

                return (
                    f"The file {name} "
                    "already exists, Sir."
                )

            file_path.touch()

            return (
                f"Created the file "
                f"{name}, Sir."
            )

        except Exception as e:

            print(
                "[Files] Create file error:",
                repr(e)
            )

            return (
                f"Sorry Sir, I couldn't create "
                f"the file {name}."
            )

    # ========================================
    # OPEN FILE
    # ========================================

    def open_file(
        self,
        path
    ):

        path = Path(
            os.path.expandvars(
                os.path.expanduser(
                    str(path).strip()
                )
            )
        )

        if not path.exists():

            return (
                f"Sorry Sir, I couldn't find "
                f"{path.name}."
            )

        try:

            os.startfile(
                str(path)
            )

            return (
                f"Opening {path.name}, Sir."
            )

        except Exception as e:

            print(
                "[Files] Open file error:",
                repr(e)
            )

            return (
                f"Sorry Sir, I couldn't open "
                f"{path.name}."
            )


# ========================================
# GLOBAL FILE MANAGER
# ========================================

files = FileManager()