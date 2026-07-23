"""
Project FRIDAY
Command Manager
"""

class CommandManager:

    def __init__(self):

        self.exact = {}
        self.prefix = {}
        self.intent = {}

    # -------------------------
    # Exact Commands
    # -------------------------

    def register_exact(self, command, function):
        self.exact[command] = function

    # -------------------------
    # Prefix Commands
    # -------------------------

    def register_prefix(self, prefix, function):
        self.prefix[prefix] = function

    # -------------------------
    # Intent Commands
    # -------------------------

    def register_intent(self, intent, function):
        self.intent[intent] = function

    # -------------------------
    # Execute
    # -------------------------

    def execute(self, command):

        command = command.strip().lower()

        print(f"Command received: '{command}'")

        # Exact
        if command in self.exact:

            return self.exact[command]()

        # Prefix
        for prefix, function in self.prefix.items():

            if command.startswith(prefix):

                argument = command[len(prefix):].strip()

                print(f"Prefix: {prefix}"
                       )
                print(f"Argument: '{argument}'")

                return function(argument)
        print("No command matched.")    
        return None


manager = CommandManager()