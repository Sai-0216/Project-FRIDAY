"""
Project FRIDAY
AI Planner
"""

from proactive.episodic_memory import episodic_memory
import json
import re
from urllib.parse import quote_plus

from ai import ai


class Planner:

    # ========================================
    # SUPPORTED INTENTS
    # ========================================

    SUPPORTED_INTENTS = {
        "open_app",
        "open_browser",
        "google_search",
        "youtube_search",

        "volume_up",
        "volume_down",
        "mute",
        "unmute",

        "brightness_up",
        "brightness_down",

        "battery",
        "cpu",
        "ram",
        "disk",

        "open_camera",
        "close_camera",
        "take_photo",

        "take_screenshot",
        "analyze_screen",

        "remember",
        "recall",

        "add_habit",
        "list_habits",
        "habit_progress",
        "delete_habit",
        "complete_habit",

        "daily_briefing",
        "today_plan",
        "daily_progress",

        "add_reminder",
        "list_reminders",
        "remove_reminder",

        "run_workflow",
        "stop_workflow",
        "resume_tasks",
        "retry_task",
        "check_reasoning",
        "workflow_status",
        "list_workflows",
        "show_workflow",
        "delete_workflow",
    }

    # ========================================
    # MAIN PLANNER
    # ========================================

    def _cognitive_pattern(self, command):
        normalized = " ".join(str(command).strip().lower().split())
        if not normalized:
            return None

        try:
            records = episodic_memory.recent(50)
        except Exception as e:
            print("[PLANNER] Cognitive pattern analysis unavailable:", repr(e))
            return None

        matches = []
        for record in records:
            if not isinstance(record, dict):
                continue
            event = " ".join(str(record.get("event", "")).strip().lower().split())
            if event == normalized:
                matches.append(record)

        if len(matches) < 2:
            return None

        completed = sum(1 for record in matches if record.get("outcome") == "completed")
        partial = sum(1 for record in matches if record.get("outcome") == "partial")
        failed = sum(1 for record in matches if record.get("outcome") == "failed")
        total = len(matches)
        success_rate = round(completed / total, 2) if total else 0.0
        failure_rate = round(failed / total, 2) if total else 0.0

        recent_matches = matches[-3:]
        recent_completed = sum(1 for record in recent_matches if record.get("outcome") == "completed")
        recent_failed = sum(1 for record in recent_matches if record.get("outcome") == "failed")
        recent_total = len(recent_matches)
        recent_success_rate = round(recent_completed / recent_total, 2) if recent_total else 0.0
        recent_failure_rate = round(recent_failed / recent_total, 2) if recent_total else 0.0

        evidence_strength = round(min(1.0, total / 5.0), 2)
        adaptive_score = round(
            (success_rate * 0.4) + (recent_success_rate * 0.6),
            2
        )
        adaptive_failure_score = round(
            (failure_rate * 0.4) + (recent_failure_rate * 0.6),
            2
        )

        if adaptive_score >= 0.6 and adaptive_score > adaptive_failure_score:
            recommendation = "prefer_successful_strategy"
        elif adaptive_failure_score >= 0.6 and adaptive_failure_score > adaptive_score:
            recommendation = "avoid_failed_strategy"
        else:
            recommendation = "use_with_caution"

        confidence = round(
            max(adaptive_score, adaptive_failure_score) * evidence_strength,
            2
        )

        strategy_counts = {}
        for record in matches:
            context = record.get("context", {})
            if not isinstance(context, dict):
                continue
            intent = context.get("intent")
            if not intent:
                continue
            strategy_key = str(intent)
            strategy_counts[strategy_key] = strategy_counts.get(strategy_key, 0) + 1

        strategy_reliability = {}
        for strategy in strategy_counts:
            strategy_records = [r for r in matches if isinstance(r.get("context", {}), dict) and str(r.get("context", {}).get("intent", "")) == strategy]
            strategy_total = len(strategy_records)
            strategy_completed = sum(1 for r in strategy_records if r.get("outcome") == "completed")
            strategy_failed = sum(1 for r in strategy_records if r.get("outcome") == "failed")
            strategy_reliability[strategy] = {"occurrences": strategy_total, "completed": strategy_completed, "failed": strategy_failed, "success_rate": round(strategy_completed / strategy_total, 2) if strategy_total else 0.0, "failure_rate": round(strategy_failed / strategy_total, 2) if strategy_total else 0.0}

        preferred_strategy = None
        if strategy_reliability:
            eligible_strategies = {
                strategy: stats
                for strategy, stats in strategy_reliability.items()
                if stats["failure_rate"] < 0.5
            }

            if eligible_strategies:
                preferred_strategy = max(
                    eligible_strategies,
                    key=lambda strategy: (
                        eligible_strategies[strategy]["success_rate"],
                        -eligible_strategies[strategy]["failure_rate"],
                        eligible_strategies[strategy]["occurrences"],
                    ),
                )

        pattern = {
            "command": normalized,
            "occurrences": total,
            "completed": completed,
            "partial": partial,
            "failed": failed,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "recent_success_rate": recent_success_rate,
            "recent_failure_rate": recent_failure_rate,
            "evidence_strength": evidence_strength,
            "adaptive_score": adaptive_score,
            "adaptive_failure_score": adaptive_failure_score,
            "confidence": confidence,
            "recommendation": recommendation,
            "strategy_counts": strategy_counts,
            "strategy_reliability": strategy_reliability,
            "conflict_resolution": max(eligible_strategies, key=lambda strategy: (eligible_strategies[strategy]["success_rate"], -eligible_strategies[strategy]["failure_rate"], eligible_strategies[strategy]["occurrences"])) if len(strategy_reliability) > 1 and eligible_strategies else None,
            "preferred_strategy": preferred_strategy,
            "preferred_strategy_reliability": strategy_reliability.get(preferred_strategy, {}).get("success_rate", 0.0) if preferred_strategy else 0.0
        }

        print("[PLANNER] Cognitive pattern:", pattern)
        return pattern

    def _cognitive_feedback(self, command):
        try:
            experiences = episodic_memory.search(command, limit=5)
        except Exception as e:
            print("[PLANNER] Cognitive feedback unavailable:", repr(e))
            return ""

        if not experiences:
            return ""

        feedback = []
        for experience in experiences:
            if not isinstance(experience, dict):
                continue

            outcome = experience.get("outcome")

            if outcome == "completed":
                quality = "successful"
            elif outcome == "partial":
                quality = "partially_successful"
            elif outcome == "failed":
                quality = "failed_avoid_repeating"
            else:
                quality = "unknown"

            feedback.append({
                "event": experience.get("event"),
                "context": experience.get("context", {}),
                "outcome": outcome,
                "quality": quality
            })

        pattern = self._cognitive_pattern(command)

        if not feedback and pattern is None:
            return ""

        feedback.sort(
            key=lambda item: {
                "successful": 0,
                "partially_successful": 1,
                "failed_avoid_repeating": 2,
                "unknown": 3
            }.get(item.get("quality"), 3)
        )

        payload = {
            "experiences": feedback,
            "pattern": pattern,
            "strategy_guidance": None,
            "failure_avoidance": None,


        }

        if pattern and pattern.get("preferred_strategy"):
            payload["strategy_guidance"] = {
                "preferred_strategy": pattern.get("preferred_strategy"),
                "confidence": pattern.get("confidence", 0.0),
                "reliability": pattern.get("preferred_strategy_reliability", 0.0),
                "decision_quality": "strong" if pattern.get("confidence", 0.0) >= 0.7 and pattern.get("preferred_strategy_reliability", 0.0) >= 0.8 else "moderate" if pattern.get("confidence", 0.0) >= 0.4 else "weak",
                "calibration": "high" if pattern.get("confidence", 0.0) >= 0.7 else "medium" if pattern.get("confidence", 0.0) >= 0.4 else "low",
                "calibration_guidance": "trust_strategy" if pattern.get("confidence", 0.0) >= 0.7 else "use_normal_judgment" if pattern.get("confidence", 0.0) >= 0.4 else "be_cautious",
                "conflict_detected": len(pattern.get("strategy_counts", {})) > 1,
                "conflict_resolution": pattern.get("conflict_resolution"),
                "conflict_strategy_count": len(pattern.get("strategy_counts", {})),
                "decision_gate": "allow_strong_preference" if pattern.get("confidence", 0.0) >= 0.7 and pattern.get("preferred_strategy_reliability", 0.0) >= 0.8 else "allow_normal_preference" if pattern.get("confidence", 0.0) >= 0.4 else "limit_memory_influence",
                "cognitive_priority": "failure_avoidance" if pattern.get("recommendation") == "avoid_failed_strategy" else "reliable_strategy" if pattern.get("preferred_strategy_reliability", 0.0) >= 0.8 and pattern.get("confidence", 0.0) >= 0.7 else "recent_evidence" if pattern.get("recent_success_rate", 0.0) > pattern.get("success_rate", 0.0) else "weak_memory",
                "cognitive_decision": "avoid_strategy" if pattern.get("recommendation") == "avoid_failed_strategy" else "prefer_strategy" if pattern.get("preferred_strategy_reliability", 0.0) >= 0.8 and pattern.get("confidence", 0.0) >= 0.7 else "consider_strategy" if pattern.get("recommendation") == "prefer_successful_strategy" else "use_cautiously",
                "recommendation": pattern.get("recommendation")
            }

        if pattern:
            reliability = pattern.get("strategy_reliability", {})
            failing_strategies = {
                name: stats
                for name, stats in reliability.items()
                if stats.get("failure_rate", 0.0) >= 0.5
            }

            if failing_strategies:
                strategy, strategy_stats = max(
                    failing_strategies.items(),
                    key=lambda item: (
                        item[1].get("failure_rate", 0.0),
                        -item[1].get("success_rate", 0.0),
                        item[1].get("occurrences", 0),
                    ),
                )
                payload["failure_avoidance"] = {
                    "avoid": True,
                    "strategy": strategy,
                    "confidence": pattern.get("confidence", 0.0),
                    "failure_rate": strategy_stats.get("failure_rate", 0.0),
                }

        print("[PLANNER] Cognitive feedback:", payload)
        return "\nRELEVANT PAST EXECUTION FEEDBACK:\n" + json.dumps(payload, ensure_ascii=False)

    def _validated_plan(self, command, plan):
        """Apply command relevance validation to every locally generated plan."""
        if not isinstance(plan, dict):
            return plan

        tasks = plan.get("tasks")
        if not isinstance(tasks, list):
            return plan

        safe_tasks = [
            task for task in tasks
            if isinstance(task, dict)
        ]

        return {
            **plan,
            "tasks": self._validate_against_command(command, safe_tasks),
        }

    def plan(self, command):

        command = str(command).strip()

        if not command:
            return None

        # ========================================
        # MULTI-TASK FIRST
        # ========================================

        multi_plan = self._multi_task_plan(
            command
        )

        if multi_plan is not None:

            print(
                "[PLANNER] Multi-task plan:",
                multi_plan
            )

            return self._validated_plan(command, multi_plan)

        # ========================================
        # SIMPLE LOCAL COMMANDS
        # ========================================

        local_plan = self._local_plan(
            command
        )

        if local_plan is not None:

            print(
                "[PLANNER] Local plan:",
                local_plan
            )

            return self._validated_plan(command, local_plan)

        # ========================================
        # DIRECT BROWSER SEARCH
        # ========================================

        browser_plan = self._browser_search_plan(
            command
        )

        if browser_plan is not None:

            print(
                "[PLANNER] Direct browser plan:",
                browser_plan
            )

            return self._validated_plan(command, browser_plan)

        # ========================================
        # AI FALLBACK
        # ========================================

        cognitive_feedback = self._cognitive_feedback(command)

        prompt = f"""
You are FRIDAY's execution planner.

Convert ONLY the CURRENT USER REQUEST into
an executable JSON plan.

Return ONLY valid JSON.

Required format:

{{
    "tasks": [
        {{
            "intent": "intent_name",
            "parameters": {{}}
        }}
    ]
}}

Rules:

1. Use ONLY the current request.
2. Past execution feedback may be used only as guidance; never copy a previous request or invent details not present in the current request.
3. When feedback is marked successful, prefer the demonstrated approach when it matches the current request.
4. When feedback is marked partially_successful, use it cautiously and improve the approach when possible.
5. When feedback is marked failed_avoid_repeating, avoid repeating the failed approach unless the current request clearly requires it.
6. Use pattern confidence as evidence strength: low-confidence patterns are weak guidance, while high-confidence patterns should have greater influence on planning.
7. When failure avoidance is provided, avoid the specified strategy unless the current request clearly requires a different or corrective approach.
8. NEVER invent applications.
9. NEVER invent actions.
10. Preserve the order of actions.
11. Use "parameters", never "data".
12. For open_app use:
   {{"app": "spotify"}}
13. For google_search use:
   {{"query": "python tutorials"}}
14. For open_browser use:
   {{"browser": "chrome", "url": "..."}}
15. Return {{"tasks":[]}} if no executable action exists.
16. Return valid JSON only.
17. Do not return markdown.
18. Do not return explanations.

Supported intents:

open_app
open_browser
google_search
youtube_search
volume_up
volume_down
mute
unmute
brightness_up
brightness_down
battery
cpu
ram
disk
open_camera
close_camera
take_photo
take_screenshot
analyze_screen
remember
recall
add_habit
list_habits
habit_progress
delete_habit
complete_habit
daily_briefing
today_plan
daily_progress
add_reminder
list_reminders
remove_reminder
run_workflow
stop_workflow
resume_tasks
retry_task
workflow_status
list_workflows
show_workflow
delete_workflow

CURRENT USER REQUEST:

{command}

{cognitive_feedback}
"""

        try:

            print(
                "[PLANNER] Sending request to Ollama..."
            )

            response = ai.ask(
                prompt
            )

            if not response:

                print(
                    "[PLANNER] Empty AI response."
                )

                return None

            print(
                "[PLANNER] Raw response:",
                response
            )

            # ========================================
            # CLEAN MARKDOWN
            # ========================================

            response = response.strip()

            response = re.sub(
                r"^```(?:json)?\s*",
                "",
                response,
                flags=re.IGNORECASE
            )

            response = re.sub(
                r"\s*```$",
                "",
                response
            )

            # ========================================
            # FIND JSON
            # ========================================

            match = re.search(
                r"\{.*\}",
                response,
                re.DOTALL
            )

            if not match:

                print(
                    "[PLANNER] No JSON found."
                )

                return None

            json_text = match.group(
                0
            ).strip()

            # ========================================
            # PARSE
            # ========================================

            try:

                plan = json.loads(
                    json_text
                )

            except json.JSONDecodeError as e:

                print(
                    "[PLANNER] JSON error:",
                    repr(e)
                )

                return None

            # ========================================
            # NORMALIZE SINGLE TASK
            # ========================================

            if (
                isinstance(plan, dict)
                and "tasks" not in plan
                and "intent" in plan
            ):

                plan = {
                    "tasks": [
                        {
                            "intent": plan.get(
                                "intent"
                            ),
                            "parameters": plan.get(
                                "parameters",
                                {}
                            )
                        }
                    ]
                }

            if not isinstance(
                plan,
                dict
            ):

                return None

            tasks = plan.get(
                "tasks",
                []
            )

            if not isinstance(
                tasks,
                list
            ):

                return None

            # ========================================
            # VALIDATE TASKS
            # ========================================

            validated_tasks = []

            for task in tasks:

                if not isinstance(
                    task,
                    dict
                ):

                    continue

                intent = task.get(
                    "intent"
                )

                parameters = task.get(
                    "parameters",
                    {}
                )

                # ------------------------------------
                # Compatibility with old "data"
                # ------------------------------------

                if (
                    not parameters
                    and isinstance(
                        task.get("data"),
                        dict
                    )
                ):

                    parameters = task[
                        "data"
                    ]

                if not isinstance(
                    intent,
                    str
                ):

                    continue

                intent = intent.strip()

                if intent not in self.SUPPORTED_INTENTS:

                    print(
                        "[PLANNER] Rejected unsupported "
                        f"intent: {intent}"
                    )

                    continue

                if not isinstance(
                    parameters,
                    dict
                ):

                    parameters = {}

                # ------------------------------------
                # app_name → app
                # ------------------------------------

                if (
                    intent == "open_app"
                    and "app" not in parameters
                    and "app_name" in parameters
                ):

                    parameters["app"] = parameters.pop(
                        "app_name"
                    )

                validated_tasks.append(
                    {
                        "intent": intent,
                        "parameters": parameters
                    }
                )

            validated_tasks = (
                self._validate_against_command(
                    command,
                    validated_tasks
                )
            )

            final_plan = {
                "tasks": validated_tasks
            }

            print(
                "[PLANNER] Parsed plan:",
                final_plan
            )

            return final_plan

        except Exception as e:

            print(
                "[PLANNER] Error:",
                repr(e)
            )

            return None

    # ========================================
    # SIMPLE LOCAL COMMANDS
    # ========================================

    def _local_plan(
        self,
        command
    ):

        text = command.lower().strip()

        # ----------------------------------------
        # BATTERY
        # ----------------------------------------

        battery_phrases = [
            "battery",
            "what is my battery",
            "what's my battery",
            "whats my battery",
            "battery percentage",
            "battery status",
            "how much battery",
            "how much battery do i have",
            "how much battery do i have left",
            "how much battery is left",
        ]

        if any(
            phrase in text
            for phrase in battery_phrases
        ):

            return {
                "tasks": [
                    {
                        "intent": "battery",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # VOLUME UP
        # ----------------------------------------

        if self._is_volume_up(
            text
        ):

            return {
                "tasks": [
                    {
                        "intent": "volume_up",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # VOLUME DOWN
        # ----------------------------------------

        if self._is_volume_down(
            text
        ):

            return {
                "tasks": [
                    {
                        "intent": "volume_down",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # MUTE
        # ----------------------------------------

        if (
            text == "mute"
            or "mute the volume" in text
            or "mute volume" in text
        ):

            return {
                "tasks": [
                    {
                        "intent": "mute",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # UNMUTE
        # ----------------------------------------

        if (
            text == "unmute"
            or "unmute the volume" in text
            or "unmute volume" in text
        ):

            return {
                "tasks": [
                    {
                        "intent": "unmute",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # SCREENSHOT
        # ----------------------------------------

        if self._is_screenshot(
            text
        ):

            return {
                "tasks": [
                    {
                        "intent": "take_screenshot",
                        "parameters": {}
                    }
                ]
            }

        return None

    # ========================================
    # VOLUME UP DETECTION
    # ========================================

    def _is_volume_up(
        self,
        text
    ):

        phrases = [
            "volume up",
            "increase volume",
            "increase the volume",
            "turn up the volume",
            "turn the volume up",
            "make the volume louder",
            "make volume louder",
            "make it louder",
            "turn it up",
            "raise the volume",
            "raise volume",
            "volume louder",
            "louder",
        ]

        return any(
            phrase in text
            for phrase in phrases
        )

    # ========================================
    # VOLUME DOWN DETECTION
    # ========================================

    def _is_volume_down(
        self,
        text
    ):

        phrases = [
            "volume down",
            "decrease volume",
            "decrease the volume",
            "turn down the volume",
            "turn the volume down",
            "make the volume quieter",
            "make volume quieter",
            "make it quieter",
            "turn it down",
            "lower the volume",
            "lower volume",
            "volume quieter",
            "quieter",
        ]

        return any(
            phrase in text
            for phrase in phrases
        )

    # ========================================
    # SCREENSHOT DETECTION
    # ========================================

    def _is_screenshot(
        self,
        text
    ):

        phrases = [
            "take a screenshot",
            "take screenshot",
            "capture the screen",
            "capture screen",
            "capture my screen",
            "capture the display",
            "screenshot this",
            "take a screen capture",
            "screen capture",
        ]

        return any(
            phrase in text
            for phrase in phrases
        )

    # ========================================
    # MULTI-TASK PLANNER
    # ========================================

    def _multi_task_plan(
        self,
        command
    ):

        text = command.lower().strip()

        # ----------------------------------------
        # Must contain multiple actions.
        # ----------------------------------------

        if not any(
            separator in text
            for separator in [
                ",",
                " and ",
                " then ",
                " and then "
            ]
        ):

            return None

        # ========================================
        # NORMALIZE SEPARATORS
        # ========================================

        protected = text

        # ----------------------------------------
        # and then
        # ----------------------------------------

        protected = re.sub(
            r"\s+and then\s+",
            "|||",
            protected
        )

        # ----------------------------------------
        # then
        # ----------------------------------------

        protected = re.sub(
            r"\s+then\s+",
            "|||",
            protected
        )

        # ----------------------------------------
        # Commas before actions
        # ========================================

        protected = re.sub(
            r",\s*(?=(?:"
            r"open|"
            r"launch|"
            r"start|"
            r"close|"
            r"turn|"
            r"increase|"
            r"decrease|"
            r"raise|"
            r"lower|"
            r"make|"
            r"mute|"
            r"unmute|"
            r"search|"
            r"google|"
            r"play|"
            r"take|"
            r"capture|"
            r"set"
            r")\b)",
            "|||",
            protected
        )

        # ----------------------------------------
        # "and" before a new action
        #
        # Example:
        #
        # search Google for Python tutorials
        # and capture my screen
        # ----------------------------------------

        protected = re.sub(
            r"\s+and\s+(?=(?:"
            r"open|"
            r"launch|"
            r"start|"
            r"close|"
            r"turn|"
            r"increase|"
            r"decrease|"
            r"raise|"
            r"lower|"
            r"make|"
            r"mute|"
            r"unmute|"
            r"search|"
            r"google|"
            r"play|"
            r"take|"
            r"capture|"
            r"set"
            r")\b)",
            "|||",
            protected
        )

        # ========================================
        # SPLIT
        # ========================================

        parts = [
            part.strip()
            for part in protected.split(
                "|||"
            )
            if part.strip()
        ]

        if len(parts) < 2:

            return None

        tasks = []

        # ========================================
        # PARSE EACH TASK
        # ========================================

        for part in parts:

            # ====================================
            # OPEN CHROME + SEARCH
            # ====================================

            browser_plan = (
                self._browser_search_plan(
                    part
                )
            )

            if browser_plan is not None:

                tasks.extend(
                    browser_plan["tasks"]
                )

                continue

            # ====================================
            # OPEN / LAUNCH / START APP
            # ====================================

            open_match = re.fullmatch(
                r"(?:open|launch|start)\s+(.+)",
                part
            )

            if open_match:

                app = open_match.group(
                    1
                ).strip()

                app = self._clean_argument(
                    app
                )

                if (
                    app
                    and "search" not in app
                    and "volume" not in app
                    and "brightness" not in app
                ):

                    tasks.append(
                        {
                            "intent": "open_app",
                            "parameters": {
                                "app": app
                            }
                        }
                    )

                    continue

            # ====================================
            # GOOGLE SEARCH
            # ====================================

            google_match = re.fullmatch(
                r"(?:search\s+)?google"
                r"(?:\s+for)?\s+(.+)",
                part
            )

            if google_match:

                query = google_match.group(
                    1
                ).strip()

                query = self._clean_argument(
                    query
                )

                if query:

                    tasks.append(
                        {
                            "intent": "google_search",
                            "parameters": {
                                "query": query
                            }
                        }
                    )

                    continue

            # ====================================
            # EXPLICIT GOOGLE SEARCH
            # ====================================

            google_match = re.fullmatch(
                r"search\s+google\s+for\s+(.+)",
                part
            )

            if google_match:

                query = google_match.group(
                    1
                ).strip()

                query = self._clean_argument(
                    query
                )

                if query:

                    tasks.append(
                        {
                            "intent": "google_search",
                            "parameters": {
                                "query": query
                            }
                        }
                    )

                    continue

            # ====================================
            # YOUTUBE SEARCH
            # ====================================

            youtube_match = re.fullmatch(
                r"search\s+youtube\s+for\s+(.+)",
                part
            )

            if youtube_match:

                query = youtube_match.group(
                    1
                ).strip()

                query = self._clean_argument(
                    query
                )

                if query:

                    tasks.append(
                        {
                            "intent": "youtube_search",
                            "parameters": {
                                "query": query
                            }
                        }
                    )

                    continue

            # ====================================
            # VOLUME UP
            # ====================================

            if self._is_volume_up(
                part
            ):

                tasks.append(
                    {
                        "intent": "volume_up",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # VOLUME DOWN
            # ====================================

            if self._is_volume_down(
                part
            ):

                tasks.append(
                    {
                        "intent": "volume_down",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # MUTE
            # ====================================

            if (
                part == "mute"
                or "mute the volume" in part
                or "mute volume" in part
            ):

                tasks.append(
                    {
                        "intent": "mute",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # UNMUTE
            # ====================================

            if (
                part == "unmute"
                or "unmute the volume" in part
                or "unmute volume" in part
            ):

                tasks.append(
                    {
                        "intent": "unmute",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # BRIGHTNESS UP
            # ====================================

            if (
                "increase brightness" in part
                or "increase the brightness" in part
                or "turn up the brightness" in part
                or "turn the brightness up" in part
                or "make the brightness higher" in part
                or "make the screen brighter" in part
            ):

                tasks.append(
                    {
                        "intent": "brightness_up",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # BRIGHTNESS DOWN
            # ====================================

            if (
                "decrease brightness" in part
                or "decrease the brightness" in part
                or "turn down the brightness" in part
                or "turn the brightness down" in part
                or "make the brightness lower" in part
                or "make the screen darker" in part
            ):

                tasks.append(
                    {
                        "intent": "brightness_down",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # BATTERY
            # ====================================

            if (
                "battery" in part
                or "battery status" in part
                or "battery percentage" in part
            ):

                tasks.append(
                    {
                        "intent": "battery",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # SCREENSHOT
            # ====================================

            if self._is_screenshot(
                part
            ):

                tasks.append(
                    {
                        "intent": "take_screenshot",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # UNKNOWN PART
            # ====================================

            return None

        if not tasks:

            return None

        return {
            "tasks": tasks
        }

    # ========================================
    # CLEAN ARGUMENT
    # ========================================

    def _clean_argument(
        self,
        value
    ):

        value = str(
            value
        ).strip()

        value = value.rstrip(
            " ,."
        )

        return value.strip()

    # ========================================
    # DIRECT BROWSER SEARCH
    # ========================================

    def _browser_search_plan(
        self,
        command
    ):

        text = command.lower().strip()

        if "search" not in text:

            return None

        # ========================================
        # OPEN CHROME + SEARCH
        # ========================================

        match = re.search(
            r"(?:open|launch|start)\s+"
            r"(chrome|google chrome)"
            r"\s+and\s+search\s+"
            r"(?:for\s+)?(.+)$",
            text,
            re.IGNORECASE
        )

        if match:

            query = match.group(
                2
            ).strip()

            query = self._clean_argument(
                query
            )

            if not query:

                return None

            url = (
                "https://www.google.com/search?q="
                + quote_plus(query)
            )

            return {
                "tasks": [
                    {
                        "intent": "open_browser",
                        "parameters": {
                            "browser": "chrome",
                            "url": url
                        }
                    }
                ]
            }

        return None

    # ========================================
    # VALIDATION
    # ========================================

    def _validate_against_command(
        self,
        command,
        tasks
    ):

        text = command.lower()

        validated = []

        for task in tasks:

            intent = task.get(
                "intent"
            )

            params = task.get(
                "parameters",
                {}
            )

            # ----------------------------------------
            # OPEN APP
            # ----------------------------------------

            if intent == "open_app":

                app = str(
                    params.get(
                        "app",
                        ""
                    )
                ).lower().strip()

                if not app:

                    continue

                if app not in text:

                    print(
                        "[PLANNER] Rejected unrelated "
                        f"application: {app}"
                    )

                    continue

            # ----------------------------------------
            # OPEN BROWSER
            # ----------------------------------------

            if intent == "open_browser":

                browser_name = str(
                    params.get(
                        "browser",
                        ""
                    )
                ).lower().strip()

                if (
                    browser_name
                    and browser_name not in text
                    and not (
                        browser_name == "chrome"
                        and (
                            "search" in text
                            or "google" in text
                        )
                    )
                ):

                    print(
                        "[PLANNER] Rejected unrelated "
                        f"browser: {browser_name}"
                    )

                    continue

            # ----------------------------------------
            # GOOGLE SEARCH
            # ----------------------------------------

            if intent == "google_search":

                if (
                    "google" not in text
                    and "search" not in text
                ):

                    print(
                        "[PLANNER] Rejected unrelated "
                        "Google search."
                    )

                    continue

            # ----------------------------------------
            # YOUTUBE SEARCH
            # ----------------------------------------

            if intent == "youtube_search":

                if "youtube" not in text:

                    print(
                        "[PLANNER] Rejected unrelated "
                        "YouTube search."
                    )

                    continue

            validated.append(
                task
            )

        return validated


# ========================================
# GLOBAL PLANNER
# ========================================

planner = Planner()
