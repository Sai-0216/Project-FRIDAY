def new_activity_count(previous, current):
    previous = tuple(previous or ())
    current = tuple(current or ())
    if len(current) <= len(previous):
        return 0
    return len(current) - len(previous)


def build_activity_notification(previous, current):
    count = new_activity_count(previous, current)
    if count <= 0:
        return None
    return {
        "type": "activity",
        "count": count,
        "message": "{} new activit{} detected.".format(count, "y" if count == 1 else "ies"),
    }


def format_activity_notification(notification):
    if not notification:
        return "No new activity."
    return notification.get("message", "New activity detected.")


if __name__ == "__main__":
    previous = (("saicharan", "open notepad", "completed"),)
    current = previous + (("saicharan", "open calculator", "completed"),)
    notification = build_activity_notification(previous, current)
    print('COUNT:', new_activity_count(previous, current))
    print('NOTIFICATION:', notification)
    print('FORMAT:', format_activity_notification(notification))
    print('NONE:', format_activity_notification(None))
