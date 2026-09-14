"""
Project FRIDAY
Frontend Proactive Dashboard

Adapts proactive decisions into frontend notification data.
"""


def build_proactive_notification(decision):
    if not isinstance(decision, dict):
        return {}

    action = decision.get("action")

    if action not in ("NOTIFY", "SUGGEST", "CONFIRM"):
        return {}

    message = decision.get("message", "")

    if not message:
        return {}

    priority = decision.get("priority", "normal")

    return {
        "type": "proactive",
        "priority": priority,
        "message": message,
        "action": action,
        "read": False,
        "proactive": True,
    }


def build_proactive_notifications(decisions):
    if not isinstance(decisions, (list, tuple)):
        return []

    notifications = []

    for decision in decisions:
        notification = build_proactive_notification(decision)

        if notification:
            notifications.append(notification)

    return notifications


def proactive_notification_count(decisions):
    return len(build_proactive_notifications(decisions))


def format_proactive_dashboard(decisions):
    notifications = build_proactive_notifications(decisions)

    if not notifications:
        return "No proactive notifications."

    lines = []

    for notification in notifications:
        lines.append(
            "[{}] {}: {}".format(
                notification.get("action", "UNKNOWN"),
                notification.get("priority", "normal"),
                notification.get("message", ""),
            )
        )

    return chr(10).join(lines)
