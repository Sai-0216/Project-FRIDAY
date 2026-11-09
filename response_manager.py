"""
Project FRIDAY
Response Manager

Handles FRIDAY's response style and personality.
"""


class ResponseManager:

    def __init__(self):

        self.name = "FRIDAY"
        self.user_title = "Sir"

    # ========================================
    # COMMAND RESPONSES
    # ========================================

    def command(
        self,
        response
    ):

        if not response:

            return None

        response = str(
            response
        ).strip()

        if not response:

            return None

        # ----------------------------------------
        # Already personalized
        # ----------------------------------------

        if response.lower().startswith(
            (
                "sir,",
                "sorry sir,",
                "i'm sorry sir,",
            )
        ):

            return response

        # ----------------------------------------
        # Common successful actions
        # ----------------------------------------

        replacements = {

            "Opening spotify.":
                "Opening Spotify, Sir.",

            "Opening chrome and searching as requested.":
                "Opening Chrome and searching as requested, Sir.",

            "Volume increased.":
                "Volume increased, Sir.",

            "Volume decreased.":
                "Volume decreased, Sir.",

            "Screenshot saved successfully.":
                "Screenshot saved successfully, Sir.",

            "Muted.":
                "Muted, Sir.",

            "Unmuted.":
                "Unmuted, Sir.",

        }

        if response in replacements:

            return replacements[
                response
            ]

        return response

    # ========================================
    # AI RESPONSE
    # ========================================

    def ai(
        self,
        response
    ):

        if not response:

            return None

        response = str(
            response
        ).strip()

        if not response:

            return None

        # ----------------------------------------
        # Don't modify AI responses that already
        # address the user naturally.
        # ----------------------------------------

        if response.lower().startswith(
            (
                "sir,",
                "sorry sir,",
                "i'm sorry sir,",
                "always, sir",
                "of course, sir",
            )
        ):

            return response

        return response

    # ========================================
    # ERROR RESPONSE
    # ========================================

    def error(
        self,
        message=None
    ):

        if message:

            return (
                f"Sorry Sir, {message}"
            )

        return (
            "Sorry Sir, I couldn't "
            "complete that."
        )

    # ========================================
    # UNKNOWN COMMAND
    # ========================================

    def unknown(self):

        return (
            "I'm not sure how to do that yet, Sir."
        )

    # ========================================
    # GREETING
    # ========================================

    def greeting(self):

        return (
            "Always ready, Sir."
        )

    # ========================================
    # SUCCESS
    # ========================================

    def success(
        self,
        message
    ):

        if not message:

            return "Done, Sir."

        return (
            f"{message}, Sir."
        )


response_manager = (
    ResponseManager()
)