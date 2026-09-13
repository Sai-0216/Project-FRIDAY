"""
Project FRIDAY
Intent Dispatcher
"""

import webbrowser

from speech import speaker

from modules.volume import volume
from modules.brightness import brightness
from modules.system import system
from modules.camera import camera
from modules.screenshot import screenshot
from modules.browser import browser
from modules.apps import apps
from modules.files import files
from modules.memory import memory
from proactive.preference_memory import preference_memory
from proactive.memory_conflict import MemoryConflict
from modules.habits import HabitTracker
from modules.routine import routine
from modules.briefing import briefing
from modules.reminders import reminders
from modules.workflows import workflows
from modules.task_manager import task_manager
from decision_recall import decision_recall
from proactive.reasoning_quality import ReasoningQuality
from proactive.decision_quality import DecisionQuality
from proactive.reasoning_feedback import ReasoningFeedback
from proactive.self_correction import SelfCorrection
from proactive.reasoning_strategy import ReasoningStrategy


class IntentDispatcher:

    def execute(self, intent):

        try:
            return self._execute(intent)

        except Exception as e:

            print(
                "[Dispatcher] Intent execution error:",
                repr(e)
            )

            return (
                "Sorry Sir, I couldn't complete "
                "that action right now."
            )

    # ========================================
    # INTERNAL INTENT EXECUTION
    # ========================================

    def _execute(self, intent):

        name = intent.get(
            "intent",
            "unknown"
        )

        params = intent.get(
            "parameters",
            {}
        )

        if not isinstance(
            params,
            dict
        ):

            params = {}

        match name:

            # ========================================
            # WORKFLOWS
            # ========================================

            case "run_workflow":

                workflow_name = params.get(
                    "workflow",
                    ""
                )

                workflow_name = str(
                    workflow_name
                ).strip()

                if not workflow_name:

                    return (
                        "Please provide a workflow name, Sir."
                    )

                return workflows.run(
                    workflow_name
                )

            case "create_workflow":

                workflow_name = params.get(
                    "workflow",
                    ""
                )

                description = params.get(
                    "description",
                    ""
                )

                workflow_name = str(
                    workflow_name
                ).strip()

                description = str(
                    description
                ).strip()

                if not workflow_name:

                    return (
                        "Please provide a workflow name, Sir."
                    )

                if not description:

                    return (
                        f"I know the workflow name "
                        f"'{workflow_name}', Sir, "
                        "but I need to know what you "
                        "want it to do."
                    )

                return workflows.create_from_description(
                    workflow_name,
                    description
                )

            case "add_to_workflow":

                workflow_name = params.get(
                    "workflow",
                    ""
                )

                description = params.get(
                    "description",
                    ""
                )

                workflow_name = str(
                    workflow_name
                ).strip()

                description = str(
                    description
                ).strip()

                if not workflow_name:

                    return (
                        "Please provide a workflow name, Sir."
                    )

                if not description:

                    return (
                        "Please tell me what you want "
                        "to add to the workflow, Sir."
                    )

                print(
                    "Dispatcher: Adding to workflow:",
                    workflow_name
                )

                print(
                    "Dispatcher: Addition:",
                    description
                )

                return workflows.add_to_workflow(
                    workflow_name,
                    description
                )

            case "remove_from_workflow":

                workflow_name = params.get(
                    "workflow",
                    ""
                )

                target = params.get(
                    "target",
                    ""
                )

                workflow_name = str(
                    workflow_name
                ).strip()

                target = str(
                    target
                ).strip()

                if not workflow_name:

                    return (
                        "Please provide a workflow name, Sir."
                    )

                if not target:

                    return (
                        "Please tell me what you want "
                        "to remove from the workflow, Sir."
                    )

                print(
                    "Dispatcher: Removing from workflow:",
                    workflow_name
                )

                print(
                    "Dispatcher: Removal target:",
                    target
                )

                return workflows.remove_from_workflow(
                    workflow_name,
                    target
                )

            case "edit_workflow":

                workflow_name = params.get(
                    "workflow",
                    ""
                )

                description = params.get(
                    "description",
                    ""
                )

                workflow_name = str(
                    workflow_name
                ).strip()

                description = str(
                    description
                ).strip()

                if not workflow_name:

                    return (
                        "Please provide a workflow name, Sir."
                    )

                if not description:

                    return (
                        "Please tell me how you want "
                        "to edit the workflow, Sir."
                    )

                print(
                    "Dispatcher: Editing workflow:",
                    workflow_name
                )

                print(
                    "Dispatcher: Edit:",
                    description
                )

                return workflows.edit_workflow(
                    workflow_name,
                    description
                )

            case "resume_tasks":

                tasks = task_manager.list_tasks(task_manager.INTERRUPTED)

                if not tasks:

                    return "There are no interrupted tasks to resume, Sir."

                results = []

                for task in tasks:

                    task_id = task.get("task_id")

                    if not task_id:
                        continue

                    result = workflows.run_task(task_id)
                    results.append(result)

                if not results:

                    return "I found interrupted tasks, but none could be resumed, Sir."

                return "\n".join(str(result) for result in results if result)

            case "retry_task":

                tasks = task_manager.list_tasks(task_manager.FAILED)

                if not tasks:

                    return "There are no failed tasks to retry, Sir."

                results = []

                for task in tasks:

                    task_id = task.get("task_id")

                    if not task_id:
                        continue

                    result = workflows.auto_retry_task(task_id)
                    if result:
                        results.append("Retry prepared successfully, Sir.")
                    else:
                        results.append("I could not retry that task, Sir. The maximum retry limit has been reached.")

                if not results:

                    return "I found failed tasks, but none could be retried, Sir."

                return "\n".join(str(result) for result in results if result)

            case "verify_decision":

                decision = decision_recall.get_decision("why did you choose that")

                if not isinstance(decision, dict):
                    return "I do not have a recent decision available to verify, Sir."

                action = decision.get("chosen_option") or decision.get("recommendation")
                expected = decision.get("expected") or decision.get("intended_outcome")
                actual = decision.get("actual") or decision.get("outcome")

                if actual is None:
                    return "I found the recent decision, but no actual outcome has been recorded yet, Sir. I cannot verify its quality without an outcome."

                assessment = DecisionQuality.from_outcome(
                    action,
                    expected,
                    actual
                )

                if assessment is None:
                    return "I could not verify that decision, Sir."

                data = assessment.to_dict()
                level = data.get("level", "UNKNOWN")
                score = data.get("score", 0.0)

                return f"Decision quality is {level} with a score of {score:.2f}, Sir."

            case "correct_reasoning":

                decision = decision_recall.get_decision("why did you choose that")

                if not isinstance(decision, dict):
                    return "I do not have a recent decision available to correct, Sir."

                reasoning = {
                    "action": decision.get("chosen_option") or decision.get("recommendation"),
                    "reason": decision.get("explanation") or decision.get("recommendation")
                }

                assessment = ReasoningQuality.from_reasoning(reasoning)

                if assessment is None:
                    return "I could not assess the reasoning, Sir."

                data = assessment.to_dict()
                level = data.get("level", "UNKNOWN")
                score = data.get("score", 0.0)

                if level != "LOW":
                    return f"No reasoning correction is required. The current reasoning quality is {level} with a score of {score:.2f}, Sir."

                feedback = ReasoningFeedback.from_assessments(reasoning=data)

                if feedback is None or feedback.signal != ReasoningFeedback.NEGATIVE:
                    return "The reasoning does not meet the threshold for correction, Sir."

                target_strategy = ReasoningStrategy.VERIFY_FIRST
                correction = SelfCorrection.create(
                    SelfCorrection.CHANGE_STRATEGY,
                    target=target_strategy,
                    reason=feedback.reason,
                    confidence="HIGH",
                    evidence=feedback.evidence
                )

                if correction is None or SelfCorrection.safety_validate(correction) != "SAFE":
                    return "The proposed reasoning correction did not pass the safety checks, Sir."

                preview = SelfCorrection.preview_strategy_correction(
                    correction,
                    ReasoningStrategy.DIRECT,
                    list(ReasoningStrategy.TYPES)
                )

                if not preview:
                    return "I could not safely prepare a reasoning correction, Sir."

                SelfCorrectionStore().record(correction)

                return f"My reasoning needs correction. I propose switching from {preview["current_strategy"]} to {preview["proposed_strategy"]}, with {preview["confidence"]} confidence, Sir."

            case "check_reasoning":

                decision = decision_recall.get_decision("why did you choose that")

                if not isinstance(decision, dict):
                    return "I do not have a recent decision available to assess, Sir."

                reasoning = {
                    "action": decision.get("chosen_option"),
                    "reason": decision.get("explanation") or decision.get("recommendation")
                }

                assessment = ReasoningQuality.from_reasoning(reasoning)

                if assessment is None:
                    return "I could not assess the reasoning, Sir."

                data = assessment.to_dict()
                level = data.get("level", "UNKNOWN")
                score = data.get("score", 0.0)

                return f"My reasoning quality is {level} with a score of {score:.2f}, Sir."

            case "stop_workflow":

                return workflows.cancel()

            case "workflow_status":

                return workflows.status()

            case "list_workflows":

                return workflows.list_workflows()

            case "show_workflow":

                workflow_name = params.get(
                    "workflow",
                    ""
                )

                workflow_name = str(
                    workflow_name
                ).strip()

                if not workflow_name:

                    return (
                        "Please provide a workflow name, Sir."
                    )

                return workflows.show_workflow(
                    workflow_name
                )

            case "delete_workflow":

                workflow_name = params.get(
                    "workflow",
                    ""
                )

                workflow_name = str(
                    workflow_name
                ).strip()

                if not workflow_name:

                    return (
                        "Please provide a workflow name, Sir."
                    )

                return workflows.delete_workflow(
                    workflow_name
                )

            # ========================================
            # VOLUME
            # ========================================

            case "volume_up":

                return volume.volume_up()

            case "volume_down":

                return volume.volume_down()

            case "mute":

                return volume.mute()

            case "unmute":

                return volume.unmute()

            # ========================================
            # BRIGHTNESS
            # ========================================

            case "brightness_up":

                return brightness.brightness_up()

            case "brightness_down":

                return brightness.brightness_down()

            # ========================================
            # SYSTEM
            # ========================================

            case "battery":

                return system.battery()

            case "cpu":

                return system.cpu()

            case "ram":

                return system.ram()

            case "disk":

                return system.disk()

            # ========================================
            # WINDOWS SYSTEM CONTROL
            # ========================================

            case "task_manager":

                return system.task_manager()

            case "settings":

                return system.settings()

            case "lock_computer":

                return system.lock()

            case "sleep":

                return system.sleep()

            case "restart":

                return system.restart()

            case "shutdown":

                return system.shutdown()

            # ========================================
            # CAMERA
            # ========================================

            case "open_camera":

                return camera.open_camera()

            case "close_camera":

                return camera.close_camera()

            case "take_photo":

                return camera.take_photo()

            # ========================================
            # SCREENSHOT / VISION
            # ========================================

            case "take_screenshot":

                return screenshot.take()

            case "analyze_screen":

                return screenshot.analyze()

            # ========================================
            # BROWSER
            # ========================================

            case "open_browser":

                browser_name = params.get(
                    "browser",
                    "chrome"
                )

                url = params.get(
                    "url",
                    ""
                )

                browser_name = str(
                    browser_name
                ).strip()

                url = str(
                    url
                ).strip()

                if not url:

                    return (
                        "Please provide a URL, Sir."
                    )

                try:

                    webbrowser.open(
                        url
                    )

                    if browser_name:

                        return (
                            f"Opening {browser_name} "
                            "and searching as requested."
                        )

                    return (
                        "Opening the browser "
                        "and searching as requested."
                    )

                except Exception as e:

                    print(
                        "[Dispatcher] Browser error:",
                        repr(e)
                    )

                    return (
                        "Sorry Sir, I couldn't open "
                        "the browser."
                    )

            case "google_search":

                query = params.get(
                    "query",
                    ""
                )

                return browser.google_search(
                    query
                )

            case "youtube_search":

                query = params.get(
                    "query",
                    ""
                )

                return browser.youtube_search(
                    query
                )

            case "youtube_play":

                query = params.get(
                    "query",
                    ""
                )

                return browser.youtube_play(
                    query
                )

            # ========================================
            # APPLICATIONS
            # ========================================

            case "open_app":

                app_name = params.get(
                    "app",
                    params.get(
                        "name",
                        ""
                    )
                )

                app_name = str(
                    app_name
                ).strip()

                if not app_name:

                    return (
                        "Please tell me which application "
                        "you want me to open, Sir."
                    )

                return apps.open_app(
                    app_name
                )

            # ========================================
            # CLOSE APPLICATION
            # ========================================

            case "close_app":

                app_name = params.get(
                    "app",
                    params.get(
                        "name",
                        ""
                    )
                )

                app_name = str(
                    app_name
                ).strip()

                if not app_name:

                    return (
                        "Please tell me which application "
                        "you want me to close, Sir."
                    )

                return apps.close_app(
                    app_name
                )

            # ========================================
            # FILE & FOLDER CONTROL
            # ========================================

            case "open_folder":

                location = params.get(
                    "location",
                    ""
                )

                location = str(
                    location
                ).strip()

                if not location:

                    return (
                        "Please tell me which folder "
                        "you want me to open, Sir."
                    )

                return files.open_folder(
                    location
                )

            case "create_folder":

                name = params.get(
                    "name",
                    ""
                )

                location = params.get(
                    "location",
                    "desktop"
                )

                name = str(
                    name
                ).strip()

                location = str(
                    location
                ).strip()

                if not name:

                    return (
                        "Please tell me the folder "
                        "name, Sir."
                    )

                return files.create_folder(
                    name,
                    location
                )

            case "create_file":

                name = params.get(
                    "name",
                    ""
                )

                location = params.get(
                    "location",
                    "desktop"
                )

                name = str(
                    name
                ).strip()

                location = str(
                    location
                ).strip()

                if not name:

                    return (
                        "Please tell me the file "
                        "name, Sir."
                    )

                return files.create_file(
                    name,
                    location
                )

            case "open_file":

                path = params.get(
                    "path",
                    ""
                )

                path = str(
                    path
                ).strip()

                if not path:

                    return (
                        "Please tell me which file "
                        "you want me to open, Sir."
                    )

                return files.open_file(
                    path
                )

            # ========================================
            # HABITS
            # ========================================

            case "add_habit":

                return HabitTracker().add(
                    params.get(
                        "habit",
                        ""
                    )
                )

            case "list_habits":

                return HabitTracker().list_today()

            case "habit_progress":

                return HabitTracker().progress(
                    params.get(
                        "habit",
                        ""
                    )
                )

            case "delete_habit":

                return HabitTracker().delete(
                    params.get(
                        "habit",
                        ""
                    )
                )

            case "complete_habit":

                return HabitTracker().complete(
                    params.get(
                        "habit",
                        ""
                    )
                )

            # ========================================
            # MEMORY
            # ========================================

            case "remember":

                text = params.get(
                    "text",
                    ""
                )

                text = str(
                    text
                ).strip()

                if not text:

                    return (
                        "Please tell me what you "
                        "want me to remember."
                    )

                preference_prefixes = ("i prefer ", "i like ", "i love ", "i dislike ", "i don\'t like ", "my favorite ")
                lowered_text = text.lower()
                if lowered_text.startswith(preference_prefixes):
                    incoming={"timestamp":__import__("datetime").datetime.now().isoformat(),"preference":text,"category":"explicit_preference","confidence":"HIGH"}; existing=next((r for r in reversed(preference_memory.recent(500)) if r.get("category")=="explicit_preference"),None); resolution=MemoryConflict.resolve(existing,incoming) if existing and MemoryConflict.detect_preference_conflict(existing,incoming) else "incoming"; if_existing_safe=MemoryConflict.is_safe_resolution(existing,incoming,resolution) if existing and MemoryConflict.detect_preference_conflict(existing,incoming) else True; preference_memory.replace(existing.get("preference"), text, category="explicit_preference", confidence="HIGH") if existing and if_existing_safe and resolution=="incoming" else preference_memory.record(text, category="explicit_preference", confidence="HIGH") if not existing else None

                if " is " in text:

                    key, value = text.split(
                        " is ",
                        1
                    )

                    key = key.strip()

                    value = value.strip()

                    if key and value:

                        memory.remember(
                            key,
                            value
                        )

                        return (
                            f"I'll remember that "
                            f"{key} is {value}."
                        )

                return (
                    "Please tell me what you "
                    "want me to remember."
                )

            case "recall":

                key = params.get(
                    "text",
                    ""
                )

                key = str(
                    key
                ).strip().lower()

                if not key:

                    return (
                        "Please tell me what "
                        "you want me to recall."
                    )

                value = memory.recall(
                    key
                )

                if value:

                    return (
                        f"{key} is {value}."
                    )

                return (
                    f"I don't remember your {key}."
                )

            # ========================================
            # ROUTINE
            # ========================================

            case "add_routine":

                period = params.get(
                    "period",
                    ""
                )

                task = params.get(
                    "task",
                    ""
                )

                return routine.add(
                    period,
                    task
                )

            case "remove_routine":

                period = params.get(
                    "period",
                    ""
                )

                task = params.get(
                    "task",
                    ""
                )

                return routine.remove(
                    period,
                    task
                )

            case "show_routine":

                period = params.get(
                    "period",
                    ""
                )

                return routine.get(
                    period
                )

            case "show_full_routine":

                return routine.full_routine()

            # ========================================
            # DAILY BRIEFING
            # ========================================

            case "daily_briefing":

                return briefing.get()

            case "today_plan":

                return briefing.today_plan()

            case "daily_progress":

                return briefing.progress()

            # ========================================
            # REMINDERS
            # ========================================

            case "add_reminder":

                return reminders.add(
                    params.get(
                        "text",
                        ""
                    ),
                    params.get(
                        "time",
                        ""
                    )
                )

            case "add_weekly_reminder":

                return reminders.add_weekly(
                    params.get(
                        "text",
                        ""
                    ),
                    params.get(
                        "time",
                        ""
                    ),
                    params.get(
                        "weekday",
                        ""
                    )
                )

            case "add_relative_reminder":

                return reminders.add_relative(
                    params.get(
                        "text",
                        ""
                    ),
                    params.get(
                        "amount",
                        ""
                    ),
                    params.get(
                        "unit",
                        ""
                    )
                )

            case "list_reminders":

                return reminders.list_all()

            case "remove_reminder":

                return reminders.remove(
                    params.get(
                        "id"
                    )
                )

            case "remove_reminder_by_match":

                return reminders.remove_by_match(
                    params.get(
                        "text",
                        ""
                    ),
                    params.get(
                        "weekday"
                    )
                )

            # ========================================
            # UNKNOWN
            # ========================================

            case "unknown":

                return (
                    "Sorry Sir, "
                    "I couldn't understand."
                )

            # ========================================
            # FALLBACK
            # ========================================

            case _:

                return (
                    f"I don't know how to "
                    f"execute '{name}'."
                )

# ========================================
# GLOBAL DISPATCHER
# ========================================

dispatcher = IntentDispatcher()