def build_system_dashboard(system):
    if not isinstance(system,dict):
        return {}
    return dict(system)


def system_dashboard_count(system):
    return len(build_system_dashboard(system))


def format_system_dashboard(system):
    values=build_system_dashboard(system)
    lines=[]
    for key, value in sorted(values.items()):
        lines.append("{}: {}".format(key, value))
    return chr(10).join(lines) if lines else "System Dashboard is empty."
