"""
Project FRIDAY
Slot Validation
Phase 35.9
"""


import re


class SlotValidator:
    """Validates and normalizes values supplied for pending slots."""

    WEEKDAYS = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    UNIT_ALIASES = {
        "minute": "minutes",
        "minutes": "minutes",
        "min": "minutes",
        "mins": "minutes",
        "hour": "hours",
        "hours": "hours",
        "hr": "hours",
        "hrs": "hours",
    }

    SLOT_TYPES = {
        "workflow": "text",
        "description": "text",
        "text": "text",
        "app": "text",
        "habit": "text",
        "task": "text",
        "period": "text",
        "name": "text",
        "target": "text",
        "location": "location",
        "path": "path",
        "url": "url",
        "time": "time",
        "weekday": "weekday",
        "amount": "amount",
        "unit": "unit",
    }

    PROMPTS = {
        "time": (
            "Please give me a time like 7 PM or 19:00."
        ),
        "weekday": (
            "Please give me a weekday like Monday."
        ),
        "amount": (
            "Please give me a positive number."
        ),
        "unit": (
            "Please give me minutes or hours."
        ),
        "url": (
            "Please give me a valid website address."
        ),
        "path": (
            "Please give me a file path."
        ),
        "text": (
            "Please give me a value for that."
        ),
    }

    def expected_type(self, intent, slot):
        return self.SLOT_TYPES.get(
            slot,
            "text",
        )

    def validate(
        self,
        intent,
        slot,
        value,
    ):
        text = str(
            value
            if value is not None
            else ""
        ).strip()

        if not text:
            return self._invalid(
                slot,
                "empty_value",
            )

        slot_type = self.expected_type(
            intent,
            slot,
        )

        handlers = {
            "text": self._validate_text,
            "location": self._validate_text,
            "path": self._validate_text,
            "time": self._validate_time,
            "weekday": self._validate_weekday,
            "amount": self._validate_amount,
            "unit": self._validate_unit,
            "url": self._validate_url,
        }

        handler = handlers.get(
            slot_type,
            self._validate_text,
        )

        return handler(
            slot,
            text,
        )

    def _validate_text(
        self,
        slot,
        value,
    ):
        return {
            "valid": True,
            "value": value,
            "reason": None,
            "prompt": None,
        }

    def _validate_time(
        self,
        slot,
        value,
    ):
        text = value.lower().strip()

        match = re.fullmatch(
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)",
            text,
        )

        if match:
            hour = int(
                match.group(1)
            )
            minute = int(
                match.group(2)
                or 0
            )
            period = match.group(3)

            if not 1 <= hour <= 12:
                return self._invalid(
                    slot,
                    "invalid_time",
                )

            if not 0 <= minute <= 59:
                return self._invalid(
                    slot,
                    "invalid_time",
                )

            if period == "pm" and hour != 12:
                hour += 12

            elif period == "am" and hour == 12:
                hour = 0

            return self._valid(
                f"{hour:02d}:{minute:02d}"
            )

        match = re.fullmatch(
            r"(\d{1,2}):(\d{2})",
            text,
        )

        if match:
            hour = int(
                match.group(1)
            )
            minute = int(
                match.group(2)
            )

            if (
                0 <= hour <= 23
                and 0 <= minute <= 59
            ):
                return self._valid(
                    f"{hour:02d}:{minute:02d}"
                )

            return self._invalid(
                slot,
                "invalid_time",
            )

        match = re.fullmatch(
            r"(\d{4})",
            text,
        )

        if match:
            hour = int(
                text[:2]
            )
            minute = int(
                text[2:]
            )

            if (
                0 <= hour <= 23
                and 0 <= minute <= 59
            ):
                return self._valid(
                    f"{hour:02d}:{minute:02d}"
                )

        return self._invalid(
            slot,
            "invalid_time",
        )

    def _validate_weekday(
        self,
        slot,
        value,
    ):
        text = value.lower().strip()

        if text in self.WEEKDAYS:
            return self._valid(
                self.WEEKDAYS[text]
            )

        if re.fullmatch(
            r"\d+",
            text,
        ):
            day = int(text)

            if 0 <= day <= 6:
                return self._valid(day)

        return self._invalid(
            slot,
            "invalid_weekday",
        )

    def _validate_amount(
        self,
        slot,
        value,
    ):
        if not re.fullmatch(
            r"\d+",
            value,
        ):
            return self._invalid(
                slot,
                "invalid_amount",
            )

        amount = int(value)

        if amount <= 0:
            return self._invalid(
                slot,
                "invalid_amount",
            )

        return self._valid(amount)

    def _validate_unit(
        self,
        slot,
        value,
    ):
        unit = self.UNIT_ALIASES.get(
            value.lower().strip()
        )

        if not unit:
            return self._invalid(
                slot,
                "invalid_unit",
            )

        return self._valid(unit)

    def _validate_url(
        self,
        slot,
        value,
    ):
        text = value.strip()

        if " " in text:
            return self._invalid(
                slot,
                "invalid_url",
            )

        if not re.fullmatch(
            r"(?:https?://)?"
            r"(?:www\.)?"
            r"[A-Za-z0-9-]+"
            r"(?:\.[A-Za-z0-9-]+)+"
            r"(?:/[^\s]*)?",
            text,
        ):
            return self._invalid(
                slot,
                "invalid_url",
            )

        return self._valid(
            text
        )

    def _valid(self, value):
        return {
            "valid": True,
            "value": value,
            "reason": None,
            "prompt": None,
        }

    def _invalid(
        self,
        slot,
        reason,
    ):
        slot_type = self.expected_type(
            None,
            slot,
        )

        return {
            "valid": False,
            "value": None,
            "reason": reason,
            "prompt": self.PROMPTS.get(
                slot_type,
                self.PROMPTS["text"],
            ),
        }

    def snapshot(self):
        return {
            "slot_types": dict(
                self.SLOT_TYPES
            ),
            "weekdays": dict(
                self.WEEKDAYS
            ),
            "unit_aliases": dict(
                self.UNIT_ALIASES
            ),
        }


slot_validator = SlotValidator()
