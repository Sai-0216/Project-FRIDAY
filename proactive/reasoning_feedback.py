from pathlib import Path
class ReasoningFeedback:

    POSITIVE="POSITIVE"
    NEGATIVE="NEGATIVE"
    NEUTRAL="NEUTRAL"

    SIGNALS={POSITIVE,NEGATIVE,NEUTRAL}

    def __init__(self,signal="NEUTRAL",reason=None,evidence=None):
        self.signal=signal if signal in self.SIGNALS else "NEUTRAL"
        self.reason=reason if isinstance(reason,str) else None
        self.evidence=evidence if isinstance(evidence,dict) else {}

    @classmethod
    def create(cls,signal="NEUTRAL",reason=None,evidence=None):
        if signal not in cls.SIGNALS:
            return None
        if reason is not None and not isinstance(reason,str):
            return None
        if evidence is not None and not isinstance(evidence,dict):
            return None
        return cls(signal,reason,evidence)

    def to_dict(self):
        return {"signal":self.signal,"reason":self.reason,"evidence":self.evidence}

    def is_valid(self):
        return self.signal in self.SIGNALS

    def to_correction(self,target):
        if not isinstance(target,str) or not target.strip():
            return None
        if self.signal != self.NEGATIVE:
            return None
        from proactive.self_correction import SelfCorrection
        confidence="HIGH" if self.evidence else "MEDIUM"
        return SelfCorrection.create(SelfCorrection.CHANGE_STRATEGY,target,self.reason,confidence,self.evidence)

    @classmethod
    def from_assessments(cls, reasoning=None, decision=None):
        evidence={}
        levels=[]
        if isinstance(reasoning,dict):
            evidence["reasoning"]=reasoning
            levels.append(reasoning.get("level"))
        if isinstance(decision,dict):
            evidence["decision"]=decision
            levels.append(decision.get("level"))
        if not levels:
            return cls.create(cls.NEUTRAL,"Insufficient assessment evidence.",evidence)
        if "LOW" in levels or "POOR" in levels:
            return cls.create(cls.NEGATIVE,"Assessment indicates that reasoning or decision quality needs improvement.",evidence)
        if all(level in {"HIGH","GOOD"} for level in levels):
            return cls.create(cls.POSITIVE,"Assessment indicates that reasoning and decision quality are strong.",evidence)
        return cls.create(cls.NEUTRAL,"Assessment indicates mixed or moderate quality.",evidence)


import json
from threading import RLock

FEEDBACK_FILE=Path(__file__).resolve().parent.parent/"data"/"reasoning_feedback.json"
MAX_FEEDBACK=500

class ReasoningFeedbackStore:
    def __init__(self,file=None):
        self.file=Path(file) if file else FEEDBACK_FILE
        self.records=[]
        self.lock=RLock()
        self._load()

    def _load(self):
        with self.lock:
            try:
                if not self.file.exists():
                    self.records=[]
                    return
                with open(self.file,"r",encoding="utf-8") as f:
                    data=json.load(f)
                self.records=data[-MAX_FEEDBACK:] if isinstance(data,list) else []
            except Exception:
                self.records=[]

    def _save(self):
        with self.lock:
            try:
                self.file.parent.mkdir(parents=True,exist_ok=True)
                temp=self.file.with_suffix(self.file.suffix+".tmp")
                with open(temp,"w",encoding="utf-8") as f:
                    json.dump(self.records[-MAX_FEEDBACK:],f,indent=4,ensure_ascii=False)
                temp.replace(self.file)
                return True
            except Exception:
                return False

    def record(self,feedback):
        if isinstance(feedback,ReasoningFeedback):
            data=feedback.to_dict()
        elif isinstance(feedback,dict):
            data=feedback
        else:
            return False
        signal=data.get("signal")
        if signal not in ReasoningFeedback.SIGNALS:
            return False
        with self.lock:
            self.records.append(data)
            self.records=self.records[-MAX_FEEDBACK:]
            if self._save():
                return True
            self.records.pop()
            return False

    def recent(self,limit=20):
        if not isinstance(limit,int) or isinstance(limit,bool) or limit<1:
            return []
        with self.lock:
            return list(self.records[-limit:])

    def count(self):
        with self.lock:
            return len(self.records)
