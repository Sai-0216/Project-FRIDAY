def previous_index(index, count):
    if count <= 0:
        return None
    try:
        index = int(index)
    except (TypeError, ValueError):
        return None
    return max(0, min(index - 1, count - 1))


def next_index(index, count):
    if count <= 0:
        return None
    try:
        index = int(index)
    except (TypeError, ValueError):
        return None
    return min(index + 1, count - 1)


def navigation_state(index, count):
    if count <= 0:
        return {"index": None, "count": 0, "has_previous": False, "has_next": False}
    try:
        index = int(index)
    except (TypeError, ValueError):
        index = 0
    index = max(0, min(index, count - 1))
    return {
        "index": index,
        "count": count,
        "has_previous": index > 0,
        "has_next": index < count - 1,
    }


if __name__ == "__main__":
    print('PREV:', previous_index(1, 3))
    print('NEXT:', next_index(1, 3))
    print('FIRST PREV:', previous_index(0, 3))
    print('LAST NEXT:', next_index(2, 3))
    print('EMPTY:', navigation_state(0, 0))
