"""
Project FRIDAY
Frontend Security Dashboard
"""

FORBIDDEN_PERMISSION_KEYS = {
    "autonomy_level",
    "execution_permissions",
    "trusted_actions",
    "authorization",
}

SECRET_KEYS = {
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
}


def validate_security_state(state):
    if not isinstance(state, dict):
        return {
            "authenticated": False,
            "authorized": False,
            "secrets_present": False,
            "unsafe_permissions": False,
            "status": "BLOCKED",
        }

    authenticated = state.get("authenticated") is True
    authorized = state.get("authorized") is True

    secrets_present = any(
        key in state and state.get(key)
        for key in SECRET_KEYS
    )

    unsafe_permissions = any(
        key in state
        for key in FORBIDDEN_PERMISSION_KEYS
    )

    if unsafe_permissions:
        status = "BLOCKED"
    elif not authenticated:
        status = "UNAUTHENTICATED"
    elif not authorized:
        status = "UNAUTHORIZED"
    else:
        status = "SECURE"

    return {
        "authenticated": authenticated,
        "authorized": authorized,
        "secrets_present": secrets_present,
        "unsafe_permissions": unsafe_permissions,
        "status": status,
    }


def security_check_count(state):
    result = validate_security_state(state)
    return sum(
        1
        for key in (
            "authenticated",
            "authorized",
            "secrets_present",
            "unsafe_permissions",
        )
        if result.get(key) is True
    )


def format_security_dashboard(state):
    result = validate_security_state(state)

    lines = [
        "Security Dashboard",
        "Status: {}".format(result.get("status", "BLOCKED")),
        "Authenticated: {}".format(result.get("authenticated", False)),
        "Authorized: {}".format(result.get("authorized", False)),
        "Secrets Present: {}".format(result.get("secrets_present", False)),
        "Unsafe Permissions: {}".format(result.get("unsafe_permissions", False)),
    ]

    return chr(10).join(lines)
