from datetime import datetime


class Event:
    """
    Represents something that happened which FRIDAY may need to process.
    """

    def __init__(
        self,
        event_type,
        source,
        data=None,
        priority=0
    ):
        self.event_type = event_type
        self.source = source
        self.data = data or {}
        self.priority = priority
        self.created_at = datetime.now()

    def __repr__(self):
        return (
            f"Event("
            f"type='{self.event_type}', "
            f"source='{self.source}', "
            f"priority={self.priority}, "
            f"data={self.data}"
            f")"
        )