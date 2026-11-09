"""
Project FRIDAY
Daily Routine Manager
"""

import json
from pathlib import Path
from datetime import date


class RoutineManager:

    def __init__(self):

        self.file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "routine.json"
        )

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.file.exists():
            self.save({
                "morning": [],
                "evening": []
            })

    # ----------------------------------------
    # Load
    # ----------------------------------------

    def load(self):

        try:

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):

            return {
                "morning": [],
                "evening": []
            }

    # ----------------------------------------
    # Save
    # ----------------------------------------

    def save(self, data):

        with open(
            self.file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ----------------------------------------
    # Add Routine Item
    # ----------------------------------------

    def add(
        self,
        period,
        task
    ):

        period = period.lower().strip()
        task = task.strip()

        if period not in [
            "morning",
            "evening"
        ]:

            return (
                "I can only add morning or evening "
                "routine items, Sir."
            )

        if not task:

            return (
                "Please tell me what you want "
                "to add to your routine, Sir."
            )

        data = self.load()

        # Prevent duplicates

        if task in data[period]:

            return (
                f"{task} is already in your "
                f"{period} routine, Sir."
            )

        data[period].append(task)

        self.save(data)

        return (
            f"I added {task} to your "
            f"{period} routine, Sir."
        )

    # ----------------------------------------
    # Remove Routine Item
    # ----------------------------------------

    def remove(
        self,
        period,
        task
    ):

        period = period.lower().strip()
        task = task.strip()

        data = self.load()

        if period not in data:

            return (
                "I couldn't find that routine, Sir."
            )

        if task not in data[period]:

            return (
                f"{task} isn't in your "
                f"{period} routine, Sir."
            )

        data[period].remove(task)

        self.save(data)

        return (
            f"I removed {task} from your "
            f"{period} routine, Sir."
        )

    # ----------------------------------------
    # Get Routine
    # ----------------------------------------

    def get(
        self,
        period
    ):

        period = period.lower().strip()

        data = self.load()

        if period not in data:

            return (
                "I couldn't find that routine, Sir."
            )

        tasks = data[period]

        if not tasks:

            return (
                f"Your {period} routine is empty, Sir."
            )

        lines = []

        for index, task in enumerate(
            tasks,
            start=1
        ):

            lines.append(
                f"{index}. {task}"
            )

        return (
            f"Your {period} routine, Sir:\n"
            + "\n".join(lines)
        )

    # ----------------------------------------
    # Full Routine
    # ----------------------------------------

    def full_routine(self):

        data = self.load()

        lines = []

        morning = data.get(
            "morning",
            []
        )

        evening = data.get(
            "evening",
            []
        )

        if morning:

            lines.append(
                "🌅 Morning:"
            )

            for task in morning:

                lines.append(
                    f"• {task}"
                )

        if evening:

            lines.append(
                "\n🌙 Evening:"
            )

            for task in evening:

                lines.append(
                    f"• {task}"
                )

        if not lines:

            return (
                "You don't have a routine yet, Sir."
            )

        return "\n".join(lines)


routine = RoutineManager()