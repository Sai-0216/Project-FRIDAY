"""
Project FRIDAY
Phase 18.9.3

Environment Event Source

Periodically checks the current device/environment
state, records the snapshot for historical analysis,
and emits a proactive event only when a warning or
critical condition remains stable.

This module does NOT speak or execute actions.
It only detects conditions, stores history, and
emits events.
"""

import threading
import time

from modules.device_state import device_state

from proactive.environment_memory import (
    environment_memory
)

from modules.environment_awareness import (
    environment_awareness
)


class EnvironmentSource:

    # ========================================
    # CONFIGURATION
    # ========================================

    DEFAULT_CHECK_INTERVAL = 30

    STABILITY_CHECKS_REQUIRED = 2

    # ========================================
    # INITIALIZATION
    # ========================================

    def __init__(
        self,
        event_manager,
        check_interval=DEFAULT_CHECK_INTERVAL
    ):

        self.event_manager = event_manager

        self.check_interval = (
            check_interval
        )

        self.running = False
        self.thread = None

        # ----------------------------------------
        # STABILITY STATE
        # ----------------------------------------

        self.pending_signature = None
        self.pending_count = 0

        self.lock = threading.Lock()

    # ========================================
    # START
    # ========================================

    def start(self):

        if self.running:
            return

        self.running = True

        with self.lock:

            self.pending_signature = None
            self.pending_count = 0

        self.thread = threading.Thread(
            target=self._run,
            name="FRIDAY-Proactive-Environment-Source",
            daemon=True
        )

        self.thread.start()

        print(
            "[ENVIRONMENT SOURCE] "
            "Environment event source started."
        )

    # ========================================
    # CONDITION SIGNATURE
    # ========================================

    def _get_signature(
        self,
        analysis
    ):
        """
        Return a stable identity for the environmental
        condition.

        Live numeric values are removed so small
        fluctuations do not create a new condition.
        """

        if not analysis:
            return None

        status = analysis.get(
            "status"
        )

        reasons = analysis.get(
            "reasons",
            []
        )

        normalized_reasons = []

        for reason in reasons:

            reason = str(
                reason
            )

            normalized = reason.split(
                " (",
                1
            )[0].strip()

            normalized_reasons.append(
                normalized
            )

        return (
            status,
            tuple(
                sorted(
                    normalized_reasons
                )
            )
        )

    # ========================================
    # CHECK ENVIRONMENT
    # ========================================

    def check_environment(self):

        # ----------------------------------------
        # Capture ONE state snapshot
        # ----------------------------------------

        state = device_state.snapshot()

        # ----------------------------------------
        # Record snapshot
        # ----------------------------------------

        recorded = environment_memory.record(
            state
        )

        if not recorded:

            print(
                "[ENVIRONMENT SOURCE] "
                "Failed to record environment history."
            )

        # ----------------------------------------
        # Analyze WITHOUT marking it reported
        # ----------------------------------------

        analysis = (
            environment_awareness.analyze(
                state
            )
        )

        if not analysis.get(
            "should_report"
        ):

            with self.lock:

                self.pending_signature = None
                self.pending_count = 0

            print(
                "[ENVIRONMENT SOURCE] "
                "No new environmental condition."
            )

            return None

        # ----------------------------------------
        # Identify current condition
        # ----------------------------------------

        signature = self._get_signature(
            analysis
        )

        with self.lock:

            if (
                signature
                == self.pending_signature
            ):

                self.pending_count += 1

            else:

                self.pending_signature = (
                    signature
                )

                self.pending_count = 1

            print(
                "[ENVIRONMENT SOURCE] "
                f"Condition stability: "
                f"{self.pending_count}/"
                f"{self.STABILITY_CHECKS_REQUIRED}"
            )

            # ------------------------------------
            # Condition not stable yet
            # ------------------------------------

            if (
                self.pending_count
                < self.STABILITY_CHECKS_REQUIRED
            ):

                return None

            # ------------------------------------
            # Stable condition reached
            # ------------------------------------

            self.pending_signature = None
            self.pending_count = 0

        # ----------------------------------------
        # Create event ONLY after stability
        # ----------------------------------------

        event = (
            environment_awareness.create_event(
                state
            )
        )

        if event is None:

            print(
                "[ENVIRONMENT SOURCE] "
                "Condition changed before event creation."
            )

            return None

        print(
            "[ENVIRONMENT SOURCE] "
            f"Stable condition detected: {event}"
        )

        return event

    # ========================================
    # BACKGROUND LOOP
    # ========================================

    def _run(self):

        while self.running:

            try:

                event = (
                    self.check_environment()
                )

                if event is not None:

                    self.event_manager.emit(
                        event
                    )

            except Exception as e:

                print(
                    "[ENVIRONMENT SOURCE] "
                    f"Worker error: {e}"
                )

            time.sleep(
                self.check_interval
            )

    # ========================================
    # STOP
    # ========================================

    def stop(self):

        if not self.running:
            return

        self.running = False

        with self.lock:

            self.pending_signature = None
            self.pending_count = 0

        print(
            "[ENVIRONMENT SOURCE] "
            "Environment event source stopped."
        )