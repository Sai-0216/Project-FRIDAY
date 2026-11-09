class StrategyEffectiveness:

    MIN_EVIDENCE=2

    def __init__(self,strategy=None,total=0,successes=0,failures=0):
        self.strategy=strategy if isinstance(strategy,str) else None
        self.total=total if isinstance(total,int) and not isinstance(total,bool) and total>=0 else 0
        self.successes=successes if isinstance(successes,int) and not isinstance(successes,bool) and successes>=0 else 0
        self.failures=failures if isinstance(failures,int) and not isinstance(failures,bool) and failures>=0 else 0

    @classmethod
    def create(cls,strategy,total=0,successes=0,failures=0):
        if not isinstance(strategy,str) or not strategy.strip():
            return None
        if any(not isinstance(value,int) or isinstance(value,bool) or value<0 for value in (total,successes,failures)):
            return None
        if successes+failures>total:
            return None
        return cls(strategy,total,successes,failures)

    def success_rate(self):
        if self.total<=0:
            return 0.0
        return round(self.successes/self.total,4)

    def quality(self):
        rate=self.success_rate()
        if self.total<=0:
            return "UNKNOWN"
        if rate>=0.80:
            return "GOOD"
        if rate>=0.50:
            return "FAIR"
        return "POOR"

    def to_dict(self):
        return {
            "strategy":self.strategy,
            "total":self.total,
            "successes":self.successes,
            "failures":self.failures,
            "success_rate":self.success_rate(),
            "quality":self.quality(),
        }

    @classmethod
    def from_records(cls,strategy,records):
        if not isinstance(strategy,str) or not strategy.strip():
            return None
        if not isinstance(records,list):
            return None
        target=strategy.strip().lower()
        success_values={"completed","complete","success","succeeded","successful","accepted"}
        failure_values={"failed","failure","error","errored","unsuccessful","rejected"}
        successes=0
        failures=0
        for record in records:
            if not isinstance(record,dict):
                continue
            record_strategy=record.get("strategy")
            outcome=record.get("outcome")
            if not isinstance(record_strategy,str) or record_strategy.strip().lower()!=target:
                continue
            if not isinstance(outcome,str):
                continue
            normalized=outcome.strip().lower()
            if normalized in success_values:
                successes+=1
            elif normalized in failure_values:
                failures+=1
        return cls.create(strategy,successes+failures,successes,failures)

    @classmethod
    def filter_sufficient(cls,effectiveness_list,minimum=None):
        if not isinstance(effectiveness_list,list):
            return []
        threshold=cls.MIN_EVIDENCE if minimum is None else minimum
        if not isinstance(threshold,int) or isinstance(threshold,bool) or threshold<1:
            return []
        result=[]
        for item in effectiveness_list:
            record=item if isinstance(item,cls) else None
            if record is None and isinstance(item,dict):
                record=cls.create(item.get("strategy"),item.get("total",0),item.get("successes",0),item.get("failures",0))
            if record is not None and record.has_sufficient_evidence(threshold):
                result.append(record)
        return result

    def has_sufficient_evidence(self,minimum=None):
        threshold=self.MIN_EVIDENCE if minimum is None else minimum
        if not isinstance(threshold,int) or isinstance(threshold,bool) or threshold<1:
            return False
        return self.total>=threshold

    @classmethod
    def compare(cls,effectiveness_list,minimum=None):
        if not isinstance(effectiveness_list,list) or not effectiveness_list:
            return None
        valid=cls.filter_sufficient(effectiveness_list,minimum)
        if not valid:
            return None
        best=valid[0]
        for item in valid[1:]:
            if item.success_rate()>best.success_rate():
                best=item
        return {
            "best_strategy":best.strategy,
            "best_success_rate":best.success_rate(),
            "strategies":[item.to_dict() for item in valid],
        }

    @classmethod
    def rank(cls,effectiveness_list,minimum=None):
        valid=cls.filter_sufficient(effectiveness_list,minimum)
        if not valid:
            return []
        ranked=sorted(valid,key=lambda item:(item.success_rate(),item.total),reverse=True)
        return ranked
