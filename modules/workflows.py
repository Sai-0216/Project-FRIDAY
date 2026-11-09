"""
Project FRIDAY
Persistent Workflow Engine
"""

import json
import os
import copy
import webbrowser
import threading
import time

from urllib.parse import urlparse

from modules.apps import apps
from modules.automation import automation
from modules.workflow_planner import workflow_planner
from modules.task_manager import task_manager
from security.authorization import authorize_workflow_action


class WorkflowManager:

    # ========================================
    # RETRY POLICY
    # ========================================

    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1.0

    TRANSIENT_FAILURES = {
        "timeout",
        "temporarily unavailable",
        "connection error",
        "connection failed",
        "connection reset",
        "busy",
        "not ready",
        "temporary",
        "timed out",
        "failed to open",
        "couldn't open",
    }

    PERMANENT_FAILURES = {
        "invalid action",
        "invalid action format",
        "missing application name",
        "missing url",
        "invalid url",
        "missing wait duration",
        "missing key",
        "missing hotkey",
        "missing text",
        "wait duration cannot be negative",
        "unknown workflow action",
        "workflow execution failed.",
    }

    # ========================================
    # INITIALIZATION
    # ========================================

    def __init__(self):

        # ========================================
        # PATHS
        # ========================================

        self.data_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),
            "data"
        )

        self.workflow_file = os.path.join(
            self.data_dir,
            "workflows.json"
        )

        os.makedirs(
            self.data_dir,
            exist_ok=True
        )

        # ========================================
        # WORKFLOW STATE
        # ========================================

        self.workflow_running = False

        self.current_workflow = None

        self.current_task_id = None

        self.stop_event = threading.Event()

        self.workflow_thread = None

        self.state_lock = threading.Lock()

        self.last_failure_reason = None
        self.dependency_recovery_callback = None

        # Internal capability: only an approved run() launch receives this.
        self._execution_capability = object()

        # ========================================
        # DEFAULT WORKFLOWS
        # ========================================

        self.default_workflows = {

            "study": [
                ["open_app", "vscode"],
                ["wait", 2],
                ["open_app", "chrome"],
                ["wait", 2],
                [
                    "open_url",
                    "https://docs.python.org/3/"
                ],
            ],

            "coding": [
                ["open_app", "vscode"],
                ["wait", 2],
                ["open_app", "chrome"],
                ["wait", 2],
                [
                    "open_url",
                    "https://github.com/"
                ],
            ],

            "work": [
                ["open_app", "vscode"],
                ["wait", 2],
                ["open_app", "chrome"],
            ]
        }

        # ========================================
        # LOAD WORKFLOWS
        # ========================================

        self.workflows = self.load_workflows()

    # ========================================
    # LOAD WORKFLOWS
    # ========================================

    def load_workflows(self):

        if not os.path.exists(
            self.workflow_file
        ):

            print(
                "Workflow file not found."
            )

            print(
                "Creating default workflows..."
            )

            workflows = {
                name: [
                    list(action)
                    for action in actions
                ]
                for name, actions
                in self.default_workflows.items()
            }

            self.save_workflows(
                workflows
            )

            return workflows

        try:

            with open(
                self.workflow_file,
                "r",
                encoding="utf-8"
            ) as file:

                workflows = json.load(
                    file
                )

            if not isinstance(
                workflows,
                dict
            ):

                raise ValueError(
                    "Workflow file must contain an object."
                )

            print(
                "Workflows loaded from:",
                self.workflow_file
            )

            return workflows

        except (
            json.JSONDecodeError,
            OSError,
            ValueError
        ) as e:

            print(
                "Workflow load error:",
                repr(e)
            )

            print(
                "Restoring default workflows..."
            )

            workflows = {
                name: [
                    list(action)
                    for action in actions
                ]
                for name, actions
                in self.default_workflows.items()
            }

            self.save_workflows(
                workflows
            )

            return workflows

    # ========================================
    # SAVE WORKFLOWS
    # ========================================

    def save_workflows(
        self,
        workflows=None
    ):

        if workflows is None:

            workflows = self.workflows

        try:

            with open(
                self.workflow_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    workflows,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            print(
                "Workflows saved to:",
                self.workflow_file
            )

            return True

        except OSError as e:

            print(
                "Workflow save error:",
                repr(e)
            )

            return False

    # ========================================
    # CREATE WORKFLOW
    # ========================================

    def create_workflow(
        self,
        name,
        actions=None
    ):

        name = str(
            name
        ).lower().strip()

        name = "_".join(
            name.split()
        )

        if not name:

            return (
                "Please provide a workflow name, Sir."
            )

        with self.state_lock:

            if self.workflow_running:

                return (
                    "Please stop the running "
                    "workflow first, Sir."
                )

            if name in self.workflows:

                return (
                    f"The {name} workflow "
                    f"already exists, Sir."
                )

            if actions is None:

                actions = []

            if not isinstance(
                actions,
                list
            ):

                return (
                    "Workflow actions must be "
                    "provided as a list, Sir."
                )

            self.workflows[name] = actions

            saved = self.save_workflows()

            if not saved:

                self.workflows.pop(
                    name,
                    None
                )

                return (
                    f"Workflow '{name}' could not "
                    f"be saved, Sir."
                )

        if not actions:

            return (
                f"Workflow '{name}' created, Sir. "
                f"It is currently empty."
            )

        return (
            f"Workflow '{name}' created, Sir."
        )

    # ========================================
    # ADD WORKFLOW
    # ========================================

    def add_workflow(
        self,
        name,
        actions
    ):

        return self.create_workflow(
            name,
            actions
        )

    # ========================================
    # CREATE FROM NATURAL LANGUAGE
    # ========================================

    def create_from_description(
        self,
        name,
        description
    ):

        name = str(
            name
        ).lower().strip()

        name = "_".join(
            name.split()
        )

        description = str(
            description
        ).strip()

        # ----------------------------------------
        # Validate name
        # ----------------------------------------

        if not name:

            return (
                "Please provide a workflow name, Sir."
            )

        # ----------------------------------------
        # Validate description
        # ----------------------------------------

        if not description:

            return (
                f"Please tell me what the "
                f"{name} workflow should do, Sir."
            )

        # ----------------------------------------
        # Check running workflow
        # ----------------------------------------

        with self.state_lock:

            if self.workflow_running:

                return (
                    "Please stop the running "
                    "workflow first, Sir."
                )

        # ========================================
        # ASK WORKFLOW PLANNER
        # ========================================

        print(
            "Workflow Manager: "
            "Planning workflow..."
        )

        plan = workflow_planner.plan(
            description
        )

        # ----------------------------------------
        # Validate planner response
        # ----------------------------------------

        if not isinstance(
            plan,
            dict
        ):

            return (
                "The workflow planner returned "
                "invalid data, Sir."
            )

        if not plan.get(
            "success",
            False
        ):

            return plan.get(
                "message",
                "I couldn't create the workflow, Sir."
            )

        actions = plan.get(
            "actions",
            []
        )

        if not isinstance(
            actions,
            list
        ):

            return (
                "The workflow planner returned "
                "invalid actions, Sir."
            )

        if not actions:

            return (
                f"I couldn't determine any actions "
                f"for the {name} workflow, Sir."
            )

        # ========================================
        # CREATE OR REPLACE WORKFLOW
        # ========================================

        with self.state_lock:

            workflow_already_exists = (
                name in self.workflows
            )

            old_actions = None

            if workflow_already_exists:

                old_actions = [
                    list(action)
                    if isinstance(
                        action,
                        (list, tuple)
                    )
                    else action
                    for action in self.workflows[name]
                ]

                print(
                    f"Workflow '{name}' already exists."
                )

                print(
                    "Replacing existing actions..."
                )

            # ------------------------------------
            # Replace existing workflow or create
            # a new one.
            # ------------------------------------

            self.workflows[name] = [
                list(action)
                if isinstance(
                    action,
                    (list, tuple)
                )
                else action
                for action in actions
            ]

            saved = self.save_workflows()

            # ------------------------------------
            # Rollback if save fails
            # ------------------------------------

            if not saved:

                if workflow_already_exists:

                    self.workflows[name] = old_actions

                else:

                    self.workflows.pop(
                        name,
                        None
                    )

                return (
                    f"Workflow '{name}' could not "
                    f"be saved, Sir."
                )

        # ========================================
        # SHOW GENERATED ACTIONS
        # ========================================

        print(
            "Workflow created/replaced:"
        )

        for index, action in enumerate(
            actions,
            start=1
        ):

            print(
                f"  {index}. {action}"
            )

        # ========================================
        # RESPONSE
        # ========================================

        if workflow_already_exists:

            return (
                f"Workflow '{name}' updated with "
                f"{len(actions)} actions, Sir."
            )

        return (
            f"Workflow '{name}' created with "
            f"{len(actions)} actions, Sir."
        )

    # ========================================
    # ADD ACTION TO EXISTING WORKFLOW
    # ========================================

    def add_to_workflow(
        self,
        name,
        description
    ):

        name = str(
            name
        ).lower().strip()

        name = "_".join(
            name.split()
        )

        description = str(
            description
        ).strip()

        if not name:

            return (
                "Please provide a workflow name, Sir."
            )

        if not description:

            return (
                "Please tell me what you want "
                "to add to the workflow, Sir."
            )

        with self.state_lock:

            if self.workflow_running:

                return (
                    "Please stop the running "
                    "workflow first, Sir."
                )

            if name not in self.workflows:

                return (
                    f"I couldn't find the "
                    f"{name} workflow, Sir."
                )

        # ----------------------------------------
        # IMPORTANT:
        # Use plan_addition()
        # ----------------------------------------

        print(
            "Workflow Manager: "
            "Planning additional actions..."
        )

        plan = workflow_planner.plan_addition(
            description
        )

        if not isinstance(
            plan,
            dict
        ):

            return (
                "The workflow planner returned "
                "invalid data, Sir."
            )

        if not plan.get(
            "success",
            False
        ):

            return plan.get(
                "message",
                "I couldn't determine what to add, Sir."
            )

        new_actions = plan.get(
            "actions",
            []
        )

        if not isinstance(
            new_actions,
            list
        ):

            return (
                "The workflow planner returned "
                "invalid actions, Sir."
            )

        if not new_actions:

            return (
                "I couldn't determine any actions "
                "to add, Sir."
            )

        # ========================================
        # ADD ACTIONS
        # ========================================

        with self.state_lock:

            if name not in self.workflows:

                return (
                    f"I couldn't find the "
                    f"{name} workflow, Sir."
                )

            existing_actions = self.workflows[name]

            if not isinstance(
                existing_actions,
                list
            ):

                return (
                    f"The {name} workflow contains "
                    "invalid actions, Sir."
                )

            added_actions = []

            for action in new_actions:

                if action not in existing_actions:

                    existing_actions.append(
                        action
                    )

                    added_actions.append(
                        action
                    )

            if not added_actions:

                return (
                    f"Those actions are already "
                    f"present in the {name} workflow, Sir."
                )

            saved = self.save_workflows()

            if not saved:

                for action in reversed(
                    added_actions
                ):

                    if action in existing_actions:

                        existing_actions.remove(
                            action
                        )

                return (
                    f"I couldn't save the changes "
                    f"to the {name} workflow, Sir."
                )

        print(
            "Workflow actions added:"
        )

        for index, action in enumerate(
            added_actions,
            start=1
        ):

            print(
                f"  {index}. {action}"
            )

        return (
            f"Added {len(added_actions)} "
            f"action(s) to the {name} workflow, Sir."
        )

    # ========================================
    # NORMALIZE WORKFLOW TARGET
    # ========================================

    def normalize_target(self, value):

        value = str(
            value
        ).lower().strip()

        value = " ".join(
            value.replace("_", " ").split()
        )

        aliases = {
            "vs code": "vscode",
            "visual studio code": "vscode",
            "google chrome": "chrome",
            "chrome browser": "chrome",
            "github website": "github",
            "github site": "github",
            "microsoft edge": "edge",
            "edge browser": "edge",
            "windows terminal": "terminal",
        }

        return aliases.get(
            value,
            value
        )


    # ========================================
    # REMOVE ACTION FROM EXISTING WORKFLOW
    # ========================================

    def remove_from_workflow(
        self,
        name,
        target
    ):

        name = str(
            name
        ).lower().strip()

        name = "_".join(
            name.split()
        )

        target = str(
            target
        ).lower().strip()

        if not name:

            return (
                "Please provide a workflow name, Sir."
            )

        if not target:

            return (
                "Please tell me what you want "
                "to remove, Sir."
            )

        with self.state_lock:

            if self.workflow_running:

                return (
                    "Please stop the running "
                    "workflow first, Sir."
                )

            if name not in self.workflows:

                return (
                    f"I couldn't find the "
                    f"{name} workflow, Sir."
                )

            actions = self.workflows[name]

            if not isinstance(
                actions,
                list
            ):

                return (
                    f"The {name} workflow contains "
                    "invalid actions, Sir."
                )

            if not actions:

                return (
                    f"The {name} workflow is already empty, Sir."
                )

            target_normalized = self.normalize_target(
                target
            )

            matching_indexes = []

            for index, action in enumerate(
                actions
            ):

                if not isinstance(
                    action,
                    (list, tuple)
                ):

                    continue

                if not action:

                    continue

                action_type = str(
                    action[0]
                ).lower().strip()

                parameters = [
                    self.normalize_target(value)
                    for value in action[1:]
                ]

                normalized_action_type = self.normalize_target(
                    action_type
                )

                action_text = " ".join(
                    [normalized_action_type] + parameters
                )

                readable_text = action_text

                if (
                    target_normalized == normalized_action_type
                    or
                    target_normalized in action_text
                ):

                    matching_indexes.append(
                        index
                    )

            if not matching_indexes:

                return (
                    f"I couldn't find '{target}' "
                    f"in the {name} workflow, Sir."
                )

            remove_index = matching_indexes[-1]

            removed_action = actions.pop(
                remove_index
            )

            removed_wait = None

            if remove_index > 0:

                previous_index = (
                    remove_index - 1
                )

                if previous_index < len(
                    actions
                ):

                    previous_action = actions[
                        previous_index
                    ]

                    if (
                        isinstance(
                            previous_action,
                            (list, tuple)
                        )
                        and
                        len(previous_action) >= 2
                        and
                        previous_action[0] == "wait"
                    ):

                        removed_wait = actions.pop(
                            previous_index
                        )

                        print(
                            "Removed associated wait action:",
                            removed_wait
                        )

            saved = self.save_workflows()

            if not saved:

                if removed_wait is not None:

                    actions.insert(
                        remove_index - 1,
                        removed_wait
                    )

                actions.insert(
                    remove_index,
                    removed_action
                )

                return (
                    f"I couldn't save the changes "
                    f"to the {name} workflow, Sir."
                )

        print(
            "Workflow action removed:",
            removed_action
        )

        return (
            f"Removed {target} from the "
            f"{name} workflow, Sir."
        )

    # ========================================
    # EDIT EXISTING WORKFLOW
    # ========================================

    def edit_workflow(
        self,
        name,
        description
    ):

        name = str(
            name
        ).lower().strip()

        name = "_".join(
            name.split()
        )

        description = str(
            description
        ).strip()

        # ----------------------------------------
        # Validate
        # ----------------------------------------

        if not name:

            return (
                "Please provide a workflow name, Sir."
            )

        if not description:

            return (
                "Please tell me how you want "
                "to edit the workflow, Sir."
            )

        # ----------------------------------------
        # Check workflow
        # ----------------------------------------

        with self.state_lock:

            if self.workflow_running:

                return (
                    "Please stop the running "
                    "workflow first, Sir."
                )

            if name not in self.workflows:

                return (
                    f"I couldn't find the "
                    f"{name} workflow, Sir."
                )

            original_actions = [
                list(action)
                if isinstance(
                    action,
                    (list, tuple)
                )
                else action
                for action in self.workflows[name]
            ]

        # ========================================
        # ASK WORKFLOW PLANNER
        # ========================================

        print(
            "Workflow Manager: "
            "Planning workflow edit..."
        )

        plan = workflow_planner.plan_edit(
            description
        )

        if not isinstance(
            plan,
            dict
        ):

            return (
                "The workflow planner returned "
                "invalid edit data, Sir."
            )

        if not plan.get(
            "success",
            False
        ):

            return plan.get(
                "message",
                "I couldn't determine the workflow changes, Sir."
            )

        remove_targets = plan.get(
            "remove",
            []
        )

        add_actions = plan.get(
            "add",
            []
        )

        if not isinstance(
            remove_targets,
            list
        ):

            return (
                "The workflow removal plan "
                "was invalid, Sir."
            )

        if not isinstance(
            add_actions,
            list
        ):

            return (
                "The workflow addition plan "
                "was invalid, Sir."
            )

        if (
            not remove_targets
            and
            not add_actions
        ):

            return (
                "I couldn't determine any "
                "changes to make, Sir."
            )

        # ========================================
        # APPLY EDIT
        # ========================================

        with self.state_lock:

            actions = self.workflows[name]

            removed_actions = []

            # ====================================
            # REMOVE TARGETS
            # ====================================

            for target in remove_targets:

                target = str(
                    target
                ).lower().strip()

                if not target:

                    continue

                target_normalized = self.normalize_target(
                    target
                )

                matching_indexes = []

                for index, action in enumerate(
                    actions
                ):

                    if not isinstance(
                        action,
                        (list, tuple)
                    ):

                        continue

                    if not action:

                        continue

                    action_type = str(
                        action[0]
                    ).lower().strip()

                    parameters = [
                        self.normalize_target(value)
                        for value in action[1:]
                    ]

                    normalized_action_type = self.normalize_target(
                        action_type
                    )

                    action_text = " ".join(
                        [normalized_action_type] + parameters
                    )

                    readable_text = action_text

                    if (
                        target_normalized == normalized_action_type
                        or
                        target_normalized in action_text
                    ):

                        matching_indexes.append(
                            index
                        )

                if not matching_indexes:

                    continue

                remove_index = (
                    matching_indexes[-1]
                )

                removed_action = actions.pop(
                    remove_index
                )

                removed_actions.append(
                    removed_action
                )

                # --------------------------------
                # Remove associated wait
                # --------------------------------

                if remove_index > 0:

                    previous_index = (
                        remove_index - 1
                    )

                    if previous_index < len(
                        actions
                    ):

                        previous_action = actions[
                            previous_index
                        ]

                        if (
                            isinstance(
                                previous_action,
                                (list, tuple)
                            )
                            and
                            len(previous_action) >= 2
                            and
                            previous_action[0] == "wait"
                        ):

                            removed_wait = actions.pop(
                                previous_index
                            )

                            removed_actions.append(
                                removed_wait
                            )

            # ====================================
            # ADD ACTIONS
            # ====================================

            added_actions = []

            for action in add_actions:

                if action not in actions:

                    actions.append(
                        action
                    )

                    added_actions.append(
                        action
                    )

            # ====================================
            # CHECK CHANGES
            # ====================================

            if (
                original_actions
                ==
                actions
            ):

                return (
                    f"No changes were made to the "
                    f"{name} workflow, Sir."
                )

            # ====================================
            # SAVE
            # ====================================

            saved = self.save_workflows()

            if not saved:

                self.workflows[name] = (
                    original_actions
                )

                return (
                    f"I couldn't save the changes "
                    f"to the {name} workflow, Sir."
                )

        # ========================================
        # LOG
        # ========================================

        print(
            "Workflow edited:",
            name
        )

        print(
            "Removed actions:",
            removed_actions
        )

        print(
            "Added actions:",
            added_actions
        )

        print(
            "Updated workflow:",
            self.workflows[name]
        )

        # ========================================
        # RESPONSE
        # ========================================

        changes = []

        if removed_actions:

            changes.append(
                f"removed {len(removed_actions)} action(s)"
            )

        if added_actions:

            changes.append(
                f"added {len(added_actions)} action(s)"
            )

        change_text = " and ".join(
            changes
        )

        return (
            f"Updated the {name} workflow, Sir. "
            f"I {change_text}."
        )

    # ========================================
    # FAILURE + RETRY POLICY
    # ========================================

    def _record_failure(self, message):
        """Store the latest workflow failure reason and return False."""

        self.last_failure_reason = str(message)
        return False

    def classify_failure(self, error):
        """Classify a workflow failure as TRANSIENT or PERMANENT."""

        error_text = str(error or "").lower().strip()

        for pattern in self.PERMANENT_FAILURES:
            if pattern in error_text:
                return "PERMANENT"

        for pattern in self.TRANSIENT_FAILURES:
            if pattern in error_text:
                return "TRANSIENT"

        # Unknown failures are permanent by default. This prevents
        # automatic retry loops when the failure cause is unknown.
        return "PERMANENT"

    def should_retry(self, task):
        """Return True only when the failed task may be retried."""

        if not task:
            return False

        if task.get("status") != task_manager.FAILED:
            return False

        retry_count = int(task.get("retry_count", 0))

        if retry_count >= self.MAX_RETRIES:
            return False

        return self.classify_failure(task.get("error", "")) == "TRANSIENT"

    def retry_policy(
        self,
        task
    ):
        """Return structured retry decision information."""

        if not task:
            return {
                "retry": False,
                "reason": "Task not found.",
                "failure_type": "PERMANENT",
                "retry_count": 0,
                "escalated": True,
            }

        failure_type = self.classify_failure(
            task.get("error", "")
        )

        retry_count = int(
            task.get("retry_count", 0)
        )

        current_step = int(
            task.get("current_step", 0)
        )

        error = str(
            task.get("error", "")
        ).strip()

        if (
            failure_type == "TRANSIENT"
            and error
            and hasattr(task_manager, "has_repeated_failure")
            and task_manager.has_repeated_failure(
                task.get("task_id"),
                error,
                step=current_step,
                minimum_repetitions=2
            )
        ):
            return {
                "retry": False,
                "reason": (
                    "Repeated identical failure detected "
                    "at the same workflow step. "
                    "Automatic retry escalated."
                ),
                "failure_type": failure_type,
                "retry_count": retry_count,
                "escalated": True,
            }

        if failure_type == "PERMANENT":
            return {
                "retry": False,
                "reason": "Permanent failure.",
                "failure_type": failure_type,
                "retry_count": retry_count,
                "escalated": True,
            }

        if retry_count >= self.MAX_RETRIES:
            return {
                "retry": False,
                "reason": "Maximum retry limit reached.",
                "failure_type": failure_type,
                "retry_count": retry_count,
                "escalated": True,
            }

        return {
            "retry": True,
            "reason": "Transient failure can be retried.",
            "failure_type": failure_type,
            "retry_count": retry_count,
            "escalated": False,
        }

    def get_approved_workflow_snapshot(self, name):
        """Return a detached, validated snapshot suitable for confirmation."""
        name = str(name).lower().strip()
        name = "_".join(name.split())
        actions = self.workflows.get(name)
        if not isinstance(actions, list) or not actions or len(actions) > 100:
            return None
        try:
            source_snapshot = copy.deepcopy(actions)
        except Exception:
            return None
        snapshot = []
        for action in source_snapshot:
            if not isinstance(action, (list, tuple)) or not action:
                return None
            if not isinstance(action[0], str):
                return None
            normalized_action = [action[0].strip().lower(), *action[1:]]
            result = authorize_workflow_action(normalized_action)
            if result.get("status") != "ALLOW":
                print("[SECURITY] Workflow snapshot rejected:", result.get("reason"))
                return None
            snapshot.append(normalized_action)
        try:
            canonical = json.dumps(
                snapshot,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            if len(canonical.encode("utf-8")) > 65536:
                return None
        except (TypeError, ValueError):
            return None
        return snapshot


    def set_dependency_recovery_callback(self, callback):
        """Register a callback for successfully completed workflow tasks."""
        if callback is not None and not callable(callback):
            raise TypeError("Dependency recovery callback must be callable.")
        with self.state_lock:
            self.dependency_recovery_callback = callback

    def get_dependency_recovery_proposals(self, completed_task_id):
        """
        Build read-only proposals for WAITING tasks whose dependencies
        are now satisfied. This method never changes task state or executes.
        """
        completed_task_id = str(completed_task_id).strip()
        if not completed_task_id:
            return []

        candidates = task_manager.get_ready_dependents(completed_task_id)
        if not isinstance(candidates, list):
            return []

        proposals = []

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue

            task_id = str(candidate.get("task_id", "")).strip()
            if not task_id or candidate.get("status") != task_manager.WAITING:
                continue

            task = task_manager.get_task(task_id)
            if not isinstance(task, dict):
                continue

            if task.get("status") != task_manager.WAITING:
                continue

            workflow_name = task.get("workflow_name")
            if not isinstance(workflow_name, str) or not workflow_name.strip():
                continue

            workflow_name = "_".join(
                workflow_name.lower().strip().split()
            )

            dependencies = task.get("dependencies")
            if not isinstance(dependencies, list) or not dependencies:
                continue

            dependency_ids = []
            valid_dependencies = True
            for dependency_id in dependencies:
                if not isinstance(dependency_id, str) or not dependency_id.strip():
                    valid_dependencies = False
                    break
                dependency_ids.append(dependency_id.strip())

            if not valid_dependencies or completed_task_id not in dependency_ids:
                continue

            dependency_status = task_manager.dependency_status(task_id)
            if not isinstance(dependency_status, dict):
                continue

            if (
                dependency_status.get("failed") != []
                or dependency_status.get("blocking") != []
                or dependency_status.get("satisfied") is not True
            ):
                continue

            steps = task.get("steps")
            if not isinstance(steps, list) or not steps or len(steps) > 100:
                continue

            current_step = task.get("current_step")
            if type(current_step) is not int:
                continue
            if current_step < 0 or current_step >= len(steps):
                continue

            remaining_actions = copy.deepcopy(steps[current_step:])
            valid_actions = True

            for action in remaining_actions:
                if not isinstance(action, list) or not action:
                    valid_actions = False
                    break
                if not isinstance(action[0], str) or not action[0].strip():
                    valid_actions = False
                    break

                authorization = authorize_workflow_action(action)
                if not isinstance(authorization, dict):
                    valid_actions = False
                    break
                if authorization.get("status") != "ALLOW":
                    valid_actions = False
                    break

            if not valid_actions:
                continue

            try:
                canonical = json.dumps(
                    remaining_actions,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                if len(canonical.encode("utf-8")) > 65536:
                    continue
            except (TypeError, ValueError):
                continue

            proposals.append({
                "task_id": task_id,
                "workflow_name": workflow_name,
                "current_step": current_step,
                "total_steps": len(steps),
                "dependencies": list(dependency_ids),
                "completed_task_id": completed_task_id,
                "remaining_actions": remaining_actions,
            })

        return proposals

    @staticmethod
    def _same_action_snapshot(left, right):
        try:
            left_json = json.dumps(
                left,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
            right_json = json.dumps(
                right,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        except (TypeError, ValueError):
            return False
        return left_json == right_json

    def auto_retry_task(self, task_id):
        """Do not prepare or execute retries without a fresh approval."""
        task = task_manager.get_task(task_id)
        if task is None:
            print("[SECURITY] Retry denied: task not found.")
            return False
        print(
            "[SECURITY] Retry denied: a fresh action-bound approval "
            "is required before retrying task", task_id
        )
        return False

    # ========================================
    # RUN EXISTING TASK
    # ========================================

    def run_task(self, task_id):
        """Fail closed until task execution has an explicit approval flow."""
        print("[SECURITY] Existing task launch blocked pending explicit approval:", task_id)
        return (
            "This task cannot resume automatically. It requires a fresh "
            "trusted approval for its exact remaining actions, Sir."
        )

    def run_chain(self, chain_id):
        """Fail closed until every task in the chain has its own approval."""
        return (
            "Task-chain execution is disabled until every task can receive "
            "its own fresh action-bound approval, Sir."
        )

    def run(
        self,
        name,
        *,
        approval_token=None,
        approval_manager=None,
        approval_intent=None,
    ):
        """Launch only the exact workflow snapshot covered by trusted approval."""
        name = str(name).lower().strip()
        name = "_".join(name.split())

        if name not in self.workflows:
            return f"Sorry Sir, I don't know the {name} workflow."

        actions = self.get_approved_workflow_snapshot(name)
        if not actions:
            return (
                f"The {name} workflow is empty or contains an invalid action. "
                "It was not executed, Sir."
            )

        if approval_manager is None or not isinstance(approval_intent, dict):
            return (
                "This workflow requires fresh trusted approval for its exact "
                "action sequence, Sir."
            )

        approval_payload = [
            approval_intent,
            {"workflow_actions": actions},
        ]
        if not approval_manager.consume(approval_token, approval_payload):
            return (
                "Workflow approval was missing, expired, altered, replayed, "
                "or did not match the current action sequence. Nothing ran, Sir."
            )

        workflow_names = {"study": "Study", "coding": "Coding", "work": "Work"}
        display_name = workflow_names.get(name, name.title())

        with self.state_lock:
            if self.workflow_running:
                return (
                    f"The {self.current_workflow} workflow is already running, Sir."
                )

            task = task_manager.create_task(
                name=name,
                goal=f"Execute workflow '{name}'",
                steps=copy.deepcopy(actions),
                workflow_name=name,
            )
            if task is None:
                return f"I couldn't create a task for the {display_name} workflow, Sir."

            task_id = task["task_id"]
            self.current_task_id = task_id
            self.workflow_running = True
            self.current_workflow = name
            worker_stop_event = threading.Event()
            self.stop_event = worker_stop_event
            worker_thread = threading.Thread(
                target=self._run_workflow,
                args=(name, task_id, copy.deepcopy(actions), self._execution_capability, worker_stop_event),
                daemon=True,
            )
            self.workflow_thread = worker_thread
        try:
            worker_thread.start()
        except Exception as exc:
            failure = f"Workflow thread could not start: {exc!r}"
            try:
                task_manager.fail_task(
                    task_id,
                    failure,
                    failure_type="LAUNCH",
                )
            finally:
                with self.state_lock:
                    if (
                        self.current_task_id == task_id
                        and self.workflow_thread is worker_thread
                        and self.stop_event is worker_stop_event
                    ):
                        self.workflow_running = False
                        self.current_workflow = None
                        self.current_task_id = None
                        self.workflow_thread = None
                        self.stop_event = threading.Event()

            print("[WORKFLOW] Launch failed:", failure)
            return f"The {display_name} workflow could not start, Sir."

        print("[WORKFLOW] Started:", name, "| Task:", task_id)
        return f"{display_name} session started, Sir. Task ID: {task_id}"

    # ========================================
    # BACKGROUND WORKFLOW
    # ========================================
    # BACKGROUND WORKFLOW
    # ========================================

    def _run_workflow(
        self,
        name,
        task_id,
        approved_actions=None,
        execution_capability=None,
        stop_event=None,
        resume_existing_task=False,
    ):

        worker_stop_event = (
            stop_event if stop_event is not None else self.stop_event
        )

        completed_successfully = False
        try:
            if execution_capability is not self._execution_capability:
                raise PermissionError(
                    "Workflow thread launch denied: missing execution capability."
                )

            if not isinstance(approved_actions, list) or not approved_actions:
                raise ValueError(
                    "Workflow thread launch denied: missing approved snapshot."
                )

            if worker_stop_event.is_set():
                task_manager.cancel_task(task_id)
                print("[WORKFLOW] Cancellation received before execution:", task_id)
                return

            print(
                f"Starting {name} workflow..."
            )

            while True:

                # ----------------------------------------
                # Dependency gate for existing task
                # ----------------------------------------

                dependency_status = task_manager.dependency_status(
                    task_id
                )

                if dependency_status is None:
                    raise RuntimeError(
                        "Dependency status is missing or invalid."
                    )

                failed_dependencies = dependency_status.get("failed")
                if failed_dependencies is None:
                    raise RuntimeError(
                        "Dependency failure state is unknown."
                    )

                if failed_dependencies:
                    raise RuntimeError(
                        "Workflow dependencies failed: "
                        + ", ".join(failed_dependencies)
                    )

                if not dependency_status.get("satisfied", False):
                    waiting_task = task_manager.wait_for_dependencies(task_id)
                    if waiting_task is None:
                        raise RuntimeError(
                            "Could not persist WAITING dependency state."
                        )

                    print(
                        "[WORKFLOW] Task is waiting for dependencies:",
                        task_id,
                        "| Blocking:",
                        dependency_status.get("blocking", [])
                    )
                    return

                # Verify the persisted task snapshot before changing its state.
                persisted_task = task_manager.get_task(task_id)
                if persisted_task is None or not self._same_action_snapshot(
                    persisted_task.get("steps", []),
                    approved_actions,
                ):
                    raise ValueError(
                        "Persisted task steps differ from the approved workflow snapshot."
                    )

                # ----------------------------------------
                # Task: PENDING -> RUNNING
                # ----------------------------------------

                if resume_existing_task:
                    task = task_manager.get_task(task_id)
                    if (
                        task is None
                        or task.get("status") != task_manager.RUNNING
                    ):
                        raise RuntimeError(
                            "Approved recovery task is not in RUNNING state."
                        )
                else:
                    task = task_manager.start_task(
                        task_id
                    )

                    if task is None:
                        latest_status = task_manager.dependency_status(task_id)

                        if (
                            latest_status is not None
                            and not latest_status.get("failed")
                            and not latest_status.get("satisfied", False)
                        ):
                            waiting_task = task_manager.wait_for_dependencies(task_id)
                            if waiting_task is not None:
                                print(
                                    "[WORKFLOW] Task moved to WAITING after "
                                    "dependency recheck:",
                                    task_id
                                )
                                return

                        raise RuntimeError(
                            "Task could not transition into RUNNING."
                        )

                self.last_failure_reason = None

                all_actions = copy.deepcopy(task.get("steps", []))
                if not self._same_action_snapshot(all_actions, approved_actions):
                    raise ValueError(
                        "Persisted task steps differ from the approved workflow snapshot."
                    )

                start_step = int(
                    task.get("current_step", 0)
                )

                if start_step < 0 or start_step > len(all_actions):
                    raise ValueError(
                        f"Invalid persisted task step: {start_step}"
                    )

                actions = all_actions[start_step:]

                print(
                    "[WORKFLOW] Execution range:",
                    f"{start_step} -> {len(all_actions)}"
                )

                success = self.execute_actions(
                    actions,
                    task_id=task_id,
                    step_offset=start_step,
                    execution_capability=self._execution_capability,
                    stop_event=worker_stop_event,
                )

                # ----------------------------------------
                # CANCELLED
                # ----------------------------------------

                if worker_stop_event.is_set():
                    task_manager.cancel_task(
                        task_id
                    )
                    print(
                        f"{name.title()} workflow stopped."
                    )
                    return

                # ----------------------------------------
                # FAILED
                # ----------------------------------------

                if not success:

                    failure_message = (
                        self.last_failure_reason
                        or
                        "Workflow execution failed."
                    )

                    failure_type = self.classify_failure(
                        failure_message
                    )

                    current_step = int(
                        task_manager.get_current_step(task_id)
                        or 0
                    )

                    task_manager.fail_task(
                        task_id,
                        failure_message,
                        failure_type=failure_type,
                        step=current_step
                    )

                    failed_task = task_manager.get_task(
                        task_id
                    )

                    policy = self.retry_policy(
                        failed_task
                    )

                    print(
                        "[WORKFLOW] Failure:",
                        failure_message
                    )
                    print(
                        "[WORKFLOW] Failure type:",
                        policy.get("failure_type")
                    )
                    print(
                        "[WORKFLOW] Retry allowed:",
                        policy.get("retry")
                    )
                    print(
                        "[WORKFLOW] Retry count:",
                        policy.get("retry_count")
                    )
                    print(
                        "[WORKFLOW] Escalated:",
                        policy.get("escalated", False)
                    )

                    if policy.get("retry"):
                        print(
                            "[SECURITY] Automatic retry suppressed: fresh "
                            "action-bound approval is required."
                        )
                    print(
                        "[WORKFLOW] Retry denied:",
                        "fresh trusted approval required; " + str(policy.get("reason"))
                    )
                    print(
                        f"{name.title()} workflow failed."
                    )
                    return

                # ----------------------------------------
                # COMPLETED
                # ----------------------------------------

                task_manager.set_current_step(
                    task_id,
                    len(all_actions)
                )

                task_manager.complete_task(
                    task_id
                )
                completed_task = task_manager.get_task(task_id)
                completed_successfully = (
                    isinstance(completed_task, dict)
                    and completed_task.get('status') == task_manager.COMPLETED
                )

                print(
                    f"{name.title()} workflow completed successfully."
                )

                return

        except Exception as e:

            print(
                "Workflow Error:",
                repr(e)
            )

            failure_message = repr(e)
            failure_type = self.classify_failure(
                failure_message
            )

            try:
                task_manager.fail_task(
                    task_id,
                    failure_message,
                    failure_type=failure_type
                )
            except Exception as fail_error:
                print(
                    "[WORKFLOW] Could not record exception failure:",
                    repr(fail_error)
                )

        finally:

            with self.state_lock:
                owns_worker_state = (
                    self.current_task_id == task_id
                    and self.stop_event is worker_stop_event
                    and (
                        self.workflow_thread is threading.current_thread()
                        or self.workflow_thread is None
                    )
                )
                if owns_worker_state:
                    self.workflow_running = False
                    self.current_workflow = None
                    self.current_task_id = None
                    self.workflow_thread = None
                    self.stop_event = threading.Event()
            # Notify recovery only after releasing worker ownership.
            if owns_worker_state and completed_successfully:
                callback = self.dependency_recovery_callback
                if callable(callback):
                    try:
                        callback(task_id)
                    except Exception as callback_error:
                        print('[WORKFLOW] Recovery notification failed:', repr(callback_error))

            print(
                "Workflow engine is ready."
            )
    # ========================================
    # TASK BINDING
    # ========================================

    def get_task_for_workflow(self, name):

        name = str(name).lower().strip()
        name = "_".join(name.split())

        for task in task_manager.list_tasks():
            if task.get("workflow_name") == name:
                return task

        return None

    def task_status(self, name):

        task = self.get_task_for_workflow(name)

        if task is None:
            return f"There is no task bound to the {name} workflow, Sir."

        return (
            f"The {name} workflow task is "
            f"{task.get('status', 'UNKNOWN')}, Sir. "
            f"Step {task.get('current_step', 0)} of "
            f"{len(task.get('steps', []))}."
        )

    # ========================================
    # RESUME FAILED TASK
    # ========================================



    def get_resume_approval_payload(self, task_id, completed_task_id):
        """Return a task-bound approval payload after action authorization."""
        payload = task_manager.get_resume_approval_payload(
            task_id,
            completed_task_id,
        )

        if not isinstance(payload, list) or len(payload) != 3:
            return None

        if not all(isinstance(item, dict) for item in payload):
            return None

        remaining_actions = payload[2].get("remaining_actions")
        if not isinstance(remaining_actions, list) or not remaining_actions:
            return None

        for action in remaining_actions:
            if (
                not isinstance(action, list)
                or not action
                or not isinstance(action[0], str)
                or not action[0].strip()
            ):
                return None

            authorization = authorize_workflow_action(action)
            authorization_status = (
                authorization.get("status")
                if isinstance(authorization, dict)
                else getattr(authorization, "status", None)
            )
            authorization_reason = (
                authorization.get("reason")
                if isinstance(authorization, dict)
                else getattr(authorization, "reason", None)
            )
            if authorization_status != "ALLOW":
                print(
                    "[SECURITY] Recovery action rejected:",
                    authorization_reason or "Invalid authorization result",
                )
                return None

        return payload

    def resume_waiting_task(
        self,
        task_id,
        completed_task_id,
        approval_token,
        approval_manager,
    ):
        """Resume a WAITING workflow only with fresh task-bound approval."""
        if not isinstance(task_id, str) or not task_id.strip():
            return "Invalid recovery task ID."
        if not isinstance(completed_task_id, str) or not completed_task_id.strip():
            return "Invalid completed dependency ID."
        if approval_manager is None:
            return "Fresh trusted approval is required."

        task_id = task_id.strip()
        completed_task_id = completed_task_id.strip()

        task = None
        worker_thread = None
        worker_stop_event = None

        try:
            with self.state_lock:
                if self.workflow_running:
                    return (
                        f"The {self.current_workflow} workflow is already running, Sir."
                    )

                payload = self.get_resume_approval_payload(
                    task_id,
                    completed_task_id,
                )
                if payload is None:
                    return (
                        "The waiting task is no longer eligible or its remaining "
                        "actions failed authorization. Nothing was resumed, Sir."
                    )

                workflow_name = payload[0].get("workflow_name")
                approved_actions = payload[1].get("workflow_snapshot")

                if (
                    not isinstance(workflow_name, str)
                    or not workflow_name.strip()
                    or not isinstance(approved_actions, list)
                    or not approved_actions
                ):
                    return "The approved workflow snapshot is invalid, Sir."

                task = task_manager.resume_waiting_task_with_approval(
                    task_id,
                    completed_task_id,
                    approval_token,
                    approval_manager,
                )

                if task is None:
                    return (
                        "Recovery approval was invalid, expired, replayed, "
                        "or no longer matched the task. Nothing was resumed, Sir."
                    )

                if (
                    task.get("status") != task_manager.RUNNING
                    or not self._same_action_snapshot(
                        task.get("steps"),
                        approved_actions,
                    )
                    or task.get("current_step") != payload[0].get("current_step")
                ):
                    task_manager.fail_task(
                        task_id,
                        "Recovery snapshot changed after approval consumption.",
                        failure_type="SECURITY",
                    )
                    return (
                        "The task changed after approval. Recovery was stopped, Sir."
                    )

                worker_stop_event = threading.Event()

                worker_thread = threading.Thread(
                    target=self._run_workflow,
                    args=(
                        workflow_name,
                        task_id,
                        copy.deepcopy(approved_actions),
                        self._execution_capability,
                        worker_stop_event,
                        True,
                    ),
                    daemon=True,
                )

                self.current_task_id = task_id
                self.current_workflow = workflow_name
                self.workflow_running = True
                self.stop_event = worker_stop_event
                self.workflow_thread = worker_thread

            worker_thread.start()

        except Exception as exc:
            print("[WORKFLOW] Recovery launch failed:", repr(exc))

            if task is not None:
                try:
                    task_manager.fail_task(
                        task_id,
                        f"Recovery worker could not start: {exc!r}",
                        failure_type="LAUNCH",
                    )
                except Exception as fail_error:
                    print(
                        "[WORKFLOW] Could not record recovery launch failure:",
                        repr(fail_error),
                    )

            if worker_stop_event is not None:
                with self.state_lock:
                    if (
                        self.current_task_id == task_id
                        and self.workflow_thread is worker_thread
                        and self.stop_event is worker_stop_event
                    ):
                        self.workflow_running = False
                        self.current_workflow = None
                        self.current_task_id = None
                        self.workflow_thread = None
                        self.stop_event = threading.Event()

            return "The approved workflow recovery could not start, Sir."

        print(
            "[WORKFLOW] Recovery started:",
            workflow_name,
            "| Task:",
            task_id,
        )
        return (
            f"{workflow_name.replace('_', ' ').title()} recovery started, Sir. "
            f"Task ID: {task_id}"
        )
    def resume_task(self, task_id):
        """Fail closed until the remaining persisted steps are explicitly approved."""
        print("[SECURITY] Failed-task resume blocked pending exact action approval:", task_id)
        return (
            "Failed-task resume is disabled until the remaining persisted "
            "steps can be shown and approved explicitly, Sir."
        )

    def cancel(self):

        with self.state_lock:
            if not self.workflow_running:
                return (
                    "There is no workflow running, Sir."
                )

            self.stop_event.set()

        print(
            "Workflow stop requested."
        )

        return (
            "Stopping the current workflow, Sir."
        )

    # ========================================
    # WORKFLOW STATUS
    # ========================================

    def status(self):

        with self.state_lock:

            if not self.workflow_running:

                return (
                    "No workflow is currently running, Sir."
                )

            if self.stop_event.is_set():

                return (
                    f"The {self.current_workflow} "
                    f"workflow is stopping, Sir."
                )

            return (
                f"The {self.current_workflow} "
                f"workflow is currently running, Sir."
            )

    # ========================================
    # SHOW WORKFLOW
    # ========================================

    def show_workflow(
        self,
        name
    ):

        name = str(
            name
        ).lower().strip()

        name = "_".join(
            name.split()
        )

        if not name:

            return (
                "Please provide a workflow name, Sir."
            )

        if name not in self.workflows:

            return (
                f"I couldn't find the "
                f"{name} workflow, Sir."
            )

        actions = self.workflows[name]

        if not actions:

            return (
                f"The {name} workflow is empty, Sir."
            )

        lines = [
            f"The {name} workflow contains:"
        ]

        action_names = {

            "open_app":
                "Open application",

            "close_app":
                "Close application",

            "open_url":
                "Open URL",

            "wait":
                "Wait",

            "press":
                "Press key",

            "hotkey":
                "Press hotkey",

            "type":
                "Type text",

            "click":
                "Click",

            "double_click":
                "Double click",

            "right_click":
                "Right click",

            "scroll_up":
                "Scroll up",

            "scroll_down":
                "Scroll down",
        }

        for index, action in enumerate(
            actions,
            start=1
        ):

            if not action:

                continue

            if not isinstance(
                action,
                (list, tuple)
            ):

                lines.append(
                    f"{index}. Invalid action"
                )

                continue

            action_type = action[0]

            parameters = action[1:]

            readable_name = action_names.get(
                action_type,
                str(
                    action_type
                ).replace(
                    "_",
                    " "
                ).title()
            )

            if parameters:

                parameter_text = ", ".join(
                    str(parameter)
                    for parameter in parameters
                )

                lines.append(
                    f"{index}. "
                    f"{readable_name}: "
                    f"{parameter_text}"
                )

            else:

                lines.append(
                    f"{index}. "
                    f"{readable_name}"
                )

        return "\n".join(
            lines
        )

    # ========================================
    # ACTION ENGINE
    # ========================================

    def execute_actions(
        self,
        actions,
        task_id=None,
        step_offset=0,
        *,
        execution_capability=None,
        stop_event=None,
    ):
        if execution_capability is not self._execution_capability:
            self.last_failure_reason = "Workflow execution requires an approved capability."
            print("[SECURITY] Direct action execution denied.")
            return False

        cancellation_event = (
            stop_event if stop_event is not None else self.stop_event
        )

        for index, action in enumerate(actions):

            absolute_step = step_offset + index

            if task_id is not None:

                task_manager.set_current_step(
                    task_id,
                    absolute_step
                )

            if cancellation_event.is_set():

                print(
                    "Workflow cancellation detected."
                )

                self.last_failure_reason = "Workflow cancellation detected."
                return False

            if not action:

                continue

            if not isinstance(
                action,
                (list, tuple)
            ):

                print(
                    "Workflow Error: "
                    "Invalid action format."
                )

                return self._record_failure(
                    "Invalid action format."
                )

            authorization = authorize_workflow_action(action)
            if authorization.get("status") != "ALLOW":
                reason = authorization.get("reason", "Workflow action denied")
                print("[SECURITY] Workflow action denied:", reason)
                return self._record_failure(str(reason))

            action_type = action[0]

            parameters = action[1:]

            print(
                "Workflow Action:",
                action
            )

            # ====================================
            # OPEN APPLICATION
            # ====================================

            if action_type == "open_app":

                if not parameters:

                    print(
                        "Workflow Error: "
                        "Missing application name."
                    )

                    return self._record_failure(
                        "Missing application name."
                    )

                result = apps.open_app(
                    parameters[0]
                )

                print(
                    "Workflow Result:",
                    result
                )

                if not result:

                    return self._record_failure(
                        f"Failed to open application: {parameters[0]}"
                    )

                result_text = str(
                    result
                ).lower()

                if (
                    "couldn't open"
                    in result_text
                    or
                    "don't know how to open"
                    in result_text
                ):

                    return self._record_failure(
                        str(result)
                    )

            # ====================================
            # CLOSE APPLICATION
            # ====================================

            elif action_type == "close_app":

                if not parameters:

                    print(
                        "Workflow Error: "
                        "Missing application name."
                    )

                    return self._record_failure(
                        "Missing application name."
                    )

                result = apps.close_app(
                    parameters[0]
                )

                print(
                    "Workflow Result:",
                    result
                )

                if not result:

                    return self._record_failure(
                        f"Failed to close application: {parameters[0]}"
                    )

            # ====================================
            # OPEN URL
            # ====================================

            elif action_type == "open_url":

                if not parameters:

                    print(
                        "Workflow Error: "
                        "Missing URL."
                    )

                    return self._record_failure(
                        "Missing URL."
                    )

                url = str(
                    parameters[0]
                ).strip()

                parsed = urlparse(
                    url
                )

                if parsed.scheme not in (
                    "http",
                    "https"
                ):

                    print(
                        "Workflow Error: "
                        f"Invalid URL: {url}"
                    )

                    return self._record_failure(
                        f"Invalid URL: {url}"
                    )

                if not parsed.netloc:

                    print(
                        "Workflow Error: "
                        f"Invalid URL: {url}"
                    )

                    return self._record_failure(
                        f"Invalid URL: {url}"
                    )

                if cancellation_event.is_set():

                    self.last_failure_reason = "Workflow cancellation detected."
                    return False

                try:

                    opened = webbrowser.open(
                        url,
                        new=2
                    )

                except Exception as e:

                    print(
                        "URL Open Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

                if not opened:

                    print(
                        "Workflow Result:",
                        f"Failed to open {url}"
                    )

                    return self._record_failure(
                        f"Failed to open {url}"
                    )

                print(
                    "Workflow Result:",
                    f"Opened {url}"
                )

            # ====================================
            # WAIT
            # ====================================

            elif action_type == "wait":

                if not parameters:

                    print(
                        "Workflow Error: "
                        "Missing wait duration."
                    )

                    return self._record_failure(
                        "Missing wait duration."
                    )

                try:

                    seconds = float(
                        parameters[0]
                    )

                    if seconds < 0:

                        print(
                            "Workflow Error: "
                            "Wait duration cannot "
                            "be negative."
                        )

                        return False

                    print(
                        "Workflow Result:",
                        f"Waiting {seconds} seconds."
                    )

                    stopped = cancellation_event.wait(
                        timeout=seconds
                    )

                    if stopped:

                        print(
                            "Workflow stopped "
                            "during wait."
                        )

                        self.last_failure_reason = "Workflow cancellation detected."
                        return False

                except (
                    ValueError,
                    TypeError
                ) as e:

                    print(
                        "Wait Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # PRESS KEY
            # ====================================

            elif action_type == "press":

                if not parameters:

                    print(
                        "Workflow Error: "
                        "Missing key."
                    )

                    return self._record_failure(
                        "Missing key."
                    )

                try:

                    result = automation.press(
                        parameters[0]
                    )
                    if getattr(result, 'status', None) not in ('succeeded', 'already_satisfied'):
                        return self._record_failure(
                            getattr(result, 'error', None) or str(result)
                        )

                    print(
                        "Workflow Result:",
                        result
                    )

                except Exception as e:

                    print(
                        "Press Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # HOTKEY
            # ====================================

            elif action_type == "hotkey":

                if not parameters:

                    print(
                        "Workflow Error: "
                        "Missing hotkey."
                    )

                    return self._record_failure(
                        "Missing hotkey."
                    )

                try:

                    result = automation.hotkey(
                        *parameters
                    )
                    if getattr(result, 'status', None) not in ('succeeded', 'already_satisfied'):
                        return self._record_failure(
                            getattr(result, 'error', None) or str(result)
                        )

                    print(
                        "Workflow Result:",
                        result
                    )

                except Exception as e:

                    print(
                        "Hotkey Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # TYPE TEXT
            # ====================================

            elif action_type == "type":

                if not parameters:

                    print(
                        "Workflow Error: "
                        "Missing text."
                    )

                    return self._record_failure(
                        "Missing text."
                    )

                try:

                    result = automation.type_text(
                        parameters[0]
                    )
                    if getattr(result, 'status', None) not in ('succeeded', 'already_satisfied'):
                        return self._record_failure(
                            getattr(result, 'error', None) or str(result)
                        )

                    print(
                        "Workflow Result:",
                        result
                    )

                except Exception as e:

                    print(
                        "Type Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # CLICK
            # ====================================

            elif action_type == "click":

                try:

                    result = automation.click()
                    if getattr(result, 'status', None) not in ('succeeded', 'already_satisfied'):
                        return self._record_failure(
                            getattr(result, 'error', None) or str(result)
                        )

                    print(
                        "Workflow Result:",
                        result
                    )

                except Exception as e:

                    print(
                        "Click Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # DOUBLE CLICK
            # ====================================

            elif action_type == "double_click":

                try:

                    result = automation.double_click()
                    if getattr(result, 'status', None) not in ('succeeded', 'already_satisfied'):
                        return self._record_failure(
                            getattr(result, 'error', None) or str(result)
                        )

                    print(
                        "Workflow Result:",
                        result
                    )

                except Exception as e:

                    print(
                        "Double Click Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # RIGHT CLICK
            # ====================================

            elif action_type == "right_click":

                try:

                    result = automation.right_click()
                    if getattr(result, 'status', None) not in ('succeeded', 'already_satisfied'):
                        return self._record_failure(
                            getattr(result, 'error', None) or str(result)
                        )

                    print(
                        "Workflow Result:",
                        result
                    )

                except Exception as e:

                    print(
                        "Right Click Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # SCROLL UP
            # ====================================

            elif action_type == "scroll_up":

                try:

                    result = automation.scroll_up()
                    if getattr(result, 'status', None) not in ('succeeded', 'already_satisfied'):
                        return self._record_failure(
                            getattr(result, 'error', None) or str(result)
                        )

                    print(
                        "Workflow Result:",
                        result
                    )

                except Exception as e:

                    print(
                        "Scroll Up Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # SCROLL DOWN
            # ====================================

            elif action_type == "scroll_down":

                try:

                    result = automation.scroll_down()
                    if getattr(result, 'status', None) not in ('succeeded', 'already_satisfied'):
                        return self._record_failure(
                            getattr(result, 'error', None) or str(result)
                        )

                    print(
                        "Workflow Result:",
                        result
                    )

                except Exception as e:

                    print(
                        "Scroll Down Error:",
                        repr(e)
                    )

                    return self._record_failure(
                        repr(e)
                    )

            # ====================================
            # UNKNOWN ACTION
            # ====================================

            else:

                print(
                    "Unknown Workflow Action:",
                    action_type
                )

                return self._record_failure(
                    f"Unknown Workflow Action: {action_type}"
                )

        # ========================================
        # ALL ACTIONS COMPLETED
        # ========================================

        return True

    # ========================================
    # DELETE WORKFLOW
    # ========================================

    def delete_workflow(
        self,
        name
    ):

        name = str(
            name
        ).lower().strip()

        name = "_".join(
            name.split()
        )

        if not name:

            return (
                "Please provide a workflow name, Sir."
            )

        with self.state_lock:

            if self.workflow_running:

                if self.current_workflow == name:

                    return (
                        "Please stop the running "
                        "workflow first, Sir."
                    )

                return (
                    "Please wait until the running "
                    "workflow finishes, Sir."
                )

            if name not in self.workflows:

                return (
                    f"I couldn't find the "
                    f"{name} workflow, Sir."
                )

            deleted_workflow = self.workflows.pop(
                name
            )

            saved = self.save_workflows()

            if not saved:

                self.workflows[name] = (
                    deleted_workflow
                )

                return (
                    f"Workflow '{name}' could not "
                    f"be deleted, Sir."
                )

        return (
            f"Workflow '{name}' deleted, Sir."
        )

    # ========================================
    # DELETE ALIAS
    # ========================================

    def delete(
        self,
        name
    ):

        return self.delete_workflow(
            name
        )

    # ========================================
    # LIST WORKFLOWS
    # ========================================

    def list_workflows(self):

        if not self.workflows:

            return (
                "You don't have any workflows, Sir."
            )

        lines = [
            "Your workflows, Sir:"
        ]

        for name in self.workflows:

            lines.append(
                f"• {name}"
            )

        return "\n".join(
            lines
        )


# ========================================
# GLOBAL WORKFLOW MANAGER
# ========================================

workflows = WorkflowManager()
