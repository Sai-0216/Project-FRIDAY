from datetime import datetime
import copy

from .event import Event


class EventIntelligence:
    """
    Phase 33.1

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

        event_type = str(event.event_type).strip()
        source = str(event.source).strip()

        if not event_type:
            raise ValueError("event_type must not be empty")

        if not source:
            raise ValueError("source must not be empty")

        try:
            priority = int(event.priority)
        except (TypeError, ValueError):
            priority = 0

        data = event.data if isinstance(event.data, dict) else {}

        return {
            "event_type": event_type,
            "source": source,
            "priority": priority,
            "created_at": created_at,
            "data": copy.deepcopy(data),
        }


event_intelligence = EventIntelligence()
