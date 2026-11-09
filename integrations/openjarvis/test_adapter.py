import json
from io import BytesIO
from unittest import TestCase, main
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from integrations.openjarvis.adapter import OpenJarvisAdapter
from integrations.openjarvis.client import OpenJarvisClient, _NoRedirectHandler
from integrations.openjarvis import config


class TestOpenJarvisAdapter(TestCase):

    @patch("integrations.openjarvis.client._open_request")
    def test_successful_response(self, mock_urlopen):
        response = BytesIO(json.dumps({
            "choices": [{
                "message": {
                    "content": "OpenJarvis test successful!"
                }
            }]
        }).encode("utf-8"))

        mock_urlopen.return_value = response
        result = OpenJarvisAdapter().ask("Test request")

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["text"],
            "OpenJarvis test successful!"
        )
        self.assertIsNone(result["error"])

    @patch("integrations.openjarvis.client._open_request")
    def test_server_unavailable(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")
        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertIn("connection failed", result["error"].lower())

    @patch("integrations.openjarvis.client._open_request")
    def test_request_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("Request timed out")
        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertIn("timed out", result["error"].lower())

    @patch("integrations.openjarvis.client._open_request")
    def test_invalid_json_response(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(b"invalid json")
        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertTrue(result["error"])

    @patch("integrations.openjarvis.client._open_request")
    def test_empty_completion(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(b'{"choices": []}')
        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertIn("no completion", result["error"].lower())

    @patch("integrations.openjarvis.client._open_request")
    def test_empty_response_content(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(
            b'{"choices": [{"message": {"content": ""}}]}'
        )
        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertIn("empty response", result["error"].lower())

    def test_empty_prompt_rejected(self):
        result = OpenJarvisAdapter().ask("   ")

        self.assertFalse(result["ok"])
        self.assertIn("non-empty", result["error"].lower())

    def test_oversized_prompt_rejected(self):
        prompt = "x" * (config.MAX_PROMPT_CHARS + 1)
        result = OpenJarvisAdapter().ask(prompt)

        self.assertFalse(result["ok"])
        self.assertIn("size limit", result["error"].lower())

    def test_non_localhost_configuration_rejected(self):
        with patch.object(
            config,
            "BASE_URL",
            "http://192.168.1.10:8000"
        ):
            with self.assertRaises(ValueError):
                OpenJarvisClient()

    @patch("integrations.openjarvis.client._open_request")
    def test_http_500_handled(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            "http://127.0.0.1:8000",
            500,
            "Internal Server Error",
            {},
            None
        )

        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertIn("http error: 500", result["error"].lower())

    @patch("integrations.openjarvis.client._open_request")
    def test_malformed_message_structure(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(
            b'{"choices": [{"message": "invalid"}]}'
        )

        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertIn("message structure", result["error"].lower())

    @patch("integrations.openjarvis.client._open_request")
    def test_non_object_json_rejected(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(b'["unexpected"]')

        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertIn("response structure", result["error"].lower())

    @patch("integrations.openjarvis.client._open_request")
    def test_oversized_response_rejected(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(
            b"x" * (config.MAX_RESPONSE_BYTES + 1)
        )

        result = OpenJarvisAdapter().ask("Test request")

        self.assertFalse(result["ok"])
        self.assertIn("size limit", result["error"].lower())


    def test_redirect_handler_refuses_redirect(self):
        from urllib.request import Request

        handler = _NoRedirectHandler()
        request = Request("http://127.0.0.1:8000/test")

        redirected = handler.redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "http://example.com/"
        )

        self.assertIsNone(redirected)


if __name__ == "__main__":
    main()


