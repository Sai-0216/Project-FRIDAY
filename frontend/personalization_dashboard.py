"""
Project FRIDAY
Frontend Personalization Dashboard
"""

try:
    from proactive.preference_memory import preference_memory
    from proactive.response_adaptation import ResponseAdaptation
except ModuleNotFoundError:
    from preference_memory import preference_memory
    from response_adaptation import ResponseAdaptation


def build_personalization_dashboard(preferences=None):
    if preferences is None:
        preferences = preference_memory.recent(20)

    if not isinstance(preferences, list):
        preferences = []

    profile = ResponseAdaptation.personalize(preferences)

    return {
        "preferences": list(preferences),
        "signals": profile.get("signals", {}),
        "rules": profile.get("rules", {}),
    }


def personalization_preference_count(preferences=None):
    dashboard = build_personalization_dashboard(preferences)
    return len(dashboard.get("preferences", []))


def personalization_rule_count(preferences=None):
    dashboard = build_personalization_dashboard(preferences)
    return len(dashboard.get("rules", {}))


def format_personalization_dashboard(preferences=None):
    dashboard = build_personalization_dashboard(preferences)

    preferences = dashboard.get("preferences", [])
    rules = dashboard.get("rules", {})

    if not preferences and not rules:
        return "No personalization data."

    lines = [
        "Personalization Dashboard",
        "Preferences: {}".format(len(preferences)),
        "Rules: {}".format(len(rules)),
    ]

    if rules:
        lines.append("")
        lines.append("Active Rules:")

        for key, value in rules.items():
            lines.append("{}: {}".format(key, value))

    return chr(10).join(lines)
