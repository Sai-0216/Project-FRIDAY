"""
Project FRIDAY
Task Manager
Phase 17.3 - Task Execution State & Recovery
"""

import json
import copy
import os
import threading
import uuid
from datetime import datetime


class TaskManager:

    # ========================================
    # TASK STATES
    # ========================================

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    WAITING = "WAITING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"

    VALID_STATES = {
        PENDING,
        RUNNING,
        PAUSED,
        WAITING,
        FAILED,
        COMPLETED,
        CANCELLED,
        INTERRUPTED,
    }

    # ========================================
    # VALID STATE TRANSITIONS
    # ========================================

    VALID_TRANSITIONS = {

        PENDING: {
            RUNNING,
            WAITING,
            FAILED,
            CANCELLED,
        },

        RUNNING: {
            PAUSED,
            WAITING,
            FAILED,
            COMPLETED,
            CANCELLED,
            INTERRUPTED,
        },

        PAUSED: {
            RUNNING,
            CANCELLED,
        },

        WAITING: {
            RUNNING,
            CANCELLED,
            FAILED,
        },

        FAILED: {
            RUNNING,
            CANCELLED,
        },
        
        INTERRUPTED: {
            RUNNING, 
            FAILED,
            CANCELLED,
        },

        COMPLETED: set(),

        CANCELLED: set(),
    }

    # ========================================
    # INITIALIZATION
    # ========================================

    def __init__(self):

        self.data_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),
            "data"
        )

        self.task_file = os.path.join(
            self.data_dir,
            "tasks.json"
        )

        os.makedirs(
            self.data_dir,
            exist_ok=True
        )

        self.lock = threading.RLock()

        self.tasks = self._load_tasks()

    # ========================================
    # LOAD TASKS
    # ========================================

    def _load_tasks(self):

        if not os.path.exists(
            self.task_file
        ):
            return {}

        try:

            with open(
                self.task_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(
                data,
                dict
            ):
                raise ValueError(
                    "Task file must contain an object."
                )

            return data

        except (
            json.JSONDecodeError,
            OSError,
            ValueError
        ) as error:

            print(
                "[TASK MANAGER] Load Error:",
                repr(error)
            )

            return {}
        
    def recover_interrupted_tasks(self):
        """
        Recover tasks that were left RUNNING when FRIDAY stopped.

        RUNNING tasks are marked INTERRUPTED while preserving:
        - current_step
        - retry_count
        - failure_history
        - workflow_name
        - chain information
        """

        recovered = []

        with self.lock:

            for task_id, task in self.tasks.items():

                if task.get("status") != self.RUNNING:
            
                        
                    continue

                task["status"] = self.INTERRUPTED

                task["error"] = (
                    task.get("error")
                    or
                    "Task interrupted by FRIDAY shutdown or restart."
                )

                recovered.append(
                    task_id
                )

            if recovered:

                if not self._save_tasks():

                    print(
                        "[TASK MANAGER] Failed to persist interrupted tasks."
                    )

                    return []

        if recovered:

            for task_id in recovered:

                print(
                    "[TASK MANAGER] RUNNING -> INTERRUPTED | Task:",
                    task_id
                )

            print(
                "[TASK MANAGER] Recovered interrupted tasks:",
                len(recovered)
            )

        return recovered

    # ========================================
    # SAVE TASKS
    # ========================================

    def _save_tasks(self):

        temporary_file = (
            self.task_file + ".tmp"
        )

        try:

            with open(
                temporary_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.tasks,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(
                temporary_file,
                self.task_file
            )

            return True

        except OSError as error:

            print(
                "[TASK MANAGER] Save Error:",
                repr(error)
            )

            return False

    # ========================================
    # CREATE TASK
    # ========================================

    def create_task(
        self,
        name,
        goal,
        steps=None,
        workflow_name=None
    ):

        name = str(
            name
        ).strip()

        goal = str(
            goal
        ).strip()

        if not name:
            return None

        if not goal:
            goal = name

        if steps is None:
            steps = []

        if not isinstance(
            steps,
            list
        ):
            return None

        # Normalize workflow name

        if workflow_name is not None:

            workflow_name = str(
                workflow_name
            ).lower().strip()

            workflow_name = "_".join(
                workflow_name.split()
            )

        task_id = str(
            uuid.uuid4()
        )

        now = datetime.now().isoformat()

        task = {

            "task_id":
                task_id,

            "name":
                name,

            "goal":
                goal,

            "workflow_name":
                workflow_name,

            "steps":
                steps,

            "current_step":
                0,

            "status":
                self.PENDING,

            "created_at":
                now,

            "started_at":
                None,

            "completed_at":
                None,

            "error":
                None,

            "retry_count":
                0,

            "failure_history":
                [],
            
            "dependencies":
                [],
            
            "chain_id":
                None,

            "chain_order":
                0,
        }

        with self.lock:

            self.tasks[
                task_id
            ] = task

            if not self._save_tasks():

                self.tasks.pop(
                    task_id,
                    None
                )

                return None

        print(
            "[TASK MANAGER] Task created:",
            task_id,
            "| Workflow:",
            workflow_name
        )

        return dict(task)

    # ========================================
    # GET TASK
    # ========================================

    def get_task(
        self,
        task_id
    ):

        with self.lock:

            task = self.tasks.get(
                str(task_id).strip()
            )

            return (
                dict(task)
                if task
                else None
            )

    # ========================================
    # GET TASK FOR WORKFLOW
    # ========================================

    def get_task_for_workflow(
        self,
        workflow_name,
        active_only=False
    ):

        workflow_name = str(
            workflow_name
        ).lower().strip()

        workflow_name = "_".join(
            workflow_name.split()
        )

        with self.lock:

            matches = [
                dict(task)
                for task in self.tasks.values()
                if task.get(
                    "workflow_name"
                ) == workflow_name
            ]

            if active_only:

                matches = [
                    task
                    for task in matches
                    if task.get("status")
                    in {
                        self.RUNNING,
                        self.PAUSED,
                        self.WAITING,
                    }
                ]

            if not matches:
                return None

            matches.sort(
                key=lambda task:
                    task.get(
                        "created_at",
                        ""
                    ),
                reverse=True
            )

            return matches[0]

    # ========================================
    # BIND WORKFLOW
    # ========================================

    def bind_workflow(
        self,
        task_id,
        workflow_name
    ):

        workflow_name = str(
            workflow_name
        ).lower().strip()

        workflow_name = "_".join(
            workflow_name.split()
        )

        with self.lock:

            task = self.tasks.get(
                str(task_id).strip()
            )

            if (
                task is None
                or not workflow_name
            ):
                return None

            task[
                "workflow_name"
            ] = workflow_name

            if not self._save_tasks():
                return None

            print(
                "[TASK MANAGER] Workflow bound:",
                workflow_name,
                "->",
                task_id
            )

            return dict(task)
        
    def add_dependency(
        self,
        task_id,
        dependency_task_id
    ):
        """
        Add a dependency relationship:

            task_id depends on dependency_task_id

        Prevents:
        - missing tasks
        - self-dependencies
        - duplicate dependencies
        - circular dependency chains
        """

        task_id = str(
            task_id
        ).strip()

        dependency_task_id = str(
            dependency_task_id
        ).strip()

        if not task_id or not dependency_task_id:
            return None

        if task_id == dependency_task_id:
            print(
                "[TASK MANAGER] Dependency rejected:",
                "A task cannot depend on itself."
            )
            return None

        with self.lock:

            task = self.tasks.get(
                task_id
            )

            dependency_task = self.tasks.get(
                dependency_task_id
            )

            if task is None:
                print(
                    "[TASK MANAGER] Dependency rejected:",
                    "task not found:",
                    task_id
                )
                return None

            if dependency_task is None:
                print(
                    "[TASK MANAGER] Dependency rejected:",
                    "dependency task not found:",
                    dependency_task_id
                )
                return None

            dependencies = task.get(
                "dependencies",
                []
            )

            if not isinstance(
                dependencies,
                list
            ):
                dependencies = []

            if dependency_task_id in dependencies:

                print(
                    "[TASK MANAGER] Dependency already exists:",
                    task_id,
                    "<-",
                    dependency_task_id
                )

                return None

            # ========================================
            # CIRCULAR DEPENDENCY CHECK
            # ========================================

            def depends_on(
                current_id,
                target_id,
                visited=None
            ):
                if visited is None:
                    visited = set()

                if current_id in visited:
                    return False

                visited.add(
                    current_id
                )

                current_task = self.tasks.get(
                    current_id
                )

                if current_task is None:
                    return False

                current_dependencies = (
                    current_task.get(
                        "dependencies",
                        []
                    )
                )

                if not isinstance(
                    current_dependencies,
                    list
                ):
                    return False

                for parent_id in current_dependencies:

                    parent_id = str(
                        parent_id
                    ).strip()

                    if parent_id == target_id:
                        return True

                    if depends_on(
                        parent_id,
                        target_id,
                        visited
                    ):
                        return True

                return False

            # Adding:
            #
            # A -> B
            #
            # is invalid when B already depends on A
            # somewhere in its dependency chain.

            if depends_on(
                dependency_task_id,
                task_id
            ):

                print(
                    "[TASK MANAGER] Dependency rejected:",
                    "circular dependency detected:",
                    task_id,
                    "<-",
                    dependency_task_id
                )

                return None

            dependencies.append(
                dependency_task_id
            )

            task[
                "dependencies"
            ] = dependencies

            if not self._save_tasks():
                return None

            print(
                "[TASK MANAGER] Dependency added:",
                task_id,
                "<-",
                dependency_task_id
            )

            return dict(
                task
            )


    def remove_dependency(
        self,
        task_id,
        dependency_task_id
    ):
        """
        Remove an existing dependency.
        """

        task_id = str(
            task_id
        ).strip()

        dependency_task_id = str(
            dependency_task_id
        ).strip()

        with self.lock:

            task = self.tasks.get(
                task_id
            )

            if task is None:
                return None

            dependencies = task.get(
                "dependencies",
                []
            )

            if not isinstance(
                dependencies,
                list
            ):
                dependencies = []

            if dependency_task_id not in dependencies:

                print(
                    "[TASK MANAGER] Dependency not found:",
                    task_id,
                    "<-",
                    dependency_task_id
                )

                return None

            dependencies.remove(
                dependency_task_id
            )

            task[
                "dependencies"
            ] = dependencies

            if not self._save_tasks():
                return None

            print(
                "[TASK MANAGER] Dependency removed:",
                task_id,
                "<-",
                dependency_task_id
            )

            return dict(
                task
            )
            
    def get_blocking_dependencies(self, task_id):
        """Return unresolved dependencies; None means invalid lookup."""

        task_id = str(task_id).strip()

        with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                return None

            dependencies = task.get("dependencies", [])
            if not isinstance(dependencies, list):
                return None

            blocking = []

            for dependency_id in dependencies:
                dependency_id = str(dependency_id).strip()
                if not dependency_id:
                    return None

                dependency = self.tasks.get(dependency_id)

                if dependency is None:
                    blocking.append(dependency_id)
                    continue

                if dependency.get("status") != self.COMPLETED:
                    blocking.append(dependency_id)

            return blocking

    def dependencies_satisfied(
        self,
        task_id
    ):
        """
        Return True when every dependency is COMPLETED.
        """

        blocking = self.get_blocking_dependencies(
            task_id
        )

        if blocking is None:
            return False

        return len(
            blocking
        ) == 0


    def dependency_status(self, task_id):
        """Return dependency state, or None when it cannot be trusted."""

        task_id = str(task_id).strip()
        task = self.get_task(task_id)

        if task is None:
            return None

        dependencies = task.get("dependencies", [])
        if not isinstance(dependencies, list):
            return None

        blocking = self.get_blocking_dependencies(task_id)
        failed = self.get_failed_dependencies(task_id)

        if blocking is None or failed is None:
            return None

        return {
            "task_id": task_id,
            "dependencies": list(dependencies),
            "blocking": list(blocking),
            "failed": list(failed),
            "satisfied": len(blocking) == 0 and len(failed) == 0,
        }

    def create_task_chain(
        self,
        chain_name,
        tasks
    ):
        """
        Create an ordered chain of tasks.

        Each task specification must be a dictionary:

        {
            "name": "...",
            "goal": "...",
            "steps": [...],
            "workflow_name": "..."
        }

        Tasks are linked sequentially:

            Task 0
            ↓
            Task 1
            ↓
            Task 2

        Returns a dictionary containing the chain ID
        and created tasks.
        """

        chain_name = str(
            chain_name
        ).strip()

        if not chain_name:
            return None

        if not isinstance(
            tasks,
            list
        ):

            return None

        if not tasks:
            return None

        chain_id = str(
            uuid.uuid4()
        )

        created_tasks = []

        # ========================================
        # CREATE TASKS
        # ========================================

        for index, specification in enumerate(
            tasks
        ):

            if not isinstance(
                specification,
                dict
            ):

                # Roll back already-created tasks

                for created in created_tasks:

                    self.delete_task(
                        created["task_id"]
                    )

                return None

            task_name = specification.get(
                "name",
                f"{chain_name} step {index + 1}"
            )

            goal = specification.get(
                "goal",
                task_name
            )

            steps = specification.get(
                "steps",
                []
            )

            workflow_name = specification.get(
                "workflow_name"
            )

            task = self.create_task(
                name=task_name,
                goal=goal,
                steps=steps,
                workflow_name=workflow_name
            )

            if task is None:

                for created in created_tasks:

                    self.delete_task(
                        created["task_id"]
                    )

                return None

            updated = self.update_task(
                task["task_id"],
                chain_id=chain_id,
                chain_order=index
            )

            if updated is None:

                for created in created_tasks:

                    self.delete_task(
                        created["task_id"]
                    )

                return None

            created_tasks.append(
                updated
            )

        # ========================================
        # CREATE SEQUENTIAL DEPENDENCIES
        # ========================================

        for index in range(
            1,
            len(created_tasks)
        ):

            current_task = created_tasks[
                index
            ]

            previous_task = created_tasks[
                index - 1
            ]

            dependency = self.add_dependency(
                current_task["task_id"],
                previous_task["task_id"]
            )

            if dependency is None:

                for created in created_tasks:

                    self.delete_task(
                        created["task_id"]
                    )

                return None

            created_tasks[index] = dependency

        print(
            "[TASK MANAGER] Task chain created:",
            chain_name,
            "| Chain ID:",
            chain_id,
            "| Tasks:",
            len(created_tasks)
        )

        return {
            "chain_id":
                chain_id,

            "name":
                chain_name,

            "tasks":
                created_tasks
        }
    def get_task_chain(
        self,
        chain_id
    ):
        """
        Return all tasks belonging to a chain,
        ordered by chain_order.
        """

        chain_id = str(
            chain_id
        ).strip()

        if not chain_id:
            return []

        with self.lock:

            chain_tasks = [
                dict(task)
                for task in self.tasks.values()
                if task.get(
                    "chain_id"
                ) == chain_id
            ]

        chain_tasks.sort(
            key=lambda task: int(
                task.get(
                    "chain_order",
                    0
                )
            )
        )

        return chain_tasks
    
    def get_chain_status(
        self,
        chain_id
    ):
        """
        Return the overall status of a task chain.
        """

        chain_id = str(
            chain_id
        ).strip()

        tasks = self.get_task_chain(
            chain_id
        )

        if not tasks:
            return None

        completed = 0
        failed = 0
        cancelled = 0
        running = 0
        waiting = 0
        pending = 0

        for task in tasks:

            status = task.get(
                "status"
            )

            if status == self.COMPLETED:
                completed += 1

            elif status == self.FAILED:
                failed += 1

            elif status == self.CANCELLED:
                cancelled += 1

            elif status == self.RUNNING:
                running += 1

            elif status == self.WAITING:
                waiting += 1

            elif status == self.PENDING:
                pending += 1

        if failed > 0:

            overall_status = self.FAILED

        elif cancelled > 0:

            overall_status = self.CANCELLED

        elif completed == len(tasks):

            overall_status = self.COMPLETED

        elif running > 0:

            overall_status = self.RUNNING

        elif waiting > 0:

            overall_status = self.WAITING

        else:

            overall_status = self.PENDING

        return {
            "chain_id":
                chain_id,

            "total":
                len(tasks),

            "completed":
                completed,

            "failed":
                failed,

            "cancelled":
                cancelled,

            "running":
                running,

            "waiting":
                waiting,

            "pending":
                pending,

            "status":
                overall_status,
        }


    def get_next_chain_task(
        self,
        chain_id
    ):
        """
        Return the earliest chain task that is ready
        to execute.

        A task is ready when:
        - it is PENDING or INTERUPTED
        - all dependencies are COMPLETED
        """

        chain_id = str(
            chain_id
        ).strip()

        tasks = self.get_task_chain(
            chain_id
        )

        if not tasks:
            return None

        for task in tasks:

            if task.get(
                "status"
            ) != self.PENDING:

                continue

            if not self.dependencies_satisfied(
                task["task_id"]
            ):

                continue

            return dict(
                task
            )

        return None  
                
    def get_failed_dependencies(self, task_id):
        """Return failed dependencies; None means an invalid relationship."""

        task_id = str(task_id).strip()

        with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                return None

            dependencies = task.get("dependencies", [])
            if not isinstance(dependencies, list):
                return None

            failed_dependencies = []

            for dependency_id in dependencies:
                dependency_id = str(dependency_id).strip()
                if not dependency_id:
                    return None

                dependency = self.tasks.get(dependency_id)
                if dependency is None:
                    return None

                if dependency.get("status") in {
                    self.FAILED,
                    self.CANCELLED,
                }:
                    failed_dependencies.append(dependency_id)

            return failed_dependencies

    def dependencies_failed(
        self,
        task_id
    ):
        """
        Return True when at least one dependency
        has FAILED or been CANCELLED.
        """

        failed = self.get_failed_dependencies(
            task_id
        )

        if failed is None:
            return False

        return len(
            failed
        ) > 0
        
    def get_ready_dependents(
        self,
        completed_task_id
    ):
        """
        Return PENDING or WAITING tasks whose dependencies are now
        completely satisfied because completed_task_id finished.
        """

        completed_task_id = str(
            completed_task_id
        ).strip()

        with self.lock:

            completed_task = self.tasks.get(
                completed_task_id
            )

            if completed_task is None:
                return []

            if completed_task.get(
                "status"
            ) != self.COMPLETED:

                return []

            ready_tasks = []

            for task in self.tasks.values():

                status = task.get(
                    "status"
                )

                if status not in {
                    self.PENDING,
                    self.WAITING
                }:
                    continue

                dependencies = task.get(
                    "dependencies",
                    []
                )

                if not isinstance(
                    dependencies,
                    list
                ):
                    dependencies = []

                dependency_ids = [
                    str(
                        dependency
                    ).strip()
                    for dependency in dependencies
                ]

                if completed_task_id not in dependency_ids:
                    continue

                blocking = (
                    self.get_blocking_dependencies(
                        task.get(
                            "task_id"
                        )
                    )
                )

                if blocking == []:

                    ready_tasks.append(
                        dict(task)
                    )

            return ready_tasks
    # ========================================
    # UNBIND WORKFLOW
    # ========================================

    def unbind_workflow(
        self,
        task_id
    ):

        with self.lock:

            task = self.tasks.get(
                str(task_id).strip()
            )

            if task is None:
                return None

            task[
                "workflow_name"
            ] = None

            if not self._save_tasks():
                return None

            return dict(task)

    # ========================================
    # STATE TRANSITION
    # ========================================

    def _transition(
        self,
        task_id,
        new_state,
        **updates
    ):

        task_id = str(
            task_id
        ).strip()

        if new_state not in self.VALID_STATES:
            return None

        with self.lock:

            task = self.tasks.get(
                task_id
            )

            if task is None:
                return None

            current = task.get(
                "status"
            )

            if new_state not in (
                self.VALID_TRANSITIONS.get(
                    current,
                    set()
                )
            ):

                print(
                    "[TASK MANAGER] Invalid transition:",
                    f"{current} -> {new_state}",
                    "| Task:",
                    task_id
                )

                return None

            task[
                "status"
            ] = new_state

            for key, value in updates.items():

                if key in task:
                    task[key] = value

            if not self._save_tasks():
                return None

            print(
                "[TASK MANAGER]",
                current,
                "->",
                new_state,
                "| Task:",
                task_id
            )

            return dict(task)

    # ========================================
    # UPDATE TASK
    # ========================================

    def update_task(
        self,
        task_id,
        **updates
    ):

        with self.lock:

            task = self.tasks.get(
                str(task_id).strip()
            )

            if task is None:
                return None

            if (
                "status" in updates
                and
                updates["status"]
                != task.get("status")
            ):

                return self._transition(
                    task_id,
                    updates.pop("status"),
                    **updates
                )

            for key, value in updates.items():

                if key in task:
                    task[key] = value

            if not self._save_tasks():
                return None

            return dict(task)

    # ========================================
    # START TASK
    # ========================================
    def start_task(
        self,
        task_id
    ):
        """
        Start a task only when all dependencies
        have completed.

        Returns:
            task dictionary when started
            None when the task cannot be started
        """

        task = self.get_task(
            task_id
        )

        if task is None:
            return None

        blocking = self.get_blocking_dependencies(
            task_id
        )

        if blocking is None:
            return None

        if blocking:

            print(
                "[TASK MANAGER] Task blocked by dependencies:",
                task_id,
                "| Blocking:",
                blocking
            )

            return None

        return self._transition(
            task_id,
            self.RUNNING,
            started_at=(
                task.get("started_at")
                or
                datetime.now().isoformat()
            ),
            error=None
        )

    # ========================================
    # COMPLETE TASK
    # ========================================

    def complete_task(
        self,
        task_id
    ):

        return self._transition(
            task_id,
            self.COMPLETED,
            completed_at=datetime.now().isoformat(),
            error=None
        )

    # ========================================
    # FAIL TASK
    # ========================================
    def fail_task(
        self,
        task_id,
        error,
        failure_type=None,
        step=None
    ):
        """
        Mark a task as FAILED and record the failure
        in persistent failure history.
        """

        task_id = str(
            task_id
        ).strip()

        error = str(
            error
        ).strip()

        if not error:
            error = "Unknown workflow failure."

        with self.lock:

            task = self.tasks.get(
                task_id
            )

            if task is None:
                return None

            current_step = (
                int(step)
                if step is not None
                else int(
                    task.get(
                        "current_step",
                        0
                    )
                )
            )

            history = task.get(
                "failure_history"
            )

            if not isinstance(
                history,
                list
            ):
                history = []

            failure_record = {

                "attempt":
                    int(
                        task.get(
                            "retry_count",
                            0
                        )
                    ) + 1,

                "step":
                    current_step,

                "error":
                    error,

                "failure_type":
                    (
                        str(
                            failure_type
                        ).upper()
                        if failure_type
                        else None
                    ),

                "timestamp":
                    datetime.now().isoformat(),
            }

            history.append(
                failure_record
            )

            task[
                "failure_history"
            ] = history

            # ----------------------------------------
            # Transition to FAILED
            # ----------------------------------------

            current_status = task.get(
                "status"
            )

            if (
                self.FAILED
                not in self.VALID_STATES
            ):
                return None

            if (
                self.FAILED
                not in self.VALID_TRANSITIONS.get(
                    current_status,
                    set()
                )
            ):
                print(
                    "[TASK MANAGER] Invalid transition:",
                    f"{current_status} -> FAILED",
                    "| Task:",
                    task_id
                )
                return None

            task[
                "status"
            ] = self.FAILED

            task[
                "error"
            ] = error

            if not self._save_tasks():
                return None

            print(
                "[TASK MANAGER] Failure recorded:",
                task_id,
                "| Attempt:",
                failure_record["attempt"],
                "| Step:",
                current_step,
                "| Type:",
                failure_record["failure_type"],
                "| Error:",
                error
            )

            print(
                "[TASK MANAGER]",
                current_status,
                "-> FAILED",
                "| Task:",
                task_id
            )

            return dict(
                task
            )
            
    def has_repeated_failure(
        self,
        task_id,
        error,
        step=None,
        minimum_repetitions=2
    ):
        """
        Determine whether the same failure has occurred repeatedly
        at the same workflow step.

        Returns True when the latest failure has occurred at least
        minimum_repetitions times with the same error and step.
        """

        task_id = str(
            task_id
        ).strip()

        error = str(
            error
        ).strip()

        if not error:
            return False

        try:
            minimum_repetitions = int(
                minimum_repetitions
            )
        except (
            ValueError,
            TypeError
        ):
            minimum_repetitions = 2

        if minimum_repetitions < 2:
            minimum_repetitions = 2

        with self.lock:

            task = self.tasks.get(
                task_id
            )

            if task is None:
                return False

            history = task.get(
                "failure_history",
                []
            )

            if not isinstance(
                history,
                list
            ):
                return False

            target_step = (
                int(step)
                if step is not None
                else int(
                    task.get(
                        "current_step",
                        0
                    )
                )
            )

            matching_failures = 0

            for record in history:

                if not isinstance(
                    record,
                    dict
                ):
                    continue

                record_error = str(
                    record.get(
                        "error",
                        ""
                    )
                ).strip()

                try:
                    record_step = int(
                        record.get(
                            "step",
                            0
                        )
                    )
                except (
                    ValueError,
                    TypeError
                ):
                    record_step = 0

                if (
                    record_error == error
                    and
                    record_step == target_step
                ):
                    matching_failures += 1

            repeated = (
                matching_failures
                >=
                minimum_repetitions
            )

            print(
                "[TASK MANAGER] Repeated failure check:",
                task_id,
                "| Step:",
                target_step,
                "| Matches:",
                matching_failures,
                "| Required:",
                minimum_repetitions,
                "| Repeated:",
                repeated
            )

            return repeated

    # ========================================
    # PAUSE TASK
    # ========================================

    def pause_task(
        self,
        task_id
    ):

        return self._transition(
            task_id,
            self.PAUSED
        )

    # ========================================
    # RESUME TASK
    # ========================================



    def _build_resume_approval_payload_locked(
        self,
        task_id,
        completed_task_id,
    ):
        """Build the exact approval payload from current persisted task state."""
        task = self.tasks.get(task_id)

        if not isinstance(task, dict):
            return None

        if task.get("status") != self.WAITING:
            return None

        workflow_name = task.get("workflow_name")
        if not isinstance(workflow_name, str) or not workflow_name.strip():
            return None

        dependencies = task.get("dependencies")
        if not isinstance(dependencies, list) or not dependencies:
            return None

        dependency_ids = []
        for dependency_id in dependencies:
            if not isinstance(dependency_id, str) or not dependency_id.strip():
                return None
            dependency_ids.append(dependency_id.strip())

        if completed_task_id not in dependency_ids:
            return None

        for dependency_id in dependency_ids:
            dependency = self.tasks.get(dependency_id)
            if not isinstance(dependency, dict):
                return None
            if dependency.get("status") != self.COMPLETED:
                return None

        steps = task.get("steps")
        if not isinstance(steps, list) or not steps or len(steps) > 100:
            return None

        for action in steps:
            if (
                not isinstance(action, list)
                or not action
                or not isinstance(action[0], str)
                or not action[0].strip()
            ):
                return None

        current_step = task.get("current_step")
        if type(current_step) is not int:
            return None
        if current_step < 0 or current_step >= len(steps):
            return None

        try:
            workflow_snapshot = copy.deepcopy(steps)
            remaining_actions = copy.deepcopy(steps[current_step:])

            payload = [
                {
                    "intent": "resume_workflow_task",
                    "task_id": task_id,
                    "workflow_name": workflow_name,
                    "dependencies": list(dependency_ids),
                    "completed_task_id": completed_task_id,
                    "current_step": current_step,
                },
                {"workflow_snapshot": workflow_snapshot},
                {"remaining_actions": remaining_actions},
            ]

            canonical = json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )

            if len(canonical.encode("utf-8")) > 65536:
                return None

        except (TypeError, ValueError):
            return None

        return payload

    def get_resume_approval_payload(
        self,
        task_id,
        completed_task_id,
    ):
        """Return a read-only, task-bound approval payload for a WAITING task."""
        if not isinstance(task_id, str) or not task_id.strip():
            return None
        if not isinstance(completed_task_id, str) or not completed_task_id.strip():
            return None

        task_id = task_id.strip()
        completed_task_id = completed_task_id.strip()

        with self.lock:
            return self._build_resume_approval_payload_locked(
                task_id,
                completed_task_id,
            )

    def resume_waiting_task_with_approval(
        self,
        task_id,
        completed_task_id,
        approval_token,
        approval_manager,
    ):
        """
        Consume fresh task-bound approval and atomically transition WAITING
        to RUNNING. No state change occurs if validation or persistence fails.
        """
        if not isinstance(task_id, str) or not task_id.strip():
            return None
        if not isinstance(completed_task_id, str) or not completed_task_id.strip():
            return None
        if not callable(getattr(approval_manager, "consume", None)):
            return None
        if not isinstance(approval_token, str) or not approval_token:
            return None

        task_id = task_id.strip()
        completed_task_id = completed_task_id.strip()

        with self.lock:
            payload = self._build_resume_approval_payload_locked(
                task_id,
                completed_task_id,
            )
            if payload is None:
                # Burn any outstanding token when the task is no longer
                # eligible. It must not become reusable if state later changes.
                try:
                    approval_manager.consume(
                        approval_token,
                        {
                            "intent": "invalidate_unusable_resume_approval",
                            "task_id": task_id,
                            "completed_task_id": completed_task_id,
                        },
                    )
                except Exception as exc:
                    print(
                        "[TASK MANAGER] Could not invalidate stale approval:",
                        repr(exc),
                    )
                return None

            try:
                approved = approval_manager.consume(
                    approval_token,
                    payload,
                )
            except Exception as exc:
                print("[TASK MANAGER] Resume approval validation failed:", repr(exc))
                return None

            if approved is not True:
                print("[SECURITY] Task recovery approval denied:", task_id)
                return None

            task = self.tasks.get(task_id)
            if not isinstance(task, dict):
                return None

            original_task = dict(task)

            task["status"] = self.RUNNING
            task["started_at"] = (
                task.get("started_at") or datetime.now().isoformat()
            )
            task["error"] = None

            if not self._save_tasks():
                task.clear()
                task.update(original_task)
                print(
                    "[TASK MANAGER] Resume transition rolled back after save failure:",
                    task_id,
                )
                return None

            print(
                "[TASK MANAGER] WAITING -> RUNNING",
                "| Approved recovery:",
                task_id,
            )
            return dict(task)
    def resume_task(
        self,
        task_id
    ):

        return self._transition(
            task_id,
            self.RUNNING,
            error=None
        )

    # ========================================
    # CANCEL TASK
    # ========================================

    def cancel_task(
        self,
        task_id
    ):

        return self._transition(
            task_id,
            self.CANCELLED
        )

    # ========================================
    # WAIT TASK
    # ========================================

    def wait_task(
        self,
        task_id
    ):

        return self._transition(
            task_id,
            self.WAITING
        )
        
    def wait_for_dependencies(
        self,
        task_id
    ):
        """
        Move a PENDING task into WAITING because one or more
        dependencies have not completed yet.
        """

        task_id = str(
            task_id
        ).strip()

        with self.lock:

            task = self.tasks.get(
                task_id
            )

            if task is None:
                return None

            if task.get(
                "status"
            ) != self.PENDING:

                print(
                    "[TASK MANAGER] Cannot wait for dependencies:",
                    task_id,
                    "| Status:",
                    task.get("status")
                )

                return None

            return self._transition(
                task_id,
                self.WAITING
            )

    # ========================================
    # SET CURRENT STEP
    # ========================================

    def set_current_step(
        self,
        task_id,
        step_index
    ):

        try:

            step_index = int(
                step_index
            )

        except (
            ValueError,
            TypeError
        ):

            return None

        if step_index < 0:
            return None

        with self.lock:

            task = self.tasks.get(
                str(task_id).strip()
            )

            if task is None:
                return None

            task[
                "current_step"
            ] = step_index

            if not self._save_tasks():
                return None

            return dict(task)

    # ========================================
    # GET CURRENT STEP
    # ========================================

    def get_current_step(
        self,
        task_id
    ):

        task = self.get_task(
            task_id
        )

        if task is None:
            return None

        return task.get(
            "current_step",
            0
        )

    # ========================================
    # INCREMENT RETRY
    # ========================================

    def increment_retry(
        self,
        task_id
    ):

        with self.lock:

            task = self.tasks.get(
                str(task_id).strip()
            )

            if task is None:
                return None

            task[
                "retry_count"
            ] = int(
                task.get(
                    "retry_count",
                    0
                )
            ) + 1

            if not self._save_tasks():
                return None

            print(
                "[TASK MANAGER] Retry count:",
                task_id,
                task["retry_count"]
            )

            return dict(task)

    # ========================================
    # PREPARE RETRY
    # ========================================

    def prepare_retry(
        self,
        task_id,
        error=None
    ):
        """
        Prepare a FAILED task for another
        execution attempt.

        Phase 17.3:
        - increments retry_count
        - preserves current_step
        - stores the previous error
        - leaves the task in FAILED state

        WorkflowManager will transition the
        task back to RUNNING when execution
        actually begins.
        """

        task_id = str(
            task_id
        ).strip()

        with self.lock:

            task = self.tasks.get(
                task_id
            )

            if task is None:

                print(
                    "[TASK MANAGER] Retry failed: "
                    "task not found:",
                    task_id
                )

                return None

            if task.get(
                "status"
            ) != self.FAILED:

                print(
                    "[TASK MANAGER] Retry failed: "
                    "task is not FAILED:",
                    task_id,
                    "| Status:",
                    task.get("status")
                )

                return None

            task[
                "retry_count"
            ] = int(
                task.get(
                    "retry_count",
                    0
                )
            ) + 1

            if error is not None:

                task[
                    "error"
                ] = str(error)

            if not self._save_tasks():
                return None

            print(
                "[TASK MANAGER] Retry prepared:",
                task_id,
                "| Attempt:",
                task["retry_count"],
                "| Step:",
                task.get(
                    "current_step",
                    0
                )
            )

            return dict(task)

    # ========================================
    # LIST TASKS
    # ========================================

    def list_tasks(
        self,
        status=None
    ):

        with self.lock:

            if (
                status is not None
                and
                status not in self.VALID_STATES
            ):

                return []

            return [
                dict(task)
                for task in self.tasks.values()
                if (
                    status is None
                    or
                    task.get("status")
                    == status
                )
            ]

    # ========================================
    # GET ACTIVE TASK
    # ========================================

    def get_active_task(self):

        with self.lock:

            for task in self.tasks.values():

                if task.get(
                    "status"
                ) in {
                    self.RUNNING,
                    self.PAUSED,
                    self.WAITING,
                }:

                    return dict(task)

        return None

    # ========================================
    # DELETE TASK
    # ========================================

    def delete_task(
        self,
        task_id
    ):

        with self.lock:

            task_id = str(
                task_id
            ).strip()

            if task_id not in self.tasks:
                return False

            del self.tasks[
                task_id
            ]

            if not self._save_tasks():
                return False

            print(
                "[TASK MANAGER] Task deleted:",
                task_id
            )

            return True

    # ========================================
    # TASK SUMMARY
    # ========================================

    def summary(self):

        with self.lock:

            counts = {
                state: 0
                for state in self.VALID_STATES
            }

            for task in self.tasks.values():

                status = task.get(
                    "status"
                )

                if status in counts:

                    counts[
                        status
                    ] += 1

            return {
                "total":
                    len(self.tasks),

                "states":
                    counts,
            }


# ========================================
# GLOBAL TASK MANAGER
# ========================================

task_manager = TaskManager()
