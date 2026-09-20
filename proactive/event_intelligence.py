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

    def proactive_analysis(self, event):
        """
        Prepare event intelligence for the existing proactive
        decision pipeline.

        This method only analyzes the event. It does not execute
        actions or modify the Event object.
        """

        if not isinstance(event, Event):
            raise TypeError(
                "event must be an Event object"
            )

        classification = self.classify(event)
        priority = self.prioritize(event)
        fingerprint = self.deduplication_fingerprint(event)

        return {
            "classification": classification.get(
                "classification",
                "unknown",
            ),
            "base_priority": priority.get(
                "base_priority",
                0,
            ),
            "effective_priority": priority.get(
                "effective_priority",
                0,
            ),
            "priority_changed": priority.get(
                "priority_changed",
                False,
            ),
            "deduplication_fingerprint": fingerprint,
        }

    def record_to_world_model(
        self,
        event,
        model=None,
    ):
        """
        Persist an Event through the existing World Model API.

        The World Model remains the owner of persistence.
        """

        if not isinstance(event, Event):
            raise TypeError(
                "event must be an Event object"
            )

        normalized = self.normalize(event)

        if model is None:
            from world_model import world_model
            model = world_model

        if not hasattr(model, "record_event"):
            raise TypeError(
                "model must provide record_event()"
            )

        return model.record_event(
            event,
            event_id=normalized["event_id"],
        )

    def temporal_relation(
        self,
        event_a,
        event_b,
        near_seconds=60,
    ):
        """
        Determine the temporal relationship between two events.

        Returns ordering, time difference, and proximity without
        modifying either input.
        """

        if isinstance(event_a, Event):
            first = self.normalize(event_a)
        elif isinstance(event_a, dict):
            first = copy.deepcopy(event_a)
        else:
            raise TypeError(
                "event_a must be an Event or dict"
            )

        if isinstance(event_b, Event):
            second = self.normalize(event_b)
        elif isinstance(event_b, dict):
            second = copy.deepcopy(event_b)
        else:
            raise TypeError(
                "event_b must be an Event or dict"
            )

        first_time = first.get("created_at")
        second_time = second.get("created_at")

        if not first_time or not second_time:
            raise ValueError(
                "both events must contain created_at"
            )

        first_dt = datetime.fromisoformat(
            str(first_time)
        )
        second_dt = datetime.fromisoformat(
            str(second_time)
        )

        difference = (
            second_dt - first_dt
        ).total_seconds()

        absolute_difference = abs(difference)

        try:
            near_seconds = float(near_seconds)
        except (TypeError, ValueError):
            near_seconds = 60.0

        if near_seconds < 0:
            near_seconds = 0.0

        if difference < 0:
            ordering = "after"
        elif difference > 0:
            ordering = "before"
        else:
            ordering = "simultaneous"

        if absolute_difference == 0:
            proximity = "simultaneous"
        elif absolute_difference <= near_seconds:
            proximity = "near"
        else:
            proximity = "distant"

        return {
            "event_a": first.get("event_id"),
            "event_b": second.get("event_id"),
            "ordering": ordering,
            "difference_seconds": difference,
            "absolute_difference_seconds": absolute_difference,
            "proximity": proximity,
        }

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

    def query_events(
        self,
        events,
        event_type=None,
        source=None,
        classification=None,
        min_priority=None,
        start_time=None,
        end_time=None,
        limit=None,
    ):
        """
        Query event intelligence without modifying the source events.

        Supports filtering by event type, source, classification,
        minimum priority, time range, and result limit.

        Event objects are normalized before filtering. Dictionary
        inputs are copied before processing.
        """

        if events is None:
            raise TypeError("events must be an iterable of Event or dict objects")

        try:
            event_items = list(events)
        except TypeError:
            raise TypeError(
                "events must be an iterable of Event or dict objects"
            )

        normalized_events = []

        for event in event_items:
            if isinstance(event, Event):
                normalized = self.classify(event)
            elif isinstance(event, dict):
                normalized = self.classify(event)
            else:
                raise TypeError(
                    "events must contain only Event or dict objects"
                )

            normalized_events.append(normalized)

        normalized_event_type = (
            str(event_type).strip().upper()
            if event_type is not None
            else None
        )

        normalized_source = (
            str(source).strip().lower()
            if source is not None
            else None
        )

        normalized_classification = (
            str(classification).strip().lower()
            if classification is not None
            else None
        )

        if normalized_event_type == "":
            normalized_event_type = None

        if normalized_source == "":
            normalized_source = None

        if normalized_classification == "":
            normalized_classification = None

        if min_priority is not None:
            try:
                normalized_min_priority = int(min_priority)
            except (TypeError, ValueError):
                normalized_min_priority = 0
        else:
            normalized_min_priority = None

        parsed_start_time = None
        parsed_end_time = None

        if start_time is not None:
            try:
                parsed_start_time = datetime.fromisoformat(
                    str(start_time)
                )
            except (TypeError, ValueError):
                raise ValueError(
                    "start_time must be a valid ISO timestamp"
                )

        if end_time is not None:
            try:
                parsed_end_time = datetime.fromisoformat(
                    str(end_time)
                )
            except (TypeError, ValueError):
                raise ValueError(
                    "end_time must be a valid ISO timestamp"
                )

        if (
            parsed_start_time is not None
            and parsed_end_time is not None
            and parsed_start_time > parsed_end_time
        ):
            raise ValueError(
                "start_time must not be later than end_time"
            )

        results = []

        for normalized in normalized_events:
            current_type = str(
                normalized.get("event_type", "")
            ).strip().upper()

            current_source = str(
                normalized.get("source", "")
            ).strip().lower()

            current_classification = str(
                normalized.get("classification", "")
            ).strip().lower()

            try:
                current_priority = int(
                    normalized.get("priority", 0)
                )
            except (TypeError, ValueError):
                current_priority = 0

            if (
                normalized_event_type is not None
                and current_type != normalized_event_type
            ):
                continue

            if (
                normalized_source is not None
                and current_source != normalized_source
            ):
                continue

            if (
                normalized_classification is not None
                and current_classification != normalized_classification
            ):
                continue

            if (
                normalized_min_priority is not None
                and current_priority < normalized_min_priority
            ):
                continue

            created_at = normalized.get("created_at")

            if (
                parsed_start_time is not None
                or parsed_end_time is not None
            ):
                if not created_at:
                    continue

                try:
                    created_at_dt = datetime.fromisoformat(
                        str(created_at)
                    )
                except (TypeError, ValueError):
                    continue

                if (
                    parsed_start_time is not None
                    and created_at_dt < parsed_start_time
                ):
                    continue

                if (
                    parsed_end_time is not None
                    and created_at_dt > parsed_end_time
                ):
                    continue

            results.append(copy.deepcopy(normalized))

        if limit is not None:
            try:
                normalized_limit = int(limit)
            except (TypeError, ValueError):
                normalized_limit = 0

            if normalized_limit < 0:
                normalized_limit = 0

            results = results[:normalized_limit]

        return results


    def detect_patterns(self, events, min_occurrences=2):
        """
        Detect repeated event-type patterns.

        This method analyzes event history without modifying the
        source events or existing event-management components.
        """

        if events is None:
            raise TypeError(
                "events must be an iterable of Event or dict objects"
            )

        try:
            event_items = list(events)
        except TypeError:
            raise TypeError(
                "events must be an iterable of Event or dict objects"
            )

        try:
            minimum = int(min_occurrences)
        except (TypeError, ValueError):
            minimum = 2

        if minimum < 1:
            minimum = 1

        counts = {}
        total_events = 0

        for event in event_items:
            if isinstance(event, Event):
                normalized = self.classify(event)
            elif isinstance(event, dict):
                normalized = self.classify(event)
            else:
                raise TypeError(
                    "events must contain only Event or dict objects"
                )

            event_type = str(
                normalized.get("event_type", "")
            ).strip().upper()

            if not event_type:
                continue

            counts[event_type] = counts.get(event_type, 0) + 1
            total_events += 1

        patterns = []

        for event_type, occurrences in counts.items():
            if occurrences < minimum:
                continue

            frequency = (
                occurrences / total_events
                if total_events > 0
                else 0.0
            )

            if occurrences >= 4:
                confidence = "HIGH"
            elif occurrences >= 2:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            patterns.append({
                "event_type": event_type,
                "occurrences": occurrences,
                "total_events": total_events,
                "frequency": round(frequency, 3),
                "persistent": occurrences >= minimum,
                "confidence": confidence,
            })

        return sorted(
            patterns,
            key=lambda pattern: pattern["event_type"],
        )



event_intelligence = EventIntelligence()
