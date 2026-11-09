from proactive.reasoning_quality import ReasoningQuality
from proactive.decision_quality import DecisionQuality
from proactive.reasoning_feedback import ReasoningFeedback
from proactive.self_correction import SelfCorrection
from proactive.improvement_safety import ImprovementSafety
from proactive.meta_memory import MetaMemoryStore
from proactive.cross_session_reasoning import CrossSessionReasoning
from proactive.reasoning_strategy import ReasoningStrategy

class Phase20Integration:

    @classmethod
    def evaluate(cls,reasoning,action,expected,actual):
        rq=ReasoningQuality.from_reasoning(reasoning)
        dq=DecisionQuality.from_outcome(action,expected,actual)
        if rq is None or dq is None:
            return None
        feedback=ReasoningFeedback.from_assessments(rq.to_dict(),dq.to_dict())
        correction=feedback.to_correction(action) if feedback else None
        safety=SelfCorrection.safety_validate(correction) if correction else "NONE"
        boundary=ImprovementSafety.validate(correction.to_dict()) if correction else "NONE"
        return {"reasoning_quality":rq.to_dict(),"decision_quality":dq.to_dict(),"feedback":feedback.to_dict() if feedback else None,"correction":correction.to_dict() if correction else None,"self_safety":safety,"improvement_safety":boundary}

    @classmethod
    def cross_session_context(cls,strategy=None,limit=20,store=None):
        return CrossSessionReasoning.context(strategy,limit,store)

    @classmethod
    def strategy_profile(cls,context,learning=None):
        return ReasoningStrategy.learned_profile(context,learning)

