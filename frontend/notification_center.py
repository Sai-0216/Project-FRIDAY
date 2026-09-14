def build_notification_center(items):
    return [dict(x) for x in (items or []) if isinstance(x, dict)]


def notification_center_count(items):
    return len(build_notification_center(items))


def format_notification_center(items):
    values=build_notification_center(items)
    if not values:
        return "Notification Center is empty."
    lines=[]
    for item in reversed(values):
        state="READ" if item.get("read", False) else "UNREAD"
        kind=item.get("type", "unknown")
        priority=item.get("priority", "normal")
        message=item.get("message", "")
        lines.append("[{}] {}/{}: {}".format(state, kind, priority, message))
    return chr(10).join(lines)
