from .client import OpenJarvisClient


class OpenJarvisAdapter:

    def __init__(self):
        self.client = OpenJarvisClient()

    def ask(self, prompt):
        try:
            response = self.client.complete(prompt)

            return {
                "ok": True,
                "text": response,
                "error": None,
            }

        except Exception as error:
            return {
                "ok": False,
                "text": "",
                "error": str(error),
            }

    def complete_messages(self, messages, max_tokens=None, temperature=None):
        try:
            response = self.client.complete_messages(
                messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return {
                "ok": True,
                "text": response,
                "error": None,
            }

        except Exception as error:
            return {
                "ok": False,
                "text": "",
                "error": str(error),
            }
