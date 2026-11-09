"""
Project FRIDAY
Phase 16.18-B

Proactive Notification Manager

Handles decisions produced by the
Proactive Intelligence Engine.

Decision types:

    IGNORE
        -> Do nothing

    NOTIFY
        -> Inform the user

    SUGGEST
        -> Offer a suggestion

    CONFIRM
        -> Ask for confirmation

Phase 16.18-B:
    - Marks pending confirmations as proactive
      so Brain can distinguish them from normal
      confirmation flows.
"""

from speech import speaker


class NotificationManager:

    def __init__(self):

        self.enabled = True

        self.pending_confirmation = None

    # =========================================================
    # HANDLE DECISION
    # =========================================================

    def handle_decision(
        self,
        decision
    ):

        if not self.enabled:

            return

        if not decision:

            return

        action = decision.get(
            "action"
        )

        message = decision.get(
            "message"
        )

        # =====================================================
        # IGNORE
        # =====================================================

        if action == "IGNORE":

            print(
                "[FRIDAY PROACTIVE] "
                "Decision ignored."
            )

            return

        # =====================================================
        # NO MESSAGE
        # =====================================================

        if not message:

            print(
                "[FRIDAY PROACTIVE] "
                "No message provided."
            )

            return

        # =====================================================
        # NOTIFY
        # =====================================================

        if action == "NOTIFY":

            self.notify(
                message
            )

            return

        # =====================================================
        # SUGGEST
        # =====================================================

        if action == "SUGGEST":

            self.suggest(
                message
            )

            return

        # =====================================================
        # CONFIRM
        # =====================================================

        if action == "CONFIRM":

            self.request_confirmation(
                decision
            )

            return

        # =====================================================
        # UNKNOWN
        # =====================================================

        print(
            "[FRIDAY PROACTIVE] "
            f"Unknown action: {action}"
        )

    # =========================================================
    # NOTIFY
    # =========================================================

    def notify(
        self,
        message
    ):

        print(
            f"[FRIDAY NOTIFY] {message}"
        )

        speaker.speak(
            message
        )

    # =========================================================
    # SUGGEST
    # =========================================================

    def suggest(
        self,
        message
    ):

        print(
            f"[FRIDAY SUGGEST] {message}"
        )

        speaker.speak(
            message
        )

    # =========================================================
    # REQUEST CONFIRMATION
    # =========================================================

    def request_confirmation(
        self,
        decision
    ):

        message = decision.get(
            "message",
            "Would you like me to proceed?"
        )

        # -----------------------------------------------------
        # COPY THE DECISION
        #
        # Do not mutate the original decision object.
        # -----------------------------------------------------

        decision = dict(
            decision
        )

        # -----------------------------------------------------
        # MARK AS PROACTIVE
        #
        # Brain uses this flag to distinguish a proactive
        # confirmation from a normal GUI/command confirmation.
        # -----------------------------------------------------

        decision["_proactive"] = True

        self.pending_confirmation = (
            decision
        )

        print(
            f"[FRIDAY CONFIRM] {message}"
        )

        speaker.speak(
            message
        )

        print(
            "[FRIDAY CONFIRM] "
            "Waiting for user confirmation."
        )

    # =========================================================
    # CONFIRMATION STATE
    # =========================================================

    def has_pending_confirmation(
        self
    ):

        return (
            self.pending_confirmation
            is not None
        )

    def get_pending_confirmation(
        self
    ):

        return (
            self.pending_confirmation
        )

    def clear_confirmation(
        self
    ):

        self.pending_confirmation = None

        print(
            "[FRIDAY CONFIRM] "
            "Confirmation cleared."
        )

    def consume_confirmation(
        self
    ):

        decision = (
            self.pending_confirmation
        )

        if decision is not None:

            self.pending_confirmation = None

            print(
                "[FRIDAY CONFIRM] "
                "Confirmation consumed."
            )

        return decision


notification_manager = NotificationManager()