class LongTermGoals:
    STATUSES = ("active", "completed", "paused", "cancelled")

    def __init__(self):
        self.name = "long_term_goals"

    def create(self, goal, priority="medium", deadline=None):
        if not isinstance(goal, str) or not goal.strip():
            return None
        priority = priority if priority in ("low", "medium", "high", "critical") else "medium"
        return {
            "goal": goal.strip(),
            "priority": priority,
            "deadline": deadline,
            "status": "active",
            "progress": 0.0,
            "milestones": [],
        }

    def update_progress(self, goal, progress):
        if not isinstance(goal, dict):
            return None
        try:
            progress = max(0.0, min(1.0, float(progress)))
        except (TypeError, ValueError):
            return None
        goal["progress"] = progress
        if progress >= 1.0:
            goal["status"] = "completed"
        return goal

    def set_status(self, goal, status):
        if not isinstance(goal, dict) or status not in self.STATUSES:
            return False
        goal["status"] = status
        return True

    def add_milestone(self, goal, milestone):
        if not isinstance(goal, dict) or not isinstance(milestone, str) or not milestone.strip():
            return False
        goal.setdefault("milestones", []).append({
            "id": len(goal["milestones"]) + 1,
            "milestone": milestone.strip(),
            "completed": False,
        })
        return True

    def validate(self, goal):
        if not isinstance(goal, dict):
            return False
        if not isinstance(goal.get("goal"), str) or not goal["goal"]:
            return False
        if goal.get("status") not in self.STATUSES:
            return False
        progress = goal.get("progress")
        if not isinstance(progress, (int, float)) or not 0.0 <= progress <= 1.0:
            return False
        if not isinstance(goal.get("milestones"), list):
            return False
        return True


long_term_goals = LongTermGoals()
