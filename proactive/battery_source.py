"""
Project FRIDAY
Phase 16.12-A

Real Battery Event Source

Reads the actual system battery using psutil and
generates BATTERY_LOW proactive events.

Thresholds:
    <= 20%  -> low battery event
    <= 10%  -> critical battery event

Anti-spam:
    An event is generated only when the battery
    crosses into a new threshold.

Charging state is included in every event.
"""

import threading
import time

import psutil

from .event import Event


class BatterySource:

    LOW_THRESHOLD = 20
    CRITICAL_THRESHOLD = 10

    def __init__(self, event_manager, check_interval=30):
        self.event_manager = event_manager
        self.check_interval = check_interval

        self.running = False
        self.thread = None

        # Highest threshold already reported.
        #
        # None -> nothing reported
        # 20   -> low battery reported
        # 10   -> critical battery reported
        self.last_threshold = None

        self.lock = threading.Lock()

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    def start(self):
        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            name="FRIDAY-Proactive-Battery-Source",
            daemon=True,
        )

        self.thread.start()

        print("[BATTERY SOURCE] Battery event source started.")

    # --------------------------------------------------------
    # BATTERY READING
    # --------------------------------------------------------

    def read_battery(self):
        battery = psutil.sensors_battery()

        if battery is None:
            return None

        return {
            "battery": int(battery.percent),
            "charging": bool(battery.power_plugged),
        }

    # --------------------------------------------------------
    # THRESHOLD
    # --------------------------------------------------------

    def _get_threshold(self, battery_percent):
        if battery_percent <= self.CRITICAL_THRESHOLD:
            return self.CRITICAL_THRESHOLD

        if battery_percent <= self.LOW_THRESHOLD:
            return self.LOW_THRESHOLD

        return None

    # --------------------------------------------------------
    # EVENT CREATION
    # --------------------------------------------------------

    def _create_event(self, battery_percent, charging):
        threshold = self._get_threshold(battery_percent)

        if threshold == self.CRITICAL_THRESHOLD:
            message = (
                f"Sir, your battery is critically low at "
                f"{battery_percent}%."
            )
            priority = 5

        else:
            message = (
                f"Sir, your battery is low at "
                f"{battery_percent}%."
            )
            priority = 3

        return Event(
            event_type="BATTERY_LOW",
            source="battery",
            data={
                "battery": battery_percent,
                "charging": charging,
                "threshold": threshold,
            },
            priority=priority,
        )

    # --------------------------------------------------------
    # CHECK BATTERY
    # --------------------------------------------------------

    def check_battery(self):
        state = self.read_battery()

        if state is None:
            print("[BATTERY SOURCE] Battery information unavailable.")
            return None

        battery_percent = state["battery"]
        charging = state["charging"]

        print(
            f"[BATTERY SOURCE] "
            f"Battery={battery_percent}% "
            f"Charging={charging}"
        )

        threshold = self._get_threshold(battery_percent)

        # Battery is above the low threshold.
        #
        # Reset the threshold state so that if the battery
        # later drops below 20%, a new event can be generated.
        if threshold is None:
            with self.lock:
                if self.last_threshold is not None:
                    print(
                        "[BATTERY SOURCE] "
                        "Battery recovered above low threshold."
                    )

                self.last_threshold = None

            return None

        # Same threshold already reported.
        #
        # Prevents repeated notifications every 30 seconds.
        with self.lock:
            if self.last_threshold == threshold:
                return None

            self.last_threshold = threshold

        event = self._create_event(
            battery_percent,
            charging,
        )

        print(
            f"[BATTERY SOURCE] "
            f"Creating event: {event}"
        )

        return event

    # --------------------------------------------------------
    # BACKGROUND LOOP
    # --------------------------------------------------------

    def _run(self):
        while self.running:
            try:
                event = self.check_battery()

                if event is not None:
                    self.event_manager.emit(event)

            except Exception as e:
                print(
                    "[BATTERY SOURCE] "
                    f"Worker error: {e}"
                )

            time.sleep(self.check_interval)

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    def stop(self):
        if not self.running:
            return

        self.running = False

        print("[BATTERY SOURCE] Battery event source stopped.")


battery_source = None