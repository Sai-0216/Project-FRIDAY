class ReasoningContext:

    def __init__(self, goal=None, project=None, environment=None, session=None):
        self.goal = goal
        self.project = project
        self.environment = environment if isinstance(environment, dict) else {}
        self.session = session if isinstance(session, dict) else {}

    def to_dict(self):
        return {
            "goal": self.goal,
            "project": self.project,
            "environment": self.environment,
            "session": self.session,
        }

    @classmethod
    def create(cls, goal=None, project=None, environment=None, session=None):
        if goal is not None and not isinstance(goal, str):
            return None
        if project is not None and not isinstance(project, str):
            return None
        return cls(goal, project, environment, session)

    @classmethod
    def select_memories(cls, context, limit=5):
        from proactive.semantic_memory import semantic_memory
        if not isinstance(context, ReasoningContext):
            return []
        parts = []
        if isinstance(context.goal, str) and context.goal.strip():
            parts.append(context.goal.strip())
        if isinstance(context.project, str) and context.project.strip():
            parts.append(context.project.strip())
        query = " ".join(parts)
        if not query:
            return []
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return []
        if limit <= 0:
            return []
        return semantic_memory.rank_by_relevance(query, limit)

    @classmethod
    def fuse(cls, context, memories):
        if not isinstance(context, ReasoningContext):
            return None
        if not isinstance(memories, list):
            memories = []
        return {
            "context": context.to_dict(),
            "memories": [dict(memory) for memory in memories if isinstance(memory, dict)],
        }

    @classmethod
    def fuse_conflicts(cls, context, memories):
        from proactive.memory_conflict import MemoryConflict
        if not isinstance(context, ReasoningContext):
            return None
        if not isinstance(memories, list):
            memories = []
        conflicts = []
        for i, existing in enumerate(memories):
            if not isinstance(existing, dict):
                continue
            for incoming in memories[i + 1:]:
                if not isinstance(incoming, dict):
                    continue
                if MemoryConflict.detect_preference_conflict(existing, incoming):
                    resolution = MemoryConflict.resolve(existing, incoming)
                    conflicts.append({
                        "type": MemoryConflict.PREFERENCE_CONFLICT,
                        "existing": dict(existing),
                        "incoming": dict(incoming),
                        "resolution": resolution,
                        "safe": MemoryConflict.is_safe_resolution(existing, incoming, resolution),
                    })
        return {
            "context": context.to_dict(),
            "memories": [dict(memory) for memory in memories if isinstance(memory, dict)],
            "conflicts": conflicts,
        }

    @classmethod
    def fuse_confidence(cls, context, memories, minimum="MEDIUM"):
        from proactive.memory_confidence import MemoryConfidence
        if not isinstance(context, ReasoningContext):
            return None
        if not MemoryConfidence.is_valid(minimum):
            return None
        if not isinstance(memories, list):
            memories = []
        selected = []
        for memory in memories:
            if not isinstance(memory, dict):
                continue
            if MemoryConfidence.at_least(memory.get("confidence"), minimum):
                selected.append(dict(memory))
        return {
            "context": context.to_dict(),
            "memories": selected,
            "minimum_confidence": minimum,
        }
