"""
FRIDAY V3 - Phase 32.1
Persistent World Model Foundation.

Provides a unified persistent representation of FRIDAY's world
without replacing existing subsystem owners.
"""

import json
import threading
from datetime import datetime
from pathlib import Path


class WorldModel:

    VERSION = "32.1"

    SECTIONS = (
        "user",
        "devices",
        "environment",
        "tasks",
        "goals",
        "events",
        "history",
    )

    def __init__(self, file=None):
        self.file = (
            Path(file)
            if file
            else Path(__file__).resolve().parent / "data" / "world_model.json"
        )

        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()

        self.state = self._default_state()
        self._load()

    def _default_state(self):
        return {
            "version": self.VERSION,
            "updated_at": None,
            "user": {},
            "devices": {},
            "environment": {},
            "tasks": {},
            "goals": {},
            "events": {},
            "history": {},
            "relationships": [],
        }

    def _load(self):
        try:
            if not self.file.exists():
                return False

            with open(self.file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                return False

            with self.lock:
                for section in self.SECTIONS:
                    value = data.get(section)

                    if isinstance(value, dict):
                        self.state[section] = value

                relationships = data.get("relationships")
                if isinstance(relationships, list):
                    self.state["relationships"] = relationships

                updated_at = data.get("updated_at")
                if isinstance(updated_at, str) or updated_at is None:
                    self.state["updated_at"] = updated_at

            return True

        except (OSError, json.JSONDecodeError, ValueError):
            return False

    def _save(self):
        try:
            temporary_file = self.file.with_suffix(".tmp")

            with open(temporary_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.state,
                    f,
                    indent=4,
                    ensure_ascii=False,
                )

            temporary_file.replace(self.file)
            return True

        except (OSError, TypeError, ValueError):
            return False

    def _touch(self):
        self.state["updated_at"] = datetime.now().isoformat()

    def validate(self):
        with self.lock:
            if not isinstance(self.state, dict):
                return False

            if self.state.get("version") != self.VERSION:
                return False

            for section in self.SECTIONS:
                if not isinstance(self.state.get(section), dict):
                    return False

            if not isinstance(self.state.get("relationships"), list):
                return False

            return True

    def snapshot(self):
        with self.lock:
            return json.loads(json.dumps(self.state))

    def get(self, section):
        if section not in self.SECTIONS:
            return None

        with self.lock:
            return json.loads(
                json.dumps(self.state[section])
            )

    def get_user_state(self):
        return self.get("user")

    def set_user_state(self, value):
        return self.update("user", value)

    def update_user_state(self, values):
        if not isinstance(values, dict):
            return False

        with self.lock:
            previous = json.loads(
                json.dumps(self.state["user"])
            )

            updated = json.loads(
                json.dumps(previous)
            )
            updated.update(values)

            self.state["user"] = updated
            self._touch()

            if not self._save():
                self.state["user"] = previous
                return False

            return True

    def get_device_state(self):
        return self.get("devices")

    def set_device_state(self, value):
        return self.update("devices", value)

    def update_device_state(self, values):
        if not isinstance(values, dict):
            return False

        with self.lock:
            previous = json.loads(
                json.dumps(self.state["devices"])
            )

            updated = json.loads(
                json.dumps(previous)
            )
            updated.update(values)

            self.state["devices"] = updated
            self._touch()

            if not self._save():
                self.state["devices"] = previous
                return False

            return True

    def capture_device_state(self):
        try:
            from modules.device_state import device_state

            state = device_state.snapshot()

        except Exception:
            return False

        if not isinstance(state, dict):
            return False

        return self.set_device_state(state)

    def get_environment_state(self):
        return self.get("environment")

    def set_environment_state(self, value):
        return self.update("environment", value)

    def update_environment_state(self, values):
        if not isinstance(values, dict):
            return False

        with self.lock:
            previous = json.loads(
                json.dumps(self.state["environment"])
            )

            updated = json.loads(
                json.dumps(previous)
            )
            updated.update(values)

            self.state["environment"] = updated
            self._touch()

            if not self._save():
                self.state["environment"] = previous
                return False

            return True

    def capture_environment_state(self):
        try:
            from modules.environment import environment

            status = environment.status_details()
            workload = environment.workload_context()
            correlations = environment.correlations()

        except Exception:
            return False

        if not isinstance(status, dict):
            return False

        if not isinstance(workload, dict):
            return False

        if not isinstance(correlations, list):
            return False

        state = {
            "status": status,
            "workload": workload,
            "correlations": correlations,
        }

        return self.set_environment_state(state)

    def get_task_state(self):
        return self.get("tasks")

    def set_task_state(self, value):
        return self.update("tasks", value)

    def update_task_state(self, values):
        if not isinstance(values, dict):
            return False

        with self.lock:
            previous = json.loads(
                json.dumps(self.state["tasks"])
            )

            updated = json.loads(
                json.dumps(previous)
            )
            updated.update(values)

            self.state["tasks"] = updated
            self._touch()

            if not self._save():
                self.state["tasks"] = previous
                return False

            return True

    def capture_task_state(self):
        try:
            from modules.task_manager import task_manager

            items = task_manager.list_tasks()
            active = task_manager.get_active_task()
            summary = task_manager.summary()

        except Exception:
            return False

        if not isinstance(items, list):
            return False

        if active is not None and not isinstance(active, dict):
            return False

        if not isinstance(summary, dict):
            return False

        state = {
            "items": items,
            "active": active,
            "summary": summary,
        }

        return self.set_task_state(state)

    def get_goal_state(self):
        return self.get("goals")

    def set_goal_state(self, value):
        return self.update("goals", value)

    def update_goal_state(self, values):
        if not isinstance(values, dict):
            return False

        with self.lock:
            previous = json.loads(
                json.dumps(self.state["goals"])
            )

            updated = json.loads(
                json.dumps(previous)
            )
            updated.update(values)

            self.state["goals"] = updated
            self._touch()

            if not self._save():
                self.state["goals"] = previous
                return False

            return True

    def get_history_state(self):
        return self.get("history")

    def set_history_state(self, value):
        return self.update("history", value)

    def update_history_state(self, values):
        if not isinstance(values, dict):
            return False

        with self.lock:
            previous = json.loads(
                json.dumps(self.state["history"])
            )

            updated = json.loads(
                json.dumps(previous)
            )
            updated.update(values)

            self.state["history"] = updated
            self._touch()

            if not self._save():
                self.state["history"] = previous
                return False

            return True

    def capture_history_state(self):
        try:
            from proactive.episodic_memory import episodic_memory
            from proactive.session_context import session_context

            episodic_recent = episodic_memory.recent(1)
            latest_session = session_context.latest()

            state = {
                "episodic": {
                    "count": episodic_memory.count(),
                    "latest": (
                        episodic_recent[-1]
                        if episodic_recent
                        else None
                    ),
                },
                "sessions": {
                    "count": session_context.count(),
                    "latest": latest_session,
                },
            }

        except Exception:
            return False

        return self.set_history_state(state)

    def get_event_state(self):
        return self.get("events")

    def set_event_state(self, value):
        return self.update("events", value)

    def update_event_state(self, values):
        if not isinstance(values, dict):
            return False

        with self.lock:
            previous = json.loads(
                json.dumps(self.state["events"])
            )

            updated = json.loads(
                json.dumps(previous)
            )
            updated.update(values)

            self.state["events"] = updated
            self._touch()

            if not self._save():
                self.state["events"] = previous
                return False

            return True

    def record_event(self, event, event_id=None):
        try:
            from proactive.event import Event

            if not isinstance(event, Event):
                return False

            if event_id is None:
                event_id = (
                    f"{event.event_type}:"
                    f"{event.source}:"
                    f"{event.created_at.isoformat()}"
                )

            if not isinstance(event_id, str) or not event_id.strip():
                return False

            record = {
                "event_type": event.event_type,
                "source": event.source,
                "data": json.loads(
                    json.dumps(event.data)
                ),
                "priority": event.priority,
                "created_at": event.created_at.isoformat(),
            }

        except Exception:
            return False

        return self.set_item(
            "events",
            event_id.strip(),
            record,
        )

    def update(self, section, value):
        if section not in self.SECTIONS:
            return False

        if not isinstance(value, dict):
            return False

        with self.lock:
            previous = self.state[section]
            self.state[section] = json.loads(
                json.dumps(value)
            )
            self._touch()

            if not self._save():
                self.state[section] = previous
                return False

            return True

    def set_item(self, section, item_id, value):
        if section not in self.SECTIONS:
            return False

        if not isinstance(item_id, str) or not item_id.strip():
            return False

        if not isinstance(value, dict):
            return False

        with self.lock:
            previous = self.state[section].get(item_id)

            self.state[section][item_id] = json.loads(
                json.dumps(value)
            )
            self._touch()

            if not self._save():
                if previous is None:
                    self.state[section].pop(item_id, None)
                else:
                    self.state[section][item_id] = previous
                return False

            return True

    def remove_item(self, section, item_id):
        if section not in self.SECTIONS:
            return False

        if not isinstance(item_id, str) or not item_id.strip():
            return False

        with self.lock:
            if item_id not in self.state[section]:
                return False

            previous = self.state[section].pop(item_id)
            self._touch()

            if not self._save():
                self.state[section][item_id] = previous
                return False

            return True

    def add_relationship(self, relation):
        if not isinstance(relation, dict):
            return False

        source = relation.get("source")
        target = relation.get("target")
        relation_type = relation.get("type")

        if not all(
            isinstance(value, str) and value.strip()
            for value in (source, target, relation_type)
        ):
            return False

        record = {
            "source": source.strip(),
            "target": target.strip(),
            "type": relation_type.strip(),
        }

        with self.lock:
            if record in self.state["relationships"]:
                return False

            self.state["relationships"].append(record)
            self._touch()

            if not self._save():
                self.state["relationships"].pop()
                return False

            return True

    def relationships(self, source=None, target=None, relation_type=None):
        with self.lock:
            matches = []

            for relation in self.state["relationships"]:
                if source is not None and relation.get("source") != source:
                    continue

                if target is not None and relation.get("target") != target:
                    continue

                if relation_type is not None and relation.get("type") != relation_type:
                    continue

                matches.append(dict(relation))

            return matches

    def clear(self):
        with self.lock:
            previous = self.snapshot()
            self.state = self._default_state()

            if not self._save():
                self.state = previous
                return False

            return True


world_model = WorldModel()
