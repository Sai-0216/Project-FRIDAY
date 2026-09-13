def filter_notifications(items, query='', notification_type=None):
    items = list(items or [])
    query = str(query or '').strip().lower()
    filtered = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if notification_type and item.get('type') != notification_type:
            continue
        if query:
            haystack = ' '.join(str(item.get(key, '')) for key in ('type', 'count', 'message')).lower()
            if query not in haystack:
                continue
        filtered.append(item)
    return filtered


def available_notification_types(items):
    types = set()
    for item in items or []:
        if isinstance(item, dict) and item.get('type'):
            types.add(str(item.get('type')))
    return sorted(types)


if __name__ == '__main__':
    sample = [
        {'type': 'activity', 'count': 1, 'message': '1 new activity detected.'},
        {'type': 'system', 'count': 1, 'message': 'System update ready.'},
        {'type': 'activity', 'count': 2, 'message': '2 new activities detected.'},
    ]
    print('QUERY:', filter_notifications(sample, query='activity'))
    print('TYPE:', filter_notifications(sample, notification_type='system'))
    print('TYPES:', available_notification_types(sample))
