import unittest

from proactive.slot_filling import SlotFiller


class TestSlotSchemaCoverage(unittest.TestCase):
    def setUp(self):
        self.filler = SlotFiller()

    def test_all_declared_intents_have_nonempty_slot_schemas(self):
        schemas = self.filler.REQUIRED_SLOTS

        self.assertEqual(len(schemas), 25)

        for intent, slots in schemas.items():
            with self.subTest(intent=intent):
                self.assertTrue(slots)
                self.assertEqual(len(slots), len(set(slots)))
                self.assertTrue(all(isinstance(slot, str) and slot for slot in slots))

    def test_missing_parameters_are_reported_in_schema_order(self):
        for intent, slots in self.filler.REQUIRED_SLOTS.items():
            with self.subTest(intent=intent):
                self.assertEqual(self.filler.missing_slots(intent, {}), list(slots))

    def test_complete_parameters_have_no_missing_slots(self):
        for intent, slots in self.filler.REQUIRED_SLOTS.items():
            with self.subTest(intent=intent):
                parameters = {slot: "sample value" for slot in slots}
                self.assertEqual(self.filler.missing_slots(intent, parameters), [])

    def test_partial_parameters_report_only_missing_slots(self):
        for intent, slots in self.filler.REQUIRED_SLOTS.items():
            if len(slots) < 2:
                continue

            with self.subTest(intent=intent):
                parameters = {slots[0]: "sample value"}
                self.assertEqual(
                    self.filler.missing_slots(intent, parameters),
                    list(slots[1:]),
                )

    def test_empty_string_parameters_count_as_missing(self):
        for intent, slots in self.filler.REQUIRED_SLOTS.items():
            for slot in slots:
                with self.subTest(intent=intent, slot=slot):
                    self.assertEqual(
                        self.filler.missing_slots(intent, {slot: "   "}),
                        list(slots),
                    )

    def test_none_parameters_count_as_missing(self):
        for intent, slots in self.filler.REQUIRED_SLOTS.items():
            for slot in slots:
                with self.subTest(intent=intent, slot=slot):
                    self.assertEqual(
                        self.filler.missing_slots(intent, {slot: None}),
                        list(slots),
                    )

    def test_unknown_intent_has_no_required_slots(self):
        self.assertEqual(self.filler.required_slots("unknown_intent"), ())
        self.assertEqual(self.filler.missing_slots("unknown_intent", {}), [])

    def test_arm_does_not_remain_pending_when_all_slots_are_supplied(self):
        for intent, slots in self.filler.REQUIRED_SLOTS.items():
            with self.subTest(intent=intent):
                parameters = {slot: "sample value" for slot in slots}
                missing = self.filler.arm(intent, parameters)

                self.assertEqual(missing, [])
                self.assertFalse(self.filler.has_pending())
                self.assertIsNone(self.filler.pending_intent)


if __name__ == "__main__":
    unittest.main()
