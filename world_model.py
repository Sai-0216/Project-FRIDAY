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
