"""
Project FRIDAY
Phase 18.9.1

Environment History Memory

Stores a bounded history of device/environment
snapshots for future trend analysis.

This module does NOT make decisions.
It only stores and retrieves environment history.
"""

import json
import threading
from datetime import datetime
from pathlib import Path


class EnvironmentMemory:

    # ========================================
    # CONFIGURATION
    # ========================================

    MAX_HISTORY = 100

    # ========================================
    # INITIALIZATION
    # ========================================

    def __init__(
        self,
        file=None,
        max_history=MAX_HISTORY
    ):

        if file is None:

            self.file = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "environment_history.json"
            )

        else:

            self.file = Path(
                file
            )

        self.max_history = int(
            max_history
        )

        self.lock = threading.RLock()

        # ----------------------------------------
        # DATA DIRECTORY
        # ----------------------------------------

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------
        # CREATE HISTORY FILE
        # ----------------------------------------

        if not self.file.exists():

            self._save_history([])

    # ========================================
    # LOAD
    # ========================================

    def _load_history(self):

        try:

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if isinstance(
                data,
                list
            ):

                return data

            return []

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):

            return []

        except Exception as e:

            print(
                "[ENVIRONMENT MEMORY] "
                f"Load error: {e}"
            )

            return []

    # ========================================
    # SAVE
    # ========================================

    def _save_history(
        self,
        history
    ):

        try:

            with open(
                self.file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    history,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except Exception as e:

            print(
                "[ENVIRONMENT MEMORY] "
                f"Save error: {e}"
            )

            return False

    # ========================================
    # RECORD
    # ========================================

    def record(
        self,
        state
    ):
        """
        Store one environment snapshot.

        A timestamp is added automatically when
        the supplied state does not already contain one.
        """

        if not isinstance(
            state,
            dict
        ):

            return False

        snapshot = dict(
            state
        )

        if not snapshot.get(
            "timestamp"
        ):

            snapshot["timestamp"] = (
                datetime.now().isoformat()
            )

        with self.lock:

            history = self._load_history()

            history.append(
                snapshot
            )

            history = history[
                -self.max_history:
            ]

            return self._save_history(
                history
            )

    # ========================================
    # HISTORY
    # ========================================

    def history(
        self,
        limit=None
    ):
        """
        Return recent environment snapshots.
        """

        with self.lock:

            history = self._load_history()

        if limit is None:

            return history

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            return []

        if limit <= 0:

            return []

        return history[
            -limit:
        ]

    # ========================================
    # LATEST
    # ========================================

    def latest(self):

        with self.lock:

            history = self._load_history()

        if not history:

            return None

        return history[-1]

    # ========================================
    # COUNT
    # ========================================

    def count(self):

        with self.lock:

            return len(
                self._load_history()
            )

    # ========================================
    # CLEAR
    # ========================================

    def clear(self):

        with self.lock:

            return self._save_history(
                []
            )


# ============================================
# ENVIRONMENT MEMORY INSTANCE
# ============================================

environment_memory = EnvironmentMemory()