PRIORITY_VALUES = {"high": 3, "normal": 2, "low": 1}


def notification_priority(notification):
    if not isinstance(notification, dict):
        return 1
    value = str(notification.get("priority", "normal")).lower()
    return PRIORITY_VALUES.get(value, 1)


def sort_notifications(items, descending=True):
    items = list(items or [])
    return sorted(items, key=notification_priority, reverse=bool(descending))


def set_notification_priority(notification, priority):
    if not isinstance(notification, dict):
        return None
    item = dict(notification)
    value = str(priority or "normal").lower()
    if value not in PRIORITY_VALUES:
        value = "normal"
    item["priority"] = value
    return item


if __name__ == "__main__":
    sample = [
        {"type": "activity", "priority": "low", "message": "Low"},
        {"type": "activity", "priority": "high", "message": "High"},
        {"type": "activity", "priority": "normal", "message": "Normal"},
    ]
    print('PRIORITIES:', [notification_priority(item) for item in sample])
    print('SORTED:', sort_notifications(sample))
    print('SET:', set_notification_priority(sample[0], 'high'))
