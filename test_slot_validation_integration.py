import unittest

from proactive.slot_filling import SlotFiller
from proactive.slot_validation import SlotValidator


class TestSlotValidationIntegration(unittest.TestCase):
    def setUp(self):
        self.validator = SlotValidator()
        self.filler = SlotFiller()
        self.filler.validator = self.validator

    def test_weekly_reminder_normalizes_time_and_weekday_across_turns(self):
        self.filler.arm(
            "add_weekly_reminder",
            {"text": "team meeting"},
        )

        time_result = self.filler.resolve("7 PM", "unknown", {})
        self.assertTrue(time_result["pending"])
        self.assertEqual(time_result["parameters"]["time"], "19:00")
        self.assertEqual(time_result["missing"], ["weekday"])

        day_result = self.filler.resolve("Friday", "unknown", {})
        self.assertTrue(day_result["completed"])
        self.assertEqual(day_result["parameters"]["text"], "team meeting")
        self.assertEqual(day_result["parameters"]["time"], "19:00")
        self.assertEqual(day_result["parameters"]["weekday"], 4)
        self.assertFalse(self.filler.has_pending())

    def test_invalid_weekday_preserves_previously_filled_time(self):
        self.filler.arm(
            "add_weekly_reminder",
            {"text": "team meeting"},
        )
        self.filler.resolve("7 PM", "unknown", {})

        result = self.filler.resolve("Funday", "unknown", {})

        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])
        self.assertEqual(result["missing"], ["weekday"])
        self.assertEqual(result["parameters"]["text"], "team meeting")
        self.assertEqual(result["parameters"]["time"], "19:00")
        self.assertEqual(result["validation"]["reason"], "invalid_weekday")

    def test_relative_reminder_normalizes_amount_and_unit_across_turns(self):
        self.filler.arm(
            "add_relative_reminder",
            {"text": "stretch"},
        )

        amount_result = self.filler.resolve("15", "unknown", {})
        self.assertTrue(amount_result["pending"])
        self.assertEqual(amount_result["parameters"]["amount"], 15)
        self.assertEqual(amount_result["missing"], ["unit"])

        unit_result = self.filler.resolve("mins", "unknown", {})
        self.assertTrue(unit_result["completed"])
        self.assertEqual(unit_result["parameters"]["text"], "stretch")
        self.assertEqual(unit_result["parameters"]["amount"], 15)
        self.assertEqual(unit_result["parameters"]["unit"], "minutes")
        self.assertFalse(self.filler.has_pending())

    def test_invalid_amount_keeps_relative_reminder_pending(self):
        self.filler.arm(
            "add_relative_reminder",
            {"text": "stretch"},
        )

        result = self.filler.resolve("0", "unknown", {})

        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])
        self.assertEqual(result["missing"], ["amount", "unit"])
        self.assertEqual(result["parameters"]["text"], "stretch")
        self.assertEqual(result["validation"]["reason"], "invalid_amount")
        self.assertTrue(self.filler.has_pending())

    def test_browser_url_completes_with_validated_value(self):
        self.filler.arm("open_browser", {})

        result = self.filler.resolve(
            "https://example.com",
            "unknown",
            {},
        )

        self.assertTrue(result["completed"])
        self.assertEqual(result["parameters"]["url"], "https://example.com")
        self.assertFalse(self.filler.has_pending())

    def test_invalid_browser_url_preserves_pending_slot(self):
        self.filler.arm("open_browser", {})

        result = self.filler.resolve("not a url", "unknown", {})

        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])
        self.assertEqual(result["missing"], ["url"])
        self.assertEqual(result["validation"]["reason"], "invalid_url")
        self.assertTrue(self.filler.has_pending())

    def test_location_and_path_values_are_trimmed(self):
        cases = (
            ("open_folder", "location", "  Documents  ", "Documents"),
            ("open_file", "path", "  notes.txt  ", "notes.txt"),
        )

        for intent, slot, raw_value, expected in cases:
            with self.subTest(intent=intent, slot=slot):
                result = self.validator.validate(intent, slot, raw_value)
                self.assertTrue(result["valid"])
                self.assertEqual(result["value"], expected)


if __name__ == "__main__":
    unittest.main()
