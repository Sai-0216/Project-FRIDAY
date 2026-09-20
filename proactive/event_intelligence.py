from datetime import datetime
import copy

from .event import Event


class EventIntelligence:
    """
    Phase 33.2

    Provides a normalized intelligence representation
    for existing FRIDAY Event objects.

    This layer does not replace EventManager or Event.
    """

    def normalize(self, event):
        """
        Convert an Event into a stable dictionary
        representation suitable for later intelligence
        processing.
        """

        if not isinstance(event, Event):
            raise TypeError("event must be an Event object")

        created_at = event.created_at

        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        else:
            created_at = str(created_at)

        event_type = str(event.event_type).strip().upper()
        source = str(event.source).strip().lower()

        if not event_type:
            raise ValueError("event_type must not be empty")

        if not source:
            raise ValueError("source must not be empty")

        try:
            priority = int(event.priority)
        except (TypeError, ValueError):
            priority = 0

        data = event.data if isinstance(event.data, dict) else {}

        event_id = (
            f"{event_type}:"
            f"{source}:"
            f"{created_at}"
        )

        return {
            "event_id": event_id,
            "event_type": event_type,
            "source": source,
            "priority": priority,
            "created_at": created_at,
            "data": copy.deepcopy(data),
        }

    def classify(self, event_or_normalized):
        """
        Classify an event into a broad intelligence category.

        Accepts either an Event object or an already normalized
        event dictionary.
        """

        if isinstance(event_or_normalized, Event):
            normalized = self.normalize(event_or_normalized)
        elif isinstance(event_or_normalized, dict):
            normalized = copy.deepcopy(event_or_normalized)
        else:
            raise TypeError(
                "event_or_normalized must be an Event or dict"
            )

        event_type = str(
            normalized.get("event_type", "")
        ).strip().upper()

        if not event_type:
            raise ValueError(
                "event_type must not be empty"
            )

        classification = "unknown"

        prefixes = (
            ("ENVIRONMENT_", "environment"),
            ("SYSTEM_", "system"),
            ("TASK_", "task"),
            ("GOAL_", "goal"),
            ("REMINDER_", "reminder"),
            ("BATTERY_", "device"),
            ("DEVICE_", "device"),
            ("USER_", "user"),
        )

        for prefix, category in prefixes:
            if event_type.startswith(prefix):
                classification = category
                break

        normalized["classification"] = classification

        return normalized

    def deduplication_fingerprint(self, event_or_normalized):
        """
        Build a deterministic fingerprint for event deduplication.

        Volatile timestamp fields are excluded so repeated equivalent
        events can be recognized as duplicates.
        """

        if isinstance(event_or_normalized, Event):
            normalized = self.normalize(event_or_normalized)
        elif isinstance(event_or_normalized, dict):
            normalized = copy.deepcopy(event_or_normalized)
        else:
            raise TypeError(
                "event_or_normalized must be an Event or dict"
            )

        event_type = str(
            normalized.get("event_type", "")
        ).strip().upper()

        source = str(
            normalized.get("source", "")
        ).strip().lower()

        if not event_type:
            raise ValueError(
                "event_type must not be empty"
            )

        if not source:
            raise ValueError(
                "source must not be empty"
            )

        data = normalized.get("data", {})
        if not isinstance(data, dict):
            data = {}

        canonical_data = copy.deepcopy(data)

        canonical_data.pop("created_at", None)
        canonical_data.pop("timestamp", None)
        canonical_data.pop("event_id", None)

        import json
        import hashlib

        payload = {
            "event_type": event_type,
            "source": source,
            "data": canonical_data,
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

        fingerprint = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        return fingerprint

    def prioritize(self, event_or_normalized):
        """
        Determine an effective priority for an event.

        Existing event priority is used as the baseline.
        Critical and warning semantics can increase the
        effective priority without modifying the original event.
        """

        if isinstance(event_or_normalized, Event):
            normalized = self.classify(event_or_normalized)
        elif isinstance(event_or_normalized, dict):
            normalized = copy.deepcopy(event_or_normalized)
        else:
            raise TypeError(
                "event_or_normalized must be an Event or dict"
            )

        event_type = str(
            normalized.get("event_type", "")
        ).strip().upper()

        if not event_type:
            raise ValueError(
                "event_type must not be empty"
            )

        try:
            base_priority = int(
                normalized.get("priority", 0)
            )
        except (TypeError, ValueError):
            base_priority = 0

        effective_priority = base_priority

        critical_markers = (
            "CRITICAL",
            "EMERGENCY",
            "FAILURE",
            "FAILED",
            "ERROR",
        )

        warning_markers = (
            "WARNING",
            "WARN",
            "DEGRADED",
            "LOW",
        )

        if any(
            marker in event_type
            for marker in critical_markers
        ):
            effective_priority = max(
                effective_priority,
                4,
            )
        elif any(
            marker in event_type
            for marker in warning_markers
        ):
            effective_priority = max(
                effective_priority,
                2,
            )

        return {
            "event_id": normalized.get("event_id"),
            "event_type": event_type,
            "base_priority": base_priority,
            "effective_priority": effective_priority,
            "priority_changed": (
                effective_priority != base_priority
            ),
        }

    def correlate(self, event_a, event_b):
        """
        Determine deterministic relationships between two
        normalized or Event objects.

        This does not modify either input.
        """

        if isinstance(event_a, Event):
            first = self.classify(event_a)
        elif isinstance(event_a, dict):
            first = copy.deepcopy(event_a)
        else:
            raise TypeError(
                "event_a must be an Event or dict"
            )

        if isinstance(event_b, Event):
            second = self.classify(event_b)
        elif isinstance(event_b, dict):
            second = copy.deepcopy(event_b)
        else:
            raise TypeError(
                "event_b must be an Event or dict"
            )

        first_type = str(
            first.get("event_type", "")
        ).strip().upper()

        second_type = str(
            second.get("event_type", "")
        ).strip().upper()

        first_source = str(
            first.get("source", "")
        ).strip().lower()

        second_source = str(
            second.get("source", "")
        ).strip().lower()

        first_classification = str(
            first.get("classification", "")
        ).strip().lower()

        second_classification = str(
            second.get("classification", "")
        ).strip().lower()

        if not first_type or not second_type:
            raise ValueError(
                "both events must contain event_type"
            )

        relationships = []

        if (
            first_source
            and second_source
            and first_source == second_source
        ):
            relationships.append(
                "source_related"
            )

        if (
            first_classification
            and second_classification
            and first_classification == second_classification
        ):
            relationships.append(
                "classification_related"
            )

        type_groups = (
            (
                "ENVIRONMENT_",
                "environment_related",
            ),
            (
                "SYSTEM_",
                "system_related",
            ),
            (
                "TASK_",
                "task_related",
            ),
            (
                "GOAL_",
                "goal_related",
            ),
            (
                "REMINDER_",
                "reminder_related",
            ),
            (
                "BATTERY_",
                "device_related",
            ),
            (
                "DEVICE_",
                "device_related",
            ),
            (
                "USER_",
                "user_related",
            ),
        )

        for prefix, relationship in type_groups:
            if (
                first_type.startswith(prefix)
                and second_type.startswith(prefix)
            ):
                relationships.append(
                    relationship
                )
                break

        return {
            "related": bool(relationships),
            "relationships": relationships,
            "event_a": first.get("event_id"),
            "event_b": second.get("event_id"),
        }


event_intelligence = EventIntelligence()
