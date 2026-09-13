def notification_is_read(item):
    if not isinstance(item, dict):
        return False
    return bool(item.get("read", False))


def mark_notification_read(item):
    if not isinstance(item, dict):
        return item
    result = dict(item)
    result["read"] = True
    return result


def mark_notification_unread(item):
    if not isinstance(item, dict):
        return item
    result = dict(item)
    result["read"] = False
    return result


def unread_count(items):
    return sum(1 for item in (items or []) if isinstance(item, dict) and not notification_is_read(item))


def format_read_state(item):
    return "READ" if notification_is_read(item) else "UNREAD"
