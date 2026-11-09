from proactive.meta_memory import MetaMemoryStore

class CrossSessionReasoning:

    @staticmethod
    def load(strategy=None,limit=20,store=None):
        store=store or MetaMemoryStore()
        if strategy is None:
            return store.recent(limit)
        return store.search_strategy(strategy,limit)

    @staticmethod
    def summarize(records):
        if not isinstance(records,list) or not records:
            return {"count":0,"high_confidence":0,"strategies":[]}
        strategies=[]
        high=0
        for record in records:
            if not isinstance(record,dict):
                continue
            strategy=record.get("strategy")
            if isinstance(strategy,str) and strategy not in strategies:
                strategies.append(strategy)
            if record.get("confidence")=="HIGH":
                high+=1
        return {"count":len(records),"high_confidence":high,"strategies":strategies}

    @staticmethod
    def context(strategy=None,limit=20,store=None):
        records=CrossSessionReasoning.load(strategy,limit,store)
        return {"records":records,"summary":CrossSessionReasoning.summarize(records)}
