"""
Project FRIDAY
Reminder Manager
"""

import json
import re

from pathlib import Path

from datetime import datetime, timedelta


class ReminderManager:

    def __init__(self):

        self.file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "reminders.json"
        )

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.file.exists():

            self.save([])

    # ========================================
    # LOAD
    # ========================================

    def load(self):

        try:

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):

            return []

    # ========================================
    # SAVE
    # ========================================

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

    # ========================================
    # DAILY REMINDER
    # ========================================

    def add(
        self,
        text,
        time_string
    ):

        text = text.strip()

        time_string = time_string.strip()

        if not text:

            return (
                "Please tell me what "
                "to remind you about, Sir."
            )

        try:

            datetime.strptime(
                time_string,
                "%H:%M"
            )

        except ValueError:

            return (
                "Please use a valid time "
                "like 21:00, Sir."
            )

        reminders = self.load()

        for reminder in reminders:

            if (
                reminder.get("text") == text
                and reminder.get("time") == time_string
                and reminder.get("type") == "daily"
                and reminder.get("enabled", True)
            ):

                return (
                    "That daily reminder "
                    "already exists, Sir."
                )

        reminder = {

            "id": self._next_id(
                reminders
            ),

            "text": text,

            "time": time_string,

            "type": "daily",

            "enabled": True,

            "last_triggered": None
        }

        reminders.append(
            reminder
        )

        self.save(
            reminders
        )

        return (
            f"I'll remind you every day "
            f"at {time_string}, Sir."
        )

    # ========================================
    # WEEKLY REMINDER
    # ========================================

    def add_weekly(
        self,
        text,
        time_string,
        weekday
    ):

        text = text.strip()

        time_string = time_string.strip()

        if not text:

            return (
                "Please tell me what "
                "to remind you about, Sir."
            )

        try:

            datetime.strptime(
                time_string,
                "%H:%M"
            )

        except ValueError:

            return (
                "Please use a valid time "
                "like 21:00, Sir."
            )

        try:

            weekday = int(
                weekday
            )

        except (
            ValueError,
            TypeError
        ):

            return (
                "I couldn't understand "
                "the weekday, Sir."
            )

        if not 0 <= weekday <= 6:

            return (
                "That is not a valid weekday, Sir."
            )

        weekday_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        day_name = weekday_names[
            weekday
        ]

        reminders = self.load()

        for reminder in reminders:

            if (
                reminder.get("text") == text
                and reminder.get("time") == time_string
                and reminder.get("weekday") == weekday
                and reminder.get("type") == "weekly"
                and reminder.get("enabled", True)
            ):

                return (
                    f"That weekly reminder "
                    f"already exists for "
                    f"{day_name}, Sir."
                )

        reminder = {

            "id": self._next_id(
                reminders
            ),

            "text": text,

            "time": time_string,

            "type": "weekly",

            "weekday": weekday,

            "enabled": True,

            "last_triggered": None
        }

        reminders.append(
            reminder
        )

        self.save(
            reminders
        )

        return (
            f"I'll remind you every "
            f"{day_name} at "
            f"{time_string}, Sir."
        )

    # ========================================
    # RELATIVE ONE-TIME REMINDER
    # ========================================

    def add_relative(
        self,
        text,
        amount,
        unit
    ):

        text = text.strip()

        if not text:

            return (
                "Please tell me what "
                "to remind you about, Sir."
            )

        try:

            amount = int(
                amount
            )

        except ValueError:

            return (
                "I couldn't understand "
                "the amount of time, Sir."
            )

        if amount <= 0:

            return (
                "The reminder time must "
                "be greater than zero, Sir."
            )

        now = datetime.now()

        if unit.startswith(
            "minute"
        ):

            target = (
                now
                + timedelta(
                    minutes=amount
                )
            )

        elif unit.startswith(
            "hour"
        ):

            target = (
                now
                + timedelta(
                    hours=amount
                )
            )

        else:

            return (
                "I can currently set reminders "
                "in minutes or hours, Sir."
            )

        reminders = self.load()

        reminder = {

            "id": self._next_id(
                reminders
            ),

            "text": text,

            "time": target.strftime(
                "%H:%M"
            ),

            "type": "once",

            "enabled": True,

            "last_triggered": None,

            "trigger_at": target.isoformat()
        }

        reminders.append(
            reminder
        )

        self.save(
            reminders
        )

        formatted_time = target.strftime(
            "%I:%M %p"
        )

        return (
            f"I'll remind you at "
            f"{formatted_time}, Sir."
        )

    # ========================================
    # REMOVE REMINDER
    # ========================================

    def remove(
        self,
        reminder_id
    ):

        reminders = self.load()

        for reminder in reminders:

            if reminder.get(
                "id"
            ) == reminder_id:

                reminders.remove(
                    reminder
                )

                self.save(
                    reminders
                )

                return (
                    "Reminder removed, Sir."
                )

        return (
            "I couldn't find that reminder, Sir."
        )

    # ========================================
    # REMOVE REMINDER BY NATURAL LANGUAGE
    # ========================================

    def remove_by_match(
        self,
        text,
        weekday=None
    ):

        text = text.strip().lower()

        if not text:

            return (
                "Please tell me which reminder "
                "you want me to remove, Sir."
            )

        reminders = self.load()

        requested_words = [
            word
            for word in re.findall(
                r"[a-z0-9]+",
                text
            )
            if word not in {
                "reminder",
                "remind",
                "me",
                "my"
            }
        ]

        if not requested_words:

            return (
                "Please tell me which reminder "
                "you want me to remove, Sir."
            )

        try:
            if weekday is not None:
                weekday = int(weekday)

        except (ValueError, TypeError):

            return (
                "I couldn't understand "
                "the weekday, Sir."
            )

        for reminder in reminders:

            if not reminder.get(
                "enabled",
                True
            ):
                continue

            if reminder.get(
                "type",
                "daily"
            ) != "weekly":
                continue

            if (
                weekday is not None
                and reminder.get("weekday") != weekday
            ):
                continue

            reminder_text = reminder.get(
                "text",
                ""
            ).strip().lower()

            stored_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    reminder_text
                )
            )

            if all(
                word in stored_words
                for word in requested_words
            ):

                reminders.remove(
                    reminder
                )

                self.save(
                    reminders
                )

                return (
                    f"Removed your {reminder_text} "
                    f"reminder, Sir."
                )

        return (
            "I couldn't find a matching reminder, Sir."
        )


    # ========================================
    # LIST REMINDERS
    # ========================================

    def list_all(self):

        reminders = self.load()

        active = [
            reminder
            for reminder in reminders
            if reminder.get(
                "enabled",
                True
            )
        ]

        if not active:

            return (
                "You don't have any reminders, Sir."
            )

        lines = [
            "Your reminders, Sir:"
        ]

        weekday_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        for reminder in active:

            reminder_type = reminder.get(
                "type",
                "daily"
            )

            # --------------------------------
            # ONE-TIME
            # --------------------------------

            if reminder_type == "once":

                label = "once"

            # --------------------------------
            # WEEKLY
            # --------------------------------

            elif reminder_type == "weekly":

                weekday = reminder.get(
                    "weekday"
                )

                if (
                    isinstance(
                        weekday,
                        int
                    )
                    and 0 <= weekday <= 6
                ):

                    day_name = weekday_names[
                        weekday
                    ]

                    label = (
                        f"every {day_name}"
                    )

                else:

                    label = "weekly"

            # --------------------------------
            # DAILY
            # --------------------------------

            else:

                label = "every day"

            lines.append(
                f"{reminder['id']}. "
                f"{reminder['time']} - "
                f"{reminder['text']} "
                f"({label})"
            )

        return "\n".join(
            lines
        )

    # ========================================
    # GET DUE REMINDERS
    # ========================================

    def get_due(self):

        now = datetime.now()

        current_time = now.strftime(
            "%H:%M"
        )

        today = now.date().isoformat()

        current_weekday = now.weekday()

        reminders = self.load()

        due = []

        changed = False

        for reminder in reminders:

            if not reminder.get(
                "enabled",
                True
            ):

                continue

            reminder_type = reminder.get(
                "type",
                "daily"
            )

            # =================================
            # ONE-TIME
            # =================================

            if reminder_type == "once":

                trigger_at = reminder.get(
                    "trigger_at"
                )

                if not trigger_at:

                    continue

                try:

                    target = datetime.fromisoformat(
                        trigger_at
                    )

                except ValueError:

                    continue

                if now >= target:

                    due.append(
                        reminder
                    )

                    reminder[
                        "enabled"
                    ] = False

                    reminder[
                        "last_triggered"
                    ] = today

                    changed = True

                continue

            # =================================
            # WEEKLY
            # =================================

            if reminder_type == "weekly":

                reminder_weekday = reminder.get(
                    "weekday"
                )

                if (
                    reminder_weekday
                    != current_weekday
                ):

                    continue

                if reminder.get(
                    "time"
                ) != current_time:

                    continue

                if reminder.get(
                    "last_triggered"
                ) == today:

                    continue

                due.append(
                    reminder
                )

                reminder[
                    "last_triggered"
                ] = today

                changed = True

                continue

            # =================================
            # DAILY
            # =================================

            if reminder.get(
                "time"
            ) != current_time:

                continue

            if reminder.get(
                "last_triggered"
            ) == today:

                continue

            due.append(
                reminder
            )

            reminder[
                "last_triggered"
            ] = today

            changed = True

        if changed:

            self.save(
                reminders
            )

        return due

    # ========================================
    # NEXT ID
    # ========================================

    def _next_id(
        self,
        reminders
    ):

        if not reminders:

            return 1

        return max(
            reminder.get(
                "id",
                0
            )
            for reminder in reminders
        ) + 1


reminders = ReminderManager()