class CommandProcessor:

    def clean(self, command):

        command = command.lower().strip()

        words = [
            "please",
            "can you",
            "could you",
            "would you",
            "hey",
            "friday",
            "for me"
        ]

        for word in words:
            command = command.replace(word, "")

        return command.strip()


processor = CommandProcessor()