import unittest

from security.approval_manager import ApprovalManager


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class ApprovalManagerTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.manager = ApprovalManager(_clock=self.clock)
        self.actions = [
            ["open_app", "notepad"],
            ["wait", 2],
            ["open_url", "https://example.com"],
        ]

    def test_exact_action_sequence_can_be_consumed(self):
        token = self.manager.issue(self.actions)
        self.assertTrue(self.manager.consume(token, self.actions))

    def test_token_is_single_use(self):
        token = self.manager.issue(self.actions)
        self.assertTrue(self.manager.consume(token, self.actions))
        self.assertFalse(self.manager.consume(token, self.actions))

    def test_changed_action_is_rejected_and_token_invalidated(self):
        token = self.manager.issue(self.actions)
        changed = [
            ["open_app", "notepad"],
            ["wait", 2],
            ["open_url", "https://attacker.example"],
        ]
        self.assertFalse(self.manager.consume(token, changed))
        self.assertFalse(self.manager.consume(token, self.actions))

    def test_changed_action_order_is_rejected(self):
        token = self.manager.issue(self.actions)
        self.assertFalse(
            self.manager.consume(token, list(reversed(self.actions)))
        )

    def test_expired_token_is_rejected(self):
        token = self.manager.issue(self.actions, ttl_seconds=5)
        self.clock.advance(5)
        self.assertFalse(self.manager.consume(token, self.actions))

    def test_denied_token_cannot_be_consumed(self):
        token = self.manager.issue(self.actions)
        self.assertTrue(self.manager.deny(token))
        self.assertFalse(self.manager.consume(token, self.actions))

    def test_deny_unknown_token_returns_false(self):
        self.assertFalse(self.manager.deny("not-a-valid-token"))

    def test_empty_or_malformed_actions_cannot_be_approved(self):
        for actions in ([], None, {}, "open_app"):
            with self.subTest(actions=actions):
                with self.assertRaises(ValueError):
                    self.manager.issue(actions)

    def test_non_finite_action_values_are_rejected(self):
        with self.assertRaises(ValueError):
            self.manager.issue([["wait", float("nan")]])

    def test_invalid_lifetimes_are_rejected(self):
        for ttl in (0, -1, float("inf"), 301, "invalid"):
            with self.subTest(ttl=ttl):
                with self.assertRaises(ValueError):
                    self.manager.issue(self.actions, ttl_seconds=ttl)

    def test_pending_count_excludes_expired_tokens(self):
        self.manager.issue(self.actions, ttl_seconds=2)
        self.assertEqual(self.manager.pending_count(), 1)
        self.clock.advance(2)
        self.assertEqual(self.manager.pending_count(), 0)

    def test_independent_approvals_are_isolated(self):
        first = self.manager.issue(self.actions)
        second = self.manager.issue([["open_app", "calculator"]])

        self.assertTrue(self.manager.consume(first, self.actions))
        self.assertTrue(
            self.manager.consume(second, [["open_app", "calculator"]])
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
