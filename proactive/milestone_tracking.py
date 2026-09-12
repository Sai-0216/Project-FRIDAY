class MilestoneTracking:
    def __init__(self):
        self.name = "milestone_tracking"

    def create(self, milestones):
        if not isinstance(milestones, list):
            return None
        items = []
        for index, milestone in enumerate(milestones, 1):
            if isinstance(milestone, str) and milestone.strip():
                items.append({"id": index, "milestone": milestone.strip(), "completed": False})
        return {"milestones": items, "count": len(items), "completed_count": 0, "progress": 0.0, "status": "active"}

    def complete(self, tracker, milestone_id):
        if not isinstance(tracker, dict):
            return False
        for item in tracker.get("milestones", []):
            if item.get("id") == milestone_id:
                item["completed"] = True
                self.update(tracker)
                return True
        return False

    def update(self, tracker):
        if not isinstance(tracker, dict):
            return None
        milestones = tracker.get("milestones", [])
        completed = sum(1 for item in milestones if item.get("completed"))
        count = len(milestones)
        tracker["count"] = count
        tracker["completed_count"] = completed
        tracker["progress"] = completed / count if count else 0.0
        tracker["status"] = "completed" if count > 0 and completed == count else "active"
        return tracker

    def remaining(self, tracker):
        if not isinstance(tracker, dict):
            return []
        return [item for item in tracker.get("milestones", []) if not item.get("completed")]

    def validate(self, tracker):
        if not isinstance(tracker, dict):
            return False
        milestones = tracker.get("milestones")
        if not isinstance(milestones, list):
            return False
        if tracker.get("count") != len(milestones):
            return False
        completed = sum(1 for item in milestones if item.get("completed"))
        if tracker.get("completed_count") != completed:
            return False
        expected = completed / len(milestones) if milestones else 0.0
        if abs(float(tracker.get("progress", -1)) - expected) > 1e-9:
            return False
        return tracker.get("status") in ("active", "completed")


milestone_tracking = MilestoneTracking()
