class AntiDrift:

    NO_DRIFT="NO_DRIFT"
    DRIFT="DRIFT"
    REVIEW="REVIEW"

    STATES={NO_DRIFT,DRIFT,REVIEW}

    @classmethod
    def compare(cls,baseline=None,current=None,threshold=0.20):
        if not isinstance(baseline,(int,float)) or isinstance(baseline,bool):
            return cls.REVIEW
        if not isinstance(current,(int,float)) or isinstance(current,bool):
            return cls.REVIEW
        if not isinstance(threshold,(int,float)) or isinstance(threshold,bool) or threshold<0.0 or threshold>1.0:
            return cls.REVIEW
        if not 0.0<=baseline<=1.0 or not 0.0<=current<=1.0:
            return cls.REVIEW
        difference=round(abs(current-baseline),10)
        return cls.DRIFT if difference>threshold else cls.NO_DRIFT

    @classmethod
    def is_valid(cls,state):
        return state in cls.STATES
