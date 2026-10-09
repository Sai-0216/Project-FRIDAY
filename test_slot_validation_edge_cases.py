import unittest

from proactive.slot_validation import SlotValidator
from proactive.slot_filling import SlotFiller


class TestSlotValidationEdgeCases(unittest.TestCase):
    def setUp(self):
        self.validator = SlotValidator()

    def test_empty_and_whitespace_values_are_rejected(self):
        for value in (None, "", "   ", "\t\n"):
            with self.subTest(value=value):
                result = self.validator.validate(
                    "create_workflow", "description", value
                )
                self.assertFalse(result["valid"])
                self.assertEqual(result["reason"], "empty_value")

    def test_text_values_are_trimmed(self):
        result = self.validator.validate(
            "create_workflow", "description", "  daily report  "
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["value"], "daily report")

    def test_time_formats_are_normalized(self):
        cases = {
            "7 PM": "19:00",
            "12 AM": "00:00",
            "12 PM": "12:00",
            "09:30": "09:30",
            "1930": "19:30",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                result = self.validator.validate(
                    "add_reminder", "time", value
                )
                self.assertTrue(result["valid"])
                self.assertEqual(result["value"], expected)

    def test_invalid_times_are_rejected(self):
        for value in ("25:00", "12:99", "0 PM", "13 PM", "noon"):
            with self.subTest(value=value):
                result = self.validator.validate(
                    "add_reminder", "time", value
                )
                self.assertFalse(result["valid"])
                self.assertEqual(result["reason"], "invalid_time")

    def test_weekdays_normalize_to_integer_values(self):
        cases = {
            "Monday": 0,
            "Friday": 4,
            "sunday": 6,
            "0": 0,
            "6": 6,
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                result = self.validator.validate(
                    "add_weekly_reminder", "weekday", value
                )
                self.assertTrue(result["valid"])
                self.assertEqual(result["value"], expected)

    def test_invalid_weekdays_are_rejected(self):
        for value in ("Funday", "7", "-1"):
            with self.subTest(value=value):
                result = self.validator.validate(
                    "add_weekly_reminder", "weekday", value
                )
                self.assertFalse(result["valid"])
                self.assertEqual(result["reason"], "invalid_weekday")

    def test_amount_requires_a_positive_integer(self):
        for value, expected in (("1", 1), ("25", 25)):
            with self.subTest(value=value):
                result = self.validator.validate(
                    "add_relative_reminder", "amount", value
                )
                self.assertTrue(result["valid"])
                self.assertEqual(result["value"], expected)

        for value in ("0", "-1", "1.5", "abc"):
            with self.subTest(value=value):
                result = self.validator.validate(
                    "add_relative_reminder", "amount", value
                )
                self.assertFalse(result["valid"])
                self.assertEqual(result["reason"], "invalid_amount")

    def test_unit_aliases_are_normalized(self):
        cases = {
            "min": "minutes",
            "mins": "minutes",
            "minute": "minutes",
            "hr": "hours",
            "hrs": "hours",
            "hour": "hours",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                result = self.validator.validate(
                    "add_relative_reminder", "unit", value
                )
                self.assertTrue(result["valid"])
                self.assertEqual(result["value"], expected)

        result = self.validator.validate(
            "add_relative_reminder", "unit", "days"
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_unit")

    def test_urls_are_validated(self):
        for value in ("example.com", "https://example.com", "www.example.com"):
            with self.subTest(value=value):
                result = self.validator.validate(
                    "open_browser", "url", value
                )
                self.assertTrue(result["valid"])

        for value in ("not a url", "localhost", "http://"):
            with self.subTest(value=value):
                result = self.validator.validate(
                    "open_browser", "url", value
                )
                self.assertFalse(result["valid"])
                self.assertEqual(result["reason"], "invalid_url")

    def test_invalid_followup_preserves_pending_slot(self):
        filler = SlotFiller()
        filler.validator = self.validator
        filler.arm("add_reminder", {"text": "submit assignment"})

        result = filler.resolve("25:99", "unknown", {})

        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])
        self.assertEqual(result["missing"], ["time"])
        self.assertEqual(result["parameters"]["text"], "submit assignment")
        self.assertTrue(filler.has_pending())

    def test_valid_followup_preserves_existing_parameters(self):
        filler = SlotFiller()
        filler.validator = self.validator
        filler.arm("create_workflow", {"workflow": "reports"})

        result = filler.resolve("daily summary", "unknown", {})

        self.assertTrue(result["completed"])
        self.assertEqual(
            result["parameters"],
            {
                "workflow": "reports",
                "description": "daily summary",
            },
        )
        self.assertFalse(filler.has_pending())


if __name__ == "__main__":
    unittest.main()
