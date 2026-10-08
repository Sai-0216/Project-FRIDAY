"""
Project FRIDAY
Multi-Turn Slot Filling
Phase 35.8
"""


from proactive.slot_validation import slot_validator


class SlotFiller:
    """Schema-driven multi-turn required-slot filling."""

    REQUIRED_SLOTS = {
        "run_workflow": ("workflow",),
        "create_workflow": ("workflow", "description"),
        "add_to_workflow": ("workflow", "description"),
        "remove_from_workflow": ("workflow", "target"),
        "edit_workflow": ("workflow", "description"),
        "show_workflow": ("workflow",),
        "delete_workflow": ("workflow",),
        "open_browser": ("url",),
        "open_app": ("app",),
        "close_app": ("app",),
        "open_folder": ("location",),
        "create_folder": ("name",),
        "create_file": ("name",),
        "open_file": ("path",),
        "remember": ("text",),
        "recall": ("text",),
        "add_habit": ("habit",),
        "complete_habit": ("habit",),
        "delete_habit": ("habit",),
        "habit_progress": ("habit",),
        "add_routine": ("period", "task"),
        "remove_routine": ("period", "task"),
        "add_reminder": ("text", "time"),
        "add_weekly_reminder": ("text", "time", "weekday"),
        "add_relative_reminder": ("text", "amount", "unit"),
    }

    CANCEL_PHRASES = {
        "cancel",
        "never mind",
        "nevermind",
        "stop",
        "forget it",
    }

    def __init__(self):
        self.validator = slot_validator
        self.clear()

    def clear(self):
        self.pending_intent = None
        self.pending_parameters = {}
        self.pending_slots = []

    def required_slots(self, intent):
        return tuple(
            self.REQUIRED_SLOTS.get(
                intent,
                ()
            )
        )

    def missing_slots(self, intent, parameters=None):
        parameters = dict(parameters or {})

        return [
            slot
            for slot in self.required_slots(intent)
            if not self._has_value(
                parameters.get(slot)
            )
        ]

    def _has_value(self, value):
        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        return True

    def _is_fill_candidate(self, command):
        if command is None:
            return False

        text = str(command).strip()

        if not text:
            return False

        return text.lower() not in self.CANCEL_PHRASES

    def arm(self, intent, parameters=None):
        parameters = dict(parameters or {})

        missing = self.missing_slots(
            intent,
            parameters,
        )

        if not missing:
            self.clear()
            return []

        self.pending_intent = intent
        self.pending_parameters = parameters
        self.pending_slots = list(missing)

        return list(missing)

    def restore_pending(
        self,
        intent,
        parameters=None,
        missing_slots=None,
    ):
        parameters = dict(parameters or {})
        missing = list(missing_slots or [])

        if not intent or not missing:
            self.clear()
            return []

        self.pending_intent = intent
        self.pending_parameters = parameters
        self.pending_slots = missing

        return list(missing)

    def has_pending(self):
        return bool(
            self.pending_intent
            and self.pending_slots
        )

    def resolve(
        self,
        command,
        current_intent,
        current_parameters=None,
        previous_intent=None,
        previous_parameters=None,
    ):
        current_parameters = dict(
            current_parameters or {}
        )

        if not self.has_pending():
            return {
                "intent": current_intent,
                "parameters": current_parameters,
                "filled": {},
                "filled_slot": None,
                "missing": self.missing_slots(
                    current_intent,
                    current_parameters,
                ),
                "continued": False,
            }

        if (
            command is not None
            and str(command).strip().lower()
            in self.CANCEL_PHRASES
        ):
            self.clear()

            return {
                "intent": current_intent,
                "parameters": current_parameters,
                "filled": {},
                "filled_slot": None,
                "missing": [],
                "continued": False,
                "cancelled": True,
            }

        pending_intent = self.pending_intent
        pending_parameters = dict(
            self.pending_parameters
        )

        if (
            current_intent
            and current_intent != "unknown"
            and current_intent != pending_intent
        ):
            self.clear()

            return {
                "intent": current_intent,
                "parameters": current_parameters,
                "filled": {},
                "filled_slot": None,
                "missing": self.missing_slots(
                    current_intent,
                    current_parameters,
                ),
                "continued": False,
            }

        merged = dict(pending_parameters)
        merged.update(current_parameters)

        missing = self.missing_slots(
            pending_intent,
            merged,
        )

        if not missing:
            self.clear()

            return {
                "intent": pending_intent,
                "parameters": merged,
                "filled": {},
                "filled_slot": None,
                "missing": [],
                "continued": True,
            }

        slot = missing[0]

        if self._is_fill_candidate(command):
            raw_value = str(command).strip()

            validation = self.validator.validate(
                pending_intent,
                slot,
                raw_value,
            )

            if not validation["valid"]:
                return {
                    "intent": pending_intent,
                    "parameters": merged,
                    "filled": {},
                    "filled_slot": None,
                    "missing": missing,
                    "continued": True,
                    "validation": validation,
                }

            value = validation["value"]
            merged[slot] = value

            remaining = self.missing_slots(
                pending_intent,
                merged,
            )

            if remaining:
                self.arm(
                    pending_intent,
                    merged,
                )
            else:
                self.clear()

            return {
                "intent": pending_intent,
                "parameters": merged,
                "filled": {
                    slot: value,
                },
                "filled_slot": slot,
                "missing": remaining,
                "continued": True,
                "validation": validation,
            }

        return {
            "intent": pending_intent,
            "parameters": merged,
            "filled": {},
            "filled_slot": None,
            "missing": missing,
            "continued": True,
        }

    def snapshot(self):
        return {
            "required_intents": {
                intent: tuple(slots)
                for intent, slots
                in self.REQUIRED_SLOTS.items()
            },
            "pending_intent": self.pending_intent,
            "pending_parameters": dict(
                self.pending_parameters
            ),
            "pending_slots": list(
                self.pending_slots
            ),
        }


slot_filler = SlotFiller()
