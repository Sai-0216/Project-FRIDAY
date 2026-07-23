import re


class Extractor:

    def app(self, text):

        words = [
            "open",
            "launch",
            "start",
            "run"
        ]

        for word in words:
            text = re.sub(rf"\b{word}\b", "", text)

        return text.strip()

    def search(self, text):

        words = [
            "search",
            "google",
            "find",
            "look up"
        ]

        for word in words:
            text = text.replace(word, "")

        return text.strip()


extractor = Extractor()