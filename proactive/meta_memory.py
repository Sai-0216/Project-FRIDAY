from pathlib import Path
import json
from datetime import datetime, timezone
from threading import RLock

META_MEMORY_FILE=Path(__file__).resolve().parent.parent/"data"/"meta_memory.json"
MAX_RECORDS=500


class MetaMemory:

    TYPES={"STRATEGY_LEARNING","IMPROVEMENT","REASONING_QUALITY","DECISION_QUALITY"}

    def __init__(self,memory_type=None,strategy=None,learning=None,confidence="LOW",evidence_count=0,timestamp=None,details=None):
        self.memory_type=memory_type if memory_type in self.TYPES else None
        self.strategy=strategy if isinstance(strategy,str) else None
        self.learning=learning if isinstance(learning,str) else None
        self.confidence=confidence if confidence in {"HIGH","MEDIUM","LOW"} else "LOW"
        self.evidence_count=evidence_count if isinstance(evidence_count,int) and not isinstance(evidence_count,bool) and evidence_count>=0 else 0
        self.timestamp=timestamp if isinstance(timestamp,str) else datetime.now(timezone.utc).isoformat()
        self.details=details if isinstance(details,dict) else {}

    @classmethod
    def create(cls,memory_type,strategy=None,learning=None,confidence="LOW",evidence_count=0,timestamp=None,details=None):
        if memory_type not in cls.TYPES:
            return None
        if strategy is not None and not isinstance(strategy,str):
            return None
        if learning is not None and not isinstance(learning,str):
            return None
        if confidence not in {"HIGH","MEDIUM","LOW"}:
            return None
        if not isinstance(evidence_count,int) or isinstance(evidence_count,bool) or evidence_count<0:
            return None
        if timestamp is not None and not isinstance(timestamp,str):
            return None
        if details is not None and not isinstance(details,dict):
            return None
        return cls(memory_type,strategy,learning,confidence,evidence_count,timestamp,details)

    def to_dict(self):
        return {
            "type":self.memory_type,
            "strategy":self.strategy,
            "learning":self.learning,
            "confidence":self.confidence,
            "evidence_count":self.evidence_count,
            "timestamp":self.timestamp,
            "details":self.details,
        }

    def is_valid(self):
        return self.memory_type in self.TYPES and isinstance(self.timestamp,str) and bool(self.timestamp)



class MetaMemoryStore:

    def __init__(self,file=None):
        self.file=Path(file) if file else META_MEMORY_FILE
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
                self.records=data[-MAX_RECORDS:] if isinstance(data,list) else []
            except Exception:
                self.records=[]

    def _save(self):
        with self.lock:
            try:
                self.file.parent.mkdir(parents=True,exist_ok=True)
                temp=self.file.with_suffix(self.file.suffix+".tmp")
                with open(temp,"w",encoding="utf-8") as f:
                    json.dump(self.records[-MAX_RECORDS:],f,indent=4,ensure_ascii=False)
                temp.replace(self.file)
                return True
            except Exception:
                return False

    def record(self,memory):
        if isinstance(memory,MetaMemory):
            data=memory.to_dict()
        elif isinstance(memory,dict):
            data=memory
        else:
            return False
        validated=MetaMemory.create(data.get("type"),data.get("strategy"),data.get("learning"),data.get("confidence"),data.get("evidence_count"),data.get("timestamp"),data.get("details"))
        if validated is None:
            return False
        with self.lock:
            self.records.append(validated.to_dict())
            self.records=self.records[-MAX_RECORDS:]
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

    def search_strategy(self,strategy,limit=20):
        if not isinstance(strategy,str) or not strategy.strip() or not isinstance(limit,int) or isinstance(limit,bool) or limit<1:
            return []
        target=strategy.strip().lower()
        with self.lock:
            return [record for record in reversed(self.records) if isinstance(record,dict) and isinstance(record.get("strategy"),str) and record.get("strategy").strip().lower()==target][:limit]

    def search_type(self,memory_type,limit=20):
        if memory_type not in MetaMemory.TYPES or not isinstance(limit,int) or isinstance(limit,bool) or limit<1:
            return []
        with self.lock:
            return [record for record in reversed(self.records) if isinstance(record,dict) and record.get("type")==memory_type][:limit]

    def search_learning(self,learning,limit=20):
        if not isinstance(learning,str) or not learning.strip() or not isinstance(limit,int) or isinstance(limit,bool) or limit<1:
            return []
        target=learning.strip().upper()
        with self.lock:
            return [record for record in reversed(self.records) if isinstance(record,dict) and isinstance(record.get("learning"),str) and record.get("learning").strip().upper()==target][:limit]

    def search_confidence(self,confidence,limit=20):
        if confidence not in {"HIGH","MEDIUM","LOW"} or not isinstance(limit,int) or isinstance(limit,bool) or limit<1:
            return []
        with self.lock:
            return [record for record in reversed(self.records) if isinstance(record,dict) and record.get("confidence")==confidence][:limit]

    def filter_confidence(self,minimum="MEDIUM",records=None):
        if minimum not in {"HIGH","MEDIUM","LOW"}:
            return []
        source=self.records if records is None else records
        if not isinstance(source,list):
            return []
        levels={"LOW":1,"MEDIUM":2,"HIGH":3}
        threshold=levels[minimum]
        return [record for record in source if isinstance(record,dict) and levels.get(record.get("confidence"),0)>=threshold]

    @staticmethod
    def validate_record(record):
        if not isinstance(record,dict):
            return False
        if record.get("type") not in MetaMemory.TYPES:
            return False
        strategy=record.get("strategy")
        if strategy is not None and not isinstance(strategy,str):
            return False
        learning=record.get("learning")
        if learning is not None and not isinstance(learning,str):
            return False
        if record.get("confidence") not in {"HIGH","MEDIUM","LOW"}:
            return False
        evidence=record.get("evidence_count")
        if not isinstance(evidence,int) or isinstance(evidence,bool) or evidence<0:
            return False
        timestamp=record.get("timestamp")
        if not isinstance(timestamp,str) or not timestamp.strip():
            return False
        details=record.get("details",{})
        if not isinstance(details,dict):
            return False
        return True

    def validate(self):
        with self.lock:
            return all(self.validate_record(record) for record in self.records)
