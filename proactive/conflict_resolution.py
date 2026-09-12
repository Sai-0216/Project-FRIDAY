"""FRIDAY V3 - Phase 23.7 Conflict Resolution."""


class ConflictResolution:

    @staticmethod
    def _safe_results(results):
        return results if isinstance(results, list) else []

    @classmethod
    def group_results(cls, results):
        results = cls._safe_results(results)
        groups = {}

        for item in results:
            if not isinstance(item, dict):
                continue
            if not isinstance(item.get("agent"), dict):
                continue
            if "result" not in item:
                continue

            value = item["result"]
            key = repr(value)
            groups.setdefault(key, {
                "result": value,
                "roles": [],
                "count": 0,
            })
            groups[key]["count"] += 1
            role = item["agent"].get("role")
            if role:
                groups[key]["roles"].append(role)

        return list(groups.values())

    @classmethod
    def detect(cls, results):
        groups = cls.group_results(results)
        conflict = len(groups) > 1

        return {
            "conflict": conflict,
            "group_count": len(groups),
            "groups": groups,
        }

    @classmethod
    def majority(cls, results):
        groups = cls.group_results(results)

        if not groups:
            return None

        winner = max(groups, key=lambda group: group["count"])
        total = sum(group["count"] for group in groups)

        return {
            "result": winner["result"],
            "count": winner["count"],
            "total": total,
            "ratio": winner["count"] / total if total else 0.0,
            "roles": winner["roles"],
        }

    @classmethod
    def resolve(cls, results):
        detection = cls.detect(results)
        majority = cls.majority(results)

        return {
            "conflict": detection["conflict"],
            "groups": detection["groups"],
            "majority": majority,
            "resolved": bool(majority),
        }

    @classmethod
    def validate(cls, resolution):
        if not isinstance(resolution, dict):
            return False
        if not isinstance(resolution.get("conflict"), bool):
            return False
        if not isinstance(resolution.get("groups"), list):
            return False
        if resolution.get("resolved") is not bool(resolution.get("majority")):
            return False
        return True


conflict_resolution = ConflictResolution()
