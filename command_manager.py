"""
Project FRIDAY
Command Manager
"""


class CommandManager:

    def __init__(self):

        self.exact = {}
        self.prefix = {}
        self.intent = {}

    # ========================================
    # EXACT COMMANDS
    # ========================================

    def register_exact(
        self,
        command,
        function
    ):

        command = str(
            command
        ).strip().lower()

        self.exact[
            command
        ] = function

    # ========================================
    # PREFIX COMMANDS
    # ========================================

    def register_prefix(
        self,
        prefix,
        function
    ):

        prefix = str(
            prefix
        ).lower()

        self.prefix[
            prefix
        ] = function

    # ========================================
    # INTENT COMMANDS
    # ========================================

    def register_intent(
        self,
        intent,
        function
    ):

        self.intent[
            intent
        ] = function

    # ========================================
    # EXECUTE
    # ========================================

    def execute(
        self,
        command
    ):

        command = str(
            command
        ).strip().lower()

        print(
            f"Command received: '{command}'"
        )

        # ========================================
        # EXACT COMMAND
        # ========================================

        if command in self.exact:

            return self.exact[
                command
            ]()

        # ========================================
        # PREFIX COMMAND
        # ========================================
        #
        # IMPORTANT:
        # Check the LONGEST prefix first.
        #
        # Example:
        #
        # search google for java
        #
        # matches:
        #
        # search
        # search google
        #
        # The more specific prefix wins.
        # ========================================

        matching_prefixes = [

            prefix
            for prefix in self.prefix
            if command.startswith(prefix)
        ]

        matching_prefixes.sort(
            key=len,
            reverse=True
        )

        for prefix in matching_prefixes:

            function = self.prefix[
                prefix
            ]

            argument = command[
                len(prefix):
            ].strip()

            print(
                f"Prefix: {prefix}"
            )

            print(
                f"Argument: '{argument}'"
            )

            result = function(
                argument
            )

            # ----------------------------------------
            # None means:
            #
            # "I didn't handle this command."
            #
            # Continue searching for another handler.
            # ----------------------------------------

            if result is None:

                continue

            return result

        # ----------------------------------------
        # No fast command matched.
        #
        # Return None silently so Brain can
        # continue to the planner / intent engine.
        # ----------------------------------------

        return None


manager = CommandManager()