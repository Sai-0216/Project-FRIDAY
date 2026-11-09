"""
Project FRIDAY
Phase 18.15-B + Phase 18.4.2

Proactive System

Central controller for FRIDAY's proactive intelligence.

Event flow:

    Event Source
         ↓
    EventManager
         ↓
    Priority Queue
         ↓
    Collection Window
         ↓
    Highest Priority First
         ↓
    ProactiveEngine
         ↓
    DecisionPolicy
         ↓
    NotificationManager

Event sources:

    Scheduler
    ReminderSource
    BatterySource
    EnvironmentSource
"""

import threading
import time
from queue import PriorityQueue, Empty

from .event_manager import EventManager
from .proactive_engine import ProactiveEngine
from .notification_manager import notification_manager
from .scheduler import Scheduler
from .reminder_source import ReminderSource
from .battery_source import BatterySource
from .environment_source import EnvironmentSource


class ProactiveSystem:

    COLLECTION_WINDOW = 0.2

    def __init__(self):

        self.running = False

        # ----------------------------------------------------
        # CORE COMPONENTS
        # ----------------------------------------------------

        self.event_manager = EventManager()
        self.engine = ProactiveEngine()

        # ----------------------------------------------------
        # PRIORITY QUEUE
        # ----------------------------------------------------

        self.event_queue = PriorityQueue()

        self.queue_counter = 0
        self.queue_lock = threading.Lock()

        self.processor_thread = None

        # ----------------------------------------------------
        # EVENT SOURCES
        # ----------------------------------------------------

        self.scheduler = Scheduler(
            self.event_manager
        )

        self.reminder_source = ReminderSource(
            self.event_manager
        )

        self.battery_source = BatterySource(
            self.event_manager
        )

        self.environment_source = EnvironmentSource(
            self.event_manager
        )

        # ----------------------------------------------------
        # EVENT PIPELINE
        # ----------------------------------------------------

        self.event_manager.register_listener(
            self._queue_event
        )

    # ========================================================
    # EVENT QUEUE
    # ========================================================

    def _queue_event(self, event):

        if not self.running:

            print(
                "[PROACTIVE QUEUE] "
                "System stopped. Event rejected."
            )

            return

        with self.queue_lock:

            self.queue_counter += 1

            counter = self.queue_counter

        queue_item = (
            -event.priority,
            counter,
            event
        )

        self.event_queue.put(
            queue_item
        )

        print(
            "[PROACTIVE QUEUE] "
            f"Event queued: priority={event.priority}, "
            f"type={event.event_type}"
        )

    # ========================================================
    # QUEUE SIZE
    # ========================================================

    def get_queue_size(self):

        return self.event_queue.qsize()

    # ========================================================
    # COLLECT EVENT BURST
    # ========================================================

    def _collect_events(self, first_item):

        events = [
            first_item
        ]

        time.sleep(
            self.COLLECTION_WINDOW
        )

        while True:

            try:

                item = self.event_queue.get_nowait()

            except Empty:

                break

            events.append(
                item
            )

        events.sort(
            key=lambda item: (
                item[0],
                item[1]
            )
        )

        return events

    # ========================================================
    # EVENT PROCESSOR
    # ========================================================

    def _process_queue(self):

        while self.running:

            try:

                first_item = self.event_queue.get(
                    timeout=0.5
                )

            except Empty:

                continue

            batch = self._collect_events(
                first_item
            )

            for priority, counter, event in batch:

                try:

                    if not self.running:

                        print(
                            "[PROACTIVE QUEUE] "
                            "Shutdown detected. "
                            "Discarding pending event."
                        )

                        continue

                    print(
                        "[PROACTIVE QUEUE] "
                        f"Processing priority={event.priority}: "
                        f"{event}"
                    )

                    self._process_event(
                        event
                    )

                except Exception as e:

                    print(
                        "[PROACTIVE QUEUE] "
                        f"Processing error: {e}"
                    )

                finally:

                    self.event_queue.task_done()

    # ========================================================
    # EVENT PROCESSING
    # ========================================================

    def _process_event(self, event):

        try:

            decision = self.engine.process_event(
                event
            )

            if decision is None:

                return

            notification_manager.handle_decision(
                decision
            )

        except Exception as e:

            print(
                "[PROACTIVE] "
                f"Event processing error: {e}"
            )

    # ========================================================
    # START
    # ========================================================

    def start(self):

        if self.running:

            print(
                "[PROACTIVE] "
                "Proactive system already running."
            )

            return

        print(
            "[PROACTIVE] "
            "Starting proactive system..."
        )

        self.running = True

        # ----------------------------------------------------
        # START EVENT PROCESSOR
        # ----------------------------------------------------

        self.processor_thread = threading.Thread(
            target=self._process_queue,
            name="FRIDAY-Proactive-Event-Processor",
            daemon=True
        )

        self.processor_thread.start()

        # ----------------------------------------------------
        # START EVENT SOURCES
        # ----------------------------------------------------

        self.scheduler.start()

        self.reminder_source.start()

        self.battery_source.start()

        self.environment_source.start()

        print(
            "[PROACTIVE] "
            "Proactive system started."
        )

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        if not self.running:

            return

        print(
            "[PROACTIVE] "
            "Stopping proactive system..."
        )

        # Stop accepting new events first.
        self.running = False

        # ----------------------------------------------------
        # STOP EVENT SOURCES
        # ----------------------------------------------------

        self.scheduler.stop()

        self.reminder_source.stop()

        self.battery_source.stop()

        self.environment_source.stop()

        # ----------------------------------------------------
        # WAIT FOR PROCESSOR
        # ----------------------------------------------------

        if (
            self.processor_thread
            and self.processor_thread.is_alive()
        ):

            self.processor_thread.join(
                timeout=1
            )

        self.processor_thread = None

        # ----------------------------------------------------
        # DRAIN REMAINING QUEUE
        # ----------------------------------------------------

        discarded = 0

        while True:

            try:

                self.event_queue.get_nowait()

            except Empty:

                break

            self.event_queue.task_done()

            discarded += 1

        if discarded:

            print(
                "[PROACTIVE QUEUE] "
                f"Discarded {discarded} pending event(s) "
                "during shutdown."
            )

        print(
            "[PROACTIVE] "
            "Proactive system stopped."
        )


# ============================================
# PROACTIVE SYSTEM INSTANCE
# ============================================

proactive_system = ProactiveSystem()