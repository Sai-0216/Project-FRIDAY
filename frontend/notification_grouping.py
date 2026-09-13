def group_notifications(items):
    groups = {}
    order = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        key = (item.get("type", "unknown"), item.get("priority", "normal"))
        if key not in groups:
            groups[key] = {
                "type": key[0],
                "priority": key[1],
                "count": 0,
                "items": [],
            }
            order.append(key)
        groups[key]["count"] += 1
        groups[key]["items"].append(dict(item))
    return [groups[key] for key in order]


def format_notification_groups(groups):
    groups = list(groups or [])
    if not groups:
        return "No notification groups."
    lines = []
    for group in groups:
        label = "{} / {}".format(group.get("type", "unknown"), group.get("priority", "normal"))
        lines.append("{}: {} notification{}".format(label, group.get("count", 0), "" if group.get("count", 0) == 1 else "s"))
    return chr(10).join(lines)


if __name__ == "__main__":
    sample = [
        {"type": "activity", "priority": "normal", "message": "A"},
        {"type": "activity", "priority": "normal", "message": "B"},
        {"type": "activity", "priority": "high", "message": "C"},
        {"type": "activity", "priority": "normal", "message": "D"},
    ]
    groups = group_notifications(sample)
    print('GROUPS:', groups)
    print('FORMAT:')
    print(format_notification_groups(groups))
