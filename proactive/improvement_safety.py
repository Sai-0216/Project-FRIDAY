class ImprovementSafety:

    SAFE="SAFE"
    REVIEW="REVIEW"
    BLOCKED="BLOCKED"

    FORBIDDEN_KEYS={"autonomy_level","execution_permissions","trusted_actions","authorization"}

    @classmethod
    def validate(cls,correction):
        if not isinstance(correction,dict):
            return cls.BLOCKED
        if correction.get("action") not in {"PREPARE","VERIFY","CHANGE_STRATEGY","MAINTAIN","NONE"}:
            return cls.BLOCKED
        target=correction.get("target")
        action=correction.get("action")
        if target is not None and (not isinstance(target,str) or not target.strip()):
            return cls.BLOCKED
        if isinstance(target,str) and target.strip() in cls.FORBIDDEN_KEYS:
            return cls.BLOCKED
        if action=="CHANGE_STRATEGY" and (not isinstance(target,str) or not target.strip()):
            return cls.BLOCKED
        confidence=correction.get("confidence")
        if confidence not in {"HIGH","MEDIUM","LOW"}:
            return cls.BLOCKED
        evidence=correction.get("evidence",{})
        if not isinstance(evidence,dict):
            return cls.BLOCKED
        if any(key in evidence for key in cls.FORBIDDEN_KEYS):
            return cls.BLOCKED
        if confidence=="LOW":
            return cls.REVIEW
        return cls.SAFE
