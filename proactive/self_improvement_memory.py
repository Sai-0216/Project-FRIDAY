from proactive.meta_memory import MetaMemory,MetaMemoryStore

class SelfImprovementMemory:

    @staticmethod
    def create_improvement(target,learning,confidence="MEDIUM",evidence_count=1,details=None):
        return MetaMemory.create("IMPROVEMENT",target,learning,confidence,evidence_count,details=details)

    @staticmethod
    def save(memory,store=None):
        if not isinstance(memory,MetaMemory):
            return False
        from proactive.improvement_safety import ImprovementSafety
        target=memory.details.get("target",memory.strategy) if isinstance(memory.details,dict) else memory.strategy; safety=ImprovementSafety.validate({"action":"CHANGE_STRATEGY","target":target,"confidence":memory.confidence,"evidence":memory.details})
        if safety!="SAFE":
            return False
        store=store or MetaMemoryStore()
        return store.record(memory)
    @staticmethod
    def load_recent(limit=20,store=None):
        store=store or MetaMemoryStore()
        return store.recent(limit)

    @staticmethod
    def validate(memory):
        return isinstance(memory,MetaMemory) and memory.is_valid()
