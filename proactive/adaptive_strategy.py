class AdaptiveStrategy:

    REINFORCE="REINFORCE"
    MAINTAIN="MAINTAIN"
    REDUCE="REDUCE"
    INSUFFICIENT="INSUFFICIENT"

    def __init__(self,strategy=None,success_rate=0.0,evidence_count=0,learning="INSUFFICIENT",confidence="LOW"):
        self.strategy=strategy if isinstance(strategy,str) else None
        self.success_rate=self._clamp(success_rate)
        self.evidence_count=evidence_count if isinstance(evidence_count,int) and not isinstance(evidence_count,bool) and evidence_count>=0 else 0
        self.learning=learning if learning in {self.REINFORCE,self.MAINTAIN,self.REDUCE,self.INSUFFICIENT} else self.INSUFFICIENT
        self.confidence=confidence if confidence in {"HIGH","MEDIUM","LOW"} else "LOW"

    @classmethod
    def create(cls,strategy,success_rate=0.0,evidence_count=0,learning="INSUFFICIENT",confidence="LOW"):
        if not isinstance(strategy,str) or not strategy.strip():
            return None
        if not isinstance(success_rate,(int,float)) or isinstance(success_rate,bool) or success_rate<0.0 or success_rate>1.0:
            return None
        if not isinstance(evidence_count,int) or isinstance(evidence_count,bool) or evidence_count<0:
            return None
        if learning not in {cls.REINFORCE,cls.MAINTAIN,cls.REDUCE,cls.INSUFFICIENT}:
            return None
        if confidence not in {"HIGH","MEDIUM","LOW"}:
            return None
        return cls(strategy,success_rate,evidence_count,learning,confidence)

    @staticmethod
    def _clamp(value):
        return max(0.0,min(1.0,float(value))) if isinstance(value,(int,float)) and not isinstance(value,bool) else 0.0

    def to_dict(self):
        return {
            "strategy":self.strategy,
            "success_rate":self.success_rate,
            "evidence_count":self.evidence_count,
            "learning":self.learning,
            "confidence":self.confidence,
        }

    def is_valid(self):
        return isinstance(self.strategy,str) and self.learning in {self.REINFORCE,self.MAINTAIN,self.REDUCE,self.INSUFFICIENT}

    @classmethod
    def from_effectiveness(cls,effectiveness):
        if isinstance(effectiveness,dict):
            strategy=effectiveness.get("strategy")
            rate=effectiveness.get("success_rate",0.0)
            evidence=effectiveness.get("total",0)
        elif hasattr(effectiveness,"strategy"):
            strategy=effectiveness.strategy
            rate=effectiveness.success_rate()
            evidence=effectiveness.total
        else:
            return None
        if not isinstance(strategy,str) or not strategy.strip():
            return None
        if not isinstance(rate,(int,float)) or isinstance(rate,bool) or rate<0.0 or rate>1.0:
            return None
        if not isinstance(evidence,int) or isinstance(evidence,bool) or evidence<0:
            return None
        if evidence < 2:
            learning=cls.INSUFFICIENT
            confidence="LOW"
        elif rate >= 0.80:
            learning=cls.REINFORCE
            confidence="HIGH" if evidence>=4 else "MEDIUM"
        elif rate >= 0.50:
            learning=cls.MAINTAIN
            confidence="HIGH" if evidence>=4 else "MEDIUM"
        else:
            learning=cls.REDUCE
            confidence="HIGH" if evidence>=4 else "MEDIUM"
        return cls.create(strategy,rate,evidence,learning,confidence)

    @classmethod
    def validate(cls,learning):
        if isinstance(learning,cls):
            data=learning.to_dict()
        elif isinstance(learning,dict):
            data=learning
        else:
            return False
        if not isinstance(data.get("strategy"),str) or not data.get("strategy").strip():
            return False
        rate=data.get("success_rate")
        evidence=data.get("evidence_count")
        if not isinstance(rate,(int,float)) or isinstance(rate,bool) or rate<0.0 or rate>1.0:
            return False
        if not isinstance(evidence,int) or isinstance(evidence,bool) or evidence<0:
            return False
        if data.get("learning") not in {cls.REINFORCE,cls.MAINTAIN,cls.REDUCE,cls.INSUFFICIENT}:
            return False
        if data.get("confidence") not in {"HIGH","MEDIUM","LOW"}:
            return False
        return True
