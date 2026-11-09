"""
Project FRIDAY
Habit Tracker
"""

import json
from pathlib import Path
from datetime import date, timedelta


class HabitTracker:

    def __init__(self):

        self.file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "habits.json"
        )

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.file.exists():
            self.save({})

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

            return {}

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
    # Add Habit
    # ----------------------------------------

    def add(self, name):

        name = name.strip().lower()

        if not name:
            return "Please tell me the habit name, Sir."

        data = self.load()

        if name in data:
            return f"You already have a {name} habit, Sir."

        data[name] = {
            "created": date.today().isoformat(),
            "last_completed": None,
            "streak": 0,
            "total_completed": 0
        }

        self.save(data)

        return f"I added {name} to your habits, Sir."

    # ----------------------------------------
    # Complete Habit
    # ----------------------------------------

    def complete(self, name):

        name = name.strip().lower()

        data = self.load()

        if name not in data:
            return f"I couldn't find a {name} habit, Sir."

        today = date.today()
        today_string = today.isoformat()

        habit = data[name]

        # Already completed today
        if habit["last_completed"] == today_string:

            return (
                f"You already completed {name} today, Sir. "
                f"Your streak is {habit['streak']} days."
            )

        # Calculate streak
        last_completed = habit["last_completed"]

        if last_completed:

            last_date = date.fromisoformat(
                last_completed
            )

            difference = (
                today - last_date
            ).days

            if difference == 1:

                habit["streak"] += 1

            else:

                habit["streak"] = 1

        else:

            habit["streak"] = 1

        habit["last_completed"] = today_string
        habit["total_completed"] += 1

        self.save(data)

        return (
            f"Nice work, Sir. {name} completed. "
            f"Your streak is {habit['streak']} days."
        )

    # ----------------------------------------
    # List Habits
    # ----------------------------------------

    def list_today(self):

        data = self.load()

        if not data:
            return (
                "You don't have any habits yet, Sir."
            )

        today = date.today().isoformat()

        lines = []

        for name, habit in data.items():

            if habit["last_completed"] == today:

                status = "✅"

            else:

                status = "⬜"

            lines.append(
                f"{status} {name} "
                f"(streak: {habit['streak']})"
            )

        return (
            "Your habits today, Sir:\n"
            + "\n".join(lines)
        )

    # ----------------------------------------
    # Habit Progress
    # ----------------------------------------

    def progress(self, name):

        name = name.strip().lower()

        data = self.load()

        if name not in data:

            return (
                f"I couldn't find a {name} habit, Sir."
            )

        habit = data[name]

        today = date.today().isoformat()

        completed = (
            habit["last_completed"] == today
        )

        status = (
            "completed today"
            if completed
            else "not completed today"
        )

        return (
            f"{name}: {habit['streak']} day streak, "
            f"{habit['total_completed']} total completions, "
            f"{status}."
        )

    # ----------------------------------------
    # Delete Habit
    # ----------------------------------------

    def delete(self, name):

        name = name.strip().lower()

        data = self.load()

        if name not in data:

            return (
                f"I couldn't find a {name} habit, Sir."
            )

        del data[name]

        self.save(data)

        return (
            f"I removed the {name} habit, Sir."
        )


habit_tracker = HabitTracker()