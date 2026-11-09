class ReasoningStrategy:

    DIRECT="DIRECT"
    STEP_BY_STEP="STEP_BY_STEP"
    VERIFY_FIRST="VERIFY_FIRST"
    ASK_CLARIFICATION="ASK_CLARIFICATION"
    CAUTIOUS="CAUTIOUS"

    TYPES={DIRECT,STEP_BY_STEP,VERIFY_FIRST,ASK_CLARIFICATION,CAUTIOUS}

    def __init__(self,name=None,description=None,score=0.0):
        self.name=name if name in self.TYPES else None
        self.description=description if isinstance(description,str) else None
        self.score=self._clamp(score)

    @classmethod
    def create(cls,name,description=None,score=0.0):
        if name not in cls.TYPES:
            return None
        if description is not None and not isinstance(description,str):
            return None
        if not isinstance(score,(int,float)) or isinstance(score,bool):
            return None
        if score < 0.0 or score > 1.0:
            return None
        return cls(name,description,score)

    @staticmethod
    def _clamp(value):
        if not isinstance(value,(int,float)) or isinstance(value,bool):
            return 0.0
        return max(0.0,min(1.0,float(value)))

    def to_dict(self):
        return {
            "name":self.name,
            "description":self.description,
            "score":self.score,
        }

    def is_valid(self):
        return self.name in self.TYPES

    @classmethod
    def select(cls,context):
        if not isinstance(context,dict):
            return None
        if context.get("safety_concern") is True or context.get("risk_level") in {"HIGH","CRITICAL"}:
            return cls.CAUTIOUS
        if context.get("verify_required") is True or context.get("needs_verification") is True:
            return cls.VERIFY_FIRST
        if context.get("missing_information") is True or context.get("needs_clarification") is True:
            return cls.ASK_CLARIFICATION
        if context.get("complex") is True or context.get("multi_step") is True:
            return cls.STEP_BY_STEP
        return cls.DIRECT

    @classmethod
    def score(cls,name,context):
        if name not in cls.TYPES or not isinstance(context,dict):
            return 0.0
        if name == cls.CAUTIOUS:
            return 1.0 if context.get("safety_concern") is True or context.get("risk_level") in {"HIGH","CRITICAL"} else 0.0
        if name == cls.VERIFY_FIRST:
            return 1.0 if context.get("verify_required") is True or context.get("needs_verification") is True else 0.0
        if name == cls.ASK_CLARIFICATION:
            return 1.0 if context.get("missing_information") is True or context.get("needs_clarification") is True else 0.0
        if name == cls.STEP_BY_STEP:
            return 1.0 if context.get("complex") is True or context.get("multi_step") is True else 0.0
        special_signal=context.get("safety_concern") is True or context.get("risk_level") in {"HIGH","CRITICAL"} or context.get("verify_required") is True or context.get("needs_verification") is True or context.get("missing_information") is True or context.get("needs_clarification") is True or context.get("complex") is True or context.get("multi_step") is True
        return 0.0 if special_signal else 1.0

    @classmethod
    def best(cls,context):
        if not isinstance(context,dict):
            return None
        selected=cls.select(context)
        if selected is None:
            return None
        best_score=cls.score(selected,context)
        for name in cls.TYPES:
            score=cls.score(name,context)
            if score > best_score:
                selected=name
                best_score=score
        return selected

    @classmethod
    def profile(cls,context):
        if not isinstance(context,dict):
            return None
        scores={name:cls.score(name,context) for name in cls.TYPES}
        best=cls.best(context)
        return {"scores":scores,"selected":best}

    @classmethod
    def validate_profile(cls,profile):
        if not isinstance(profile,dict):
            return False
        scores=profile.get("scores")
        selected=profile.get("selected")
        if not isinstance(scores,dict):
            return False
        if selected not in cls.TYPES:
            return False
        for name,score in scores.items():
            if name not in cls.TYPES:
                return False
            if not isinstance(score,(int,float)) or isinstance(score,bool):
                return False
            if score < 0.0 or score > 1.0:
                return False
        return True

    @staticmethod
    def learning_adjustment(strategy, learning):
        if not isinstance(strategy,str) or not isinstance(learning,dict):
            return 0.0
        if learning.get("strategy") != strategy:
            return 0.0
        if learning.get("learning") == "REINFORCE" and learning.get("confidence") in {"HIGH","MEDIUM"}:
            return 0.10
        if learning.get("learning") == "REDUCE" and learning.get("confidence") in {"HIGH","MEDIUM"}:
            return -0.10
        return 0.0

    @classmethod
    def learned_score(cls,name,context,learning=None):
        base=cls.score(name,context)
        adjustment=cls.learning_adjustment(name,learning)
        return max(0.0,min(1.0,base+adjustment))

    @staticmethod
    def learning_adjustment(strategy, learning):
        if not isinstance(strategy,str) or not isinstance(learning,dict):
            return 0.0
        if learning.get("strategy") != strategy:
            return 0.0
        if learning.get("learning") == "REINFORCE" and learning.get("confidence") in {"HIGH","MEDIUM"}:
            return 0.10
        if learning.get("learning") == "REDUCE" and learning.get("confidence") in {"HIGH","MEDIUM"}:
            return -0.10
        return 0.0

    @classmethod
    def learned_score(cls,name,context,learning=None):
        if not isinstance(context,dict):
            return 0.0
        base=cls.score(name,context)
        adjustment=cls.learning_adjustment(name,learning)
        return max(0.0,min(1.0,base+adjustment))

    @classmethod
    def learned_profile(cls,context,learning=None):
        if not isinstance(context,dict):
            return None
        profile={}
        for name in cls.TYPES:
            base=cls.score(name,context)
            adjustment=cls.learning_adjustment(name,learning)
            learned=max(0.0,min(1.0,base+adjustment))
            profile[name]={"base_score":base,"adjustment":adjustment,"learned_score":learned}
        selected=max(profile,key=lambda name:profile[name]["learned_score"]) if profile else None
        return {"strategies":profile,"selected":selected}

    @classmethod
    def validate_learned_profile(cls,profile):
        if not isinstance(profile,dict):
            return False
        strategies=profile.get("strategies")
        selected=profile.get("selected")
        if not isinstance(strategies,dict):
            return False
        if selected not in cls.TYPES:
            return False
        for name,data in strategies.items():
            if name not in cls.TYPES or not isinstance(data,dict):
                return False
            for key in ("base_score","adjustment","learned_score"):
                value=data.get(key)
                if not isinstance(value,(int,float)) or isinstance(value,bool):
                    return False
                if key != "adjustment" and (value < 0.0 or value > 1.0):
                    return False
                if key == "adjustment" and (value < -1.0 or value > 1.0):
                    return False
        return True
