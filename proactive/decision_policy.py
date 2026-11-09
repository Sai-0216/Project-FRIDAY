"""
Project FRIDAY
Phase 16.17-F

Attention-Aware Proactive Decision Policy

Uses:
    - Event type
    - Event priority
    - Current context
    - Urgency
    - Relevance
    - Combined Attention

Decision types:
    IGNORE
    NOTIFY
    SUGGEST
    CONFIRM

The policy does NOT execute actions.
"""


class DecisionPolicy:

    def __init__(self):
        self.enabled = True

    def decide(self, event, context=None):

        if not self.enabled:
            return None

        context = context or {}

        # --------------------------------------------------
        # REASONING SIGNALS
        # --------------------------------------------------

        urgency = context.get(
            "urgency",
            {}
        )

        urgency_score = urgency.get(
            "score",
            0
        )

        urgency_level = urgency.get(
            "level",
            "NONE"
        )

        relevance = context.get(
            "relevance",
            {}
        )

        relevance_score = relevance.get(
            "score",
            0
        )

        relevance_level = relevance.get(
            "level",
            "IRRELEVANT"
        )

        is_relevant = relevance.get(
            "relevant",
            False
        )

        attention = context.get(
            "attention",
            {}
        )

        attention_score = attention.get(
            "score",
            0
        )

        attention_level = attention.get(
            "level",
            "NONE"
        )

        print(
            "[DecisionPolicy] "
            f"Urgency={urgency_level} "
            f"Score={urgency_score}"
        )

        print(
            "[DecisionPolicy] "
            f"Relevance={relevance_level} "
            f"Score={relevance_score} "
            f"Relevant={is_relevant}"
        )

        print(
            "[DecisionPolicy] "
            f"Attention={attention_level} "
            f"Score={attention_score}"
        )

        event_type = event.event_type
        data = event.data or {}
        priority = event.priority

        is_quiet_hours = context.get(
            "is_quiet_hours",
            False
        )

        # --------------------------------------------------
        # NO ATTENTION
        # --------------------------------------------------

        if attention_score == 0:
            return {
                "action": "IGNORE",
                "level": 0,
                "reason": (
                    "Event requires no attention."
                ),
                "message": None,
                "intent": None,
                "parameters": {},
            }

        # --------------------------------------------------
        # BATTERY LOW
        # --------------------------------------------------

        if event_type == "BATTERY_LOW":

            battery = data.get("battery")

            charging = data.get(
                "charging",
                False
            )

            if charging:
                return {
                    "action": "IGNORE",
                    "level": 0,
                    "reason": (
                        "Battery is low but "
                        "the device is charging."
                    ),
                    "message": None,
                    "intent": None,
                    "parameters": {},
                }

            if (
                attention_score >= 4
                and battery is not None
                and battery <= 10
            ):
                return {
                    "action": "CONFIRM",
                    "level": 3,
                    "reason": (
                        "Critical battery condition "
                        "requires immediate attention."
                    ),
                    "message": (
                        f"Sir, your battery is critically "
                        f"low at {battery}%. Would you like "
                        f"me to enable battery saver?"
                    ),
                    "intent": "enable_battery_saver",
                    "parameters": {},
                }

            if (
                attention_score >= 3
                and battery is not None
                and battery <= 20
            ):
                return {
                    "action": "SUGGEST",
                    "level": 2,
                    "reason": (
                        "Battery level is low "
                        "and deserves attention."
                    ),
                    "message": (
                        f"Sir, your battery is at "
                        f"{battery}%. You may want to "
                        f"enable battery saver."
                    ),
                    "intent": "enable_battery_saver",
                    "parameters": {},
                }

            return {
                "action": "SUGGEST",
                "level": 2,
                "reason": (
                    "Battery condition "
                    "requires attention."
                ),
                "message": (
                    "Sir, your battery is "
                    "getting low."
                ),
                "intent": "enable_battery_saver",
                "parameters": {},
            }
        
        
        # --------------------------------------------------
        # ENVIRONMENT EVENTS
        # --------------------------------------------------

        if event_type == "ENVIRONMENT_CRITICAL":

            correlations = data.get(
                "correlations",
                []
            )

            memory_context = context.get(
                "environment_memory",
                {}
            )

            historical_trends = memory_context.get(
                "notable_trends",
                []
            )

            workload = data.get(
                "workload_context",
                {}
            )

            messages = []

            for finding in correlations:

                message = finding.get(
                    "message"
                )

                if message:
                    messages.append(
                        message
                    )

            # ----------------------------------------
            # Workload context
            # ----------------------------------------

            workload_types = workload.get(
                "types",
                []
            )

            workload_message = None

            trends = data.get(
                "trends",
                {}
            )

            trend_messages = []

            for trend in trends.values():

                trend_name = trend.get(
                    "name",
                    ""
                )

                trend_direction = trend.get(
                    "trend",
                    ""
                )

                if trend_direction == "INCREASING":

                    trend_messages.append(
                        f"{trend_name} usage is increasing."
                    )

                elif trend_direction == "DECREASING":

                    trend_messages.append(
                        f"{trend_name} usage is decreasing."
                    )

            if workload_types:

                readable_types = []

                for workload_type in workload_types:

                    readable_types.append(
                        str(
                            workload_type
                        ).replace(
                            "_",
                            " "
                        )
                    )

                workload_message = (
                    "Active workload: "
                    + ", ".join(
                        readable_types
                    )
                    + "."
                )

            # ----------------------------------------
            # Build message
            # ----------------------------------------

            message_parts = [
                (
                    "Sir, I detected a critical "
                    "system condition."
                )
            ]

            if messages:

                message_parts.extend(
                    messages
                )

            if trend_messages:

                message_parts.extend(
                    trend_messages
                )

            current_trend_pairs = set()

            for trend in data.get("trends", {}).values():

                name = trend.get("name")
                direction = trend.get("trend")

                if name and direction in ("INCREASING", "DECREASING"):

                    current_trend_pairs.add(
                        (name, direction)
                    )

            correlated_types = {
                finding.get("type")
                for finding in correlations
            }

            persistent_patterns = memory_context.get(
                "patterns",
                []
            )

            if persistent_patterns:

                pattern_messages = []

                for pattern in persistent_patterns:

                    pattern_type = pattern.get("type")
                    persistent = pattern.get("persistent", False)
                    confidence = pattern.get("confidence", "LOW")

                    if (
                        not persistent
                        or confidence not in ("HIGH", "MEDIUM")
                        or pattern_type in correlated_types
                    ):
                        continue

                    occurrences = pattern.get("occurrences", 0)
                    samples = pattern.get("samples", 0)

                    if pattern_type == "NETWORK_UNAVAILABLE":

                        pattern_messages.append(
                            "Wi-Fi has been unavailable repeatedly in recent observations."
                        )

                    elif pattern_type == "STORAGE_MEMORY_PRESSURE":

                        pattern_messages.append(
                            "Disk and RAM pressure has been persistent in recent observations."
                        )

                    elif pattern_type == "BATTERY_DISCHARGE":

                        pattern_messages.append(
                            "Low battery while not charging has recurred in recent observations."
                        )

                    elif pattern_type == "RESOURCE_PRESSURE":

                        pattern_messages.append(
                            f"Resource pressure has persisted across {occurrences} of {samples} recent observations."
                        )

                if pattern_messages:

                    message_parts.extend(
                        pattern_messages
                    )

            if historical_trends:

                historical_messages = []

                for trend in historical_trends:

                    name = trend.get("name")
                    direction = trend.get("trend")

                    if (
                        name
                        and direction in ("INCREASING", "DECREASING")
                        and (name, direction) not in current_trend_pairs
                    ):

                        if direction == "INCREASING":

                            historical_messages.append(
                                f"Recent history shows {name} usage is increasing."
                            )

                        elif direction == "DECREASING":

                            historical_messages.append(
                                f"Recent history shows {name} usage is decreasing."
                            )

                if historical_messages:

                    message_parts.extend(
                        historical_messages
                    )

            if workload_message:

                message_parts.append(
                    workload_message
                )

            message = " ".join(
                message_parts
            )

            return {
                "action": "NOTIFY",
                "level": 1,
                "reason": (
                    "Critical system/environment "
                    "condition requires attention."
                ),
                "message": message,
                "intent": None,
                "parameters": {},
            }

        if event_type == "ENVIRONMENT_WARNING":

            correlations = data.get(
                "correlations",
                []
            )

            memory_context = context.get(
                "environment_memory",
                {}
            )

            historical_trends = memory_context.get(
                "notable_trends",
                []
            )

            workload = data.get(
                "workload_context",
                {}
            )

            messages = []

            for finding in correlations:

                message = finding.get(
                    "message"
                )

                if message:
                    messages.append(
                        message
                    )

            # ----------------------------------------
            # Workload context
            # ----------------------------------------

            workload_types = workload.get(
                "types",
                []
            )

            workload_message = None

            trends = data.get(
                "trends",
                {}
            )

            trend_messages = []

            for trend in trends.values():

                trend_name = trend.get(
                    "name",
                    ""
                )

                trend_direction = trend.get(
                    "trend",
                    ""
                )

                if trend_direction == "INCREASING":

                    trend_messages.append(
                        f"{trend_name} usage is increasing."
                    )

                elif trend_direction == "DECREASING":

                    trend_messages.append(
                        f"{trend_name} usage is decreasing."
                    )

            if workload_types:

                readable_types = []

                for workload_type in workload_types:

                    readable_types.append(
                        str(
                            workload_type
                        ).replace(
                            "_",
                            " "
                        )
                    )

                workload_message = (
                    "Active workload: "
                    + ", ".join(
                        readable_types
                    )
                    + "."
                )

            # ----------------------------------------
            # Build message
            # ----------------------------------------

            message_parts = [
                (
                    "Sir, I noticed a system "
                    "condition that may need "
                    "your attention."
                )
            ]

            if messages:

                message_parts.extend(
                    messages
                )

            if trend_messages:

                message_parts.extend(
                    trend_messages
                )

            current_trend_pairs = set()

            for trend in data.get("trends", {}).values():

                name = trend.get("name")
                direction = trend.get("trend")

                if name and direction in ("INCREASING", "DECREASING"):

                    current_trend_pairs.add(
                        (name, direction)
                    )

            correlated_types = {
                finding.get("type")
                for finding in correlations
            }

            persistent_patterns = memory_context.get(
                "patterns",
                []
            )

            if persistent_patterns:

                pattern_messages = []

                for pattern in persistent_patterns:

                    pattern_type = pattern.get("type")
                    persistent = pattern.get("persistent", False)
                    confidence = pattern.get("confidence", "LOW")

                    if (
                        not persistent
                        or confidence not in ("HIGH", "MEDIUM")
                        or pattern_type in correlated_types
                    ):
                        continue

                    occurrences = pattern.get("occurrences", 0)
                    samples = pattern.get("samples", 0)

                    if pattern_type == "NETWORK_UNAVAILABLE":

                        pattern_messages.append(
                            "Wi-Fi has been unavailable repeatedly in recent observations."
                        )

                    elif pattern_type == "STORAGE_MEMORY_PRESSURE":

                        pattern_messages.append(
                            "Disk and RAM pressure has been persistent in recent observations."
                        )

                    elif pattern_type == "BATTERY_DISCHARGE":

                        pattern_messages.append(
                            "Low battery while not charging has recurred in recent observations."
                        )

                    elif pattern_type == "RESOURCE_PRESSURE":

                        pattern_messages.append(
                            f"Resource pressure has persisted across {occurrences} of {samples} recent observations."
                        )

                if pattern_messages:

                    message_parts.extend(
                        pattern_messages
                    )

            if historical_trends:

                historical_messages = []

                for trend in historical_trends:

                    name = trend.get("name")
                    direction = trend.get("trend")

                    if (
                        name
                        and direction in ("INCREASING", "DECREASING")
                        and (name, direction) not in current_trend_pairs
                    ):

                        if direction == "INCREASING":

                            historical_messages.append(
                                f"Recent history shows {name} usage is increasing."
                            )

                        elif direction == "DECREASING":

                            historical_messages.append(
                                f"Recent history shows {name} usage is decreasing."
                            )

                if historical_messages:

                    message_parts.extend(
                        historical_messages
                    )

            if workload_message:

                message_parts.append(
                    workload_message
                )

            message = " ".join(
                message_parts
            )

            return {
                "action": "NOTIFY",
                "level": 1,
                "reason": (
                    "Elevated system/environment "
                    "condition deserves attention."
                ),
                "message": message,
                "intent": None,
                "parameters": {},
            }
        # --------------------------------------------------
        # REMINDER EVENT
        # --------------------------------------------------

        if event_type == "REMINDER_EVENT":

            if (
                is_quiet_hours
                and attention_score < 4
            ):
                return {
                    "action": "IGNORE",
                    "level": 0,
                    "reason": (
                        "Reminder occurred during "
                        "quiet hours and does not "
                        "deserve critical attention."
                    ),
                    "message": None,
                    "intent": None,
                    "parameters": {},
                }

            if attention_score >= 3:
                return {
                    "action": "NOTIFY",
                    "level": 1,
                    "reason": (
                        "Reminder has sufficient "
                        "attention priority."
                    ),
                    "message": data.get(
                        "message",
                        "You have a reminder."
                    ),
                    "intent": None,
                    "parameters": {},
                }

            if attention_score >= 2:
                return {
                    "action": "NOTIFY",
                    "level": 1,
                    "reason": (
                        "Scheduled reminder "
                        "is due."
                    ),
                    "message": data.get(
                        "message",
                        "You have a reminder."
                    ),
                    "intent": None,
                    "parameters": {},
                }

            return {
                "action": "IGNORE",
                "level": 0,
                "reason": (
                    "Reminder does not "
                    "deserve attention."
                ),
                "message": None,
                "intent": None,
                "parameters": {},
            }

        # --------------------------------------------------
        # TIME EVENT
        # --------------------------------------------------

        if event_type == "TIME_EVENT":

            # Critical attention
            if (
                attention_score >= 4
                and (
                    priority >= 5
                    or urgency_score >= 4
                )
            ):
                return {
                    "action": "CONFIRM",
                    "level": 3,
                    "reason": (
                        "High-priority scheduled "
                        "event requires immediate "
                        "attention."
                    ),
                    "message": data.get(
                        "message",
                        "You have an important "
                        "scheduled event."
                    ),
                    "intent": data.get(
                        "intent"
                    ),
                    "parameters": data.get(
                        "parameters",
                        {}
                    ),
                }

            # High attention
            if (
                attention_score >= 3
                and not is_quiet_hours
            ):
                return {
                    "action": "NOTIFY",
                    "level": 1,
                    "reason": (
                        "Important scheduled event "
                        "deserves attention."
                    ),
                    "message": data.get(
                        "message",
                        "You have an important "
                        "scheduled event."
                    ),
                    "intent": None,
                    "parameters": {},
                }

            # Normal attention
            if (
                attention_score >= 2
                and not is_quiet_hours
            ):
                return {
                    "action": "NOTIFY",
                    "level": 1,
                    "reason": (
                        "Scheduled event "
                        "deserves attention."
                    ),
                    "message": data.get(
                        "message",
                        "You have a scheduled event."
                    ),
                    "intent": None,
                    "parameters": {},
                }

            # Low attention during quiet hours
            if is_quiet_hours:
                return {
                    "action": "IGNORE",
                    "level": 0,
                    "reason": (
                        "Low or normal-priority "
                        "event occurred during "
                        "quiet hours."
                    ),
                    "message": None,
                    "intent": None,
                    "parameters": {},
                }

            return {
                "action": "SUGGEST",
                "level": 2,
                "reason": (
                    "Low-priority scheduled "
                    "event."
                ),
                "message": data.get(
                    "message",
                    "There is a scheduled event."
                ),
                "intent": data.get(
                    "intent"
                ),
                "parameters": data.get(
                    "parameters",
                    {}
                ),
            }

        # --------------------------------------------------
        # UNKNOWN EVENT
        # --------------------------------------------------

        return {
            "action": "IGNORE",
            "level": 0,
            "reason": (
                "No proactive policy exists "
                "for this event type."
            ),
            "message": None,
            "intent": None,
            "parameters": {},
        }


decision_policy = DecisionPolicy()