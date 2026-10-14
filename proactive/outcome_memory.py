"""
Project FRIDAY
Phase 16.18-A

Proactive Outcome Memory

Stores the outcomes of proactive decisions so FRIDAY
can eventually learn which proactive behaviors are
useful, ignored, accepted, or rejected.

This phase only records outcomes.

It does NOT modify decision behavior yet.
"""

import json
import os
import threading
from datetime import datetime


class ProactiveOutcomeMemory:

    MAX_RECORDS = 500

    def __init__(self, file_path=None):

        if file_path is None:
            base_dir = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )

            data_dir = os.path.join(
                base_dir,
                "data"
            )

            os.makedirs(
                data_dir,
                exist_ok=True
            )

            file_path = os.path.join(
                data_dir,
                "proactive_outcomes.json"
            )

        self.file_path = file_path
        self.lock = threading.RLock()
        self.records = []

        self._load()

    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    def _load(self):

        with self.lock:

            try:

                if not os.path.exists(
                    self.file_path
                ):
                    self.records = []
                    return

                with open(
                    self.file_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(file)

                if isinstance(data, list):
                    self.records = data
                else:
                    self.records = []

            except Exception as e:

                print(
                    "[OUTCOME MEMORY] "
                    f"Load error: {e}"
                )

                self.records = []

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    def _save(self):

        with self.lock:

            try:

                directory = os.path.dirname(
                    self.file_path
                )

                if directory:
                    os.makedirs(
                        directory,
                        exist_ok=True
                    )

                with open(
                    self.file_path,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        self.records,
                        file,
                        indent=4,
                        ensure_ascii=False
                    )

            except Exception as e:

                print(
                    "[OUTCOME MEMORY] "
                    f"Save error: {e}"
                )

    # ------------------------------------------------------
    # RECORD OUTCOME
    # ------------------------------------------------------

    def record(
        self,
        event_type,
        action,
        attention_level,
        outcome,
        intent=None,
        reason=None
    ):

        record = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "action": action,
            "attention_level": attention_level,
            "outcome": outcome,
            "intent": intent,
            "reason": reason,
        }

        with self.lock:

            self.records.append(
                record
            )

            if len(self.records) > self.MAX_RECORDS:

                self.records = (
                    self.records[
                        -self.MAX_RECORDS:
                    ]
                )

            self._save()

        print(
            "[OUTCOME MEMORY] "
            f"Recorded: {record}"
        )

        return record

    # ------------------------------------------------------
    # READ RECENT
    # ------------------------------------------------------

    def get_recent(
        self,
        limit=20
    ):

        with self.lock:

            return list(
                self.records[-limit:]
            )

    # ------------------------------------------------------
    # FILTER BY EVENT
    # ------------------------------------------------------

    def get_by_event_type(
        self,
        event_type
    ):

        with self.lock:

            return [
                record
                for record in self.records
                if record.get(
                    "event_type"
                ) == event_type
            ]

    # ------------------------------------------------------
    # FILTER BY OUTCOME
    # ------------------------------------------------------

    def get_by_outcome(
        self,
        outcome
    ):

        with self.lock:

            return [
                record
                for record in self.records
                if record.get(
                    "outcome"
                ) == outcome
            ]

    # ------------------------------------------------------
    # STATISTICS
    # ------------------------------------------------------

    def get_statistics(
        self,
        event_type=None
    ):

        with self.lock:

            records = self.records

            if event_type is not None:

                records = [
                    record
                    for record in records
                    if record.get(
                        "event_type"
                    ) == event_type
                ]

            statistics = {
                "total": len(records),
                "accepted": 0,
                "rejected": 0,
                "ignored": 0,
                "notified": 0,
                "suggested": 0,
                "confirmed": 0,
            }

            for record in records:

                outcome = record.get(
                    "outcome"
                )

                if outcome in statistics:
                    statistics[outcome] += 1

                if outcome == "accepted":
                    statistics["accepted"] += 0

                if outcome == "rejected":
                    statistics["rejected"] += 0

            return statistics


# Global proactive outcome memory

proactive_outcome_memory = (
    ProactiveOutcomeMemory()
)