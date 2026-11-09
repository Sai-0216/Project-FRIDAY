from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from ai import AI


class TestAIRouting(TestCase):

    def setUp(self):
        self.ai = AI.__new__(AI)

        self.patches = [
            patch.object(self.ai, "_get_memory_text", return_value=""),
            patch.object(self.ai, "_get_recommendation_context", return_value=""),
            patch.object(self.ai, "_get_personalization_context", return_value=""),
            patch.object(self.ai, "_get_history", return_value=[]),
            patch.object(self.ai, "_get_response_mode", return_value=("short", 80)),
            patch.object(
                self.ai,
                "_apply_memory_personalization",
                side_effect=lambda prompt, reply, memory: reply,
            ),
        ]

        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    @patch("integrations.openjarvis.adapter.OpenJarvisAdapter")
    @patch("ai.ollama.chat")
    def test_planning_uses_ollama_only(self, ollama_chat, openjarvis_class):
        ollama_chat.return_value = SimpleNamespace(
            message=SimpleNamespace(content="PLAN RESPONSE")
        )

        result = self.ai.ask_planning("Create a safe test plan")

        self.assertEqual(result, "PLAN RESPONSE")
        ollama_chat.assert_called_once()
        openjarvis_class.assert_not_called()

    @patch("integrations.openjarvis.adapter.OpenJarvisAdapter")
    @patch("ai.ollama.chat")
    def test_conversation_uses_openjarvis_first(self, ollama_chat, openjarvis_class):
        openjarvis_class.return_value.complete_messages.return_value = {
            "ok": True,
            "text": "OPENJARVIS RESPONSE",
            "error": None,
        }

        result = self.ai.ask("Explain Python variables")

        self.assertEqual(result, "OPENJARVIS RESPONSE")
        openjarvis_class.return_value.complete_messages.assert_called_once()
        ollama_chat.assert_not_called()

    @patch("integrations.openjarvis.adapter.OpenJarvisAdapter")
    @patch("ai.ollama.chat")
    def test_conversation_falls_back_to_ollama(
        self, ollama_chat, openjarvis_class
    ):
        openjarvis_class.return_value.complete_messages.return_value = {
            "ok": False,
            "text": "",
            "error": "OpenJarvis unavailable",
        }

        ollama_chat.return_value = SimpleNamespace(
            message=SimpleNamespace(content="OLLAMA FALLBACK RESPONSE")
        )

        result = self.ai.ask("Explain Python loops")

        self.assertEqual(result, "OLLAMA FALLBACK RESPONSE")
        openjarvis_class.return_value.complete_messages.assert_called_once()
        ollama_chat.assert_called_once()


if __name__ == "__main__":
    import unittest
    unittest.main()
