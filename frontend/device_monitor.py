def device_signature(devices):
    signature = {}
    for device in devices or []:
        if isinstance(device, dict):
            device_id = str(device.get("device_id", "unknown"))
            online = bool(device.get("online", False))
        else:
            device_id = str(device)
            online = True
        signature[device_id] = online
    return signature


def detect_device_changes(previous, current):
    previous = previous or {}
    current = current or {}
    changes = []

    for device_id in sorted(set(previous) | set(current)):
        if device_id not in previous:
            changes.append({"device_id": device_id, "event": "connected", "online": current[device_id]})
        elif device_id not in current:
            changes.append({"device_id": device_id, "event": "disconnected", "online": False})
        elif previous[device_id] != current[device_id]:
            changes.append({
                "device_id": device_id,
                "event": "online" if current[device_id] else "offline",
                "online": current[device_id],
            })

    return changes


def monitoring_snapshot(devices):
    signature = device_signature(devices)
    return {
        "device_count": len(signature),
        "online_count": sum(1 for online in signature.values() if online),
        "offline_count": sum(1 for online in signature.values() if not online),
        "devices": signature,
    }


if __name__ == "__main__":
    before = device_signature([
        {"device_id": "saicharan", "online": True},
    ])
    after = device_signature([
        {"device_id": "saicharan", "online": False},
        {"device_id": "laptop", "online": True},
    ])
    print("CHANGES:", detect_device_changes(before, after))
    print("SNAPSHOT:", monitoring_snapshot([
        {"device_id": "saicharan", "online": False},
        {"device_id": "laptop", "online": True},
    ]))
