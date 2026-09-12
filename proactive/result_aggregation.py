"""FRIDAY V3 - Phase 23.6 Result Aggregation."""


class ResultAggregation:

    @staticmethod
    def _safe_results(results):
        return results if isinstance(results, list) else []

    @classmethod
    def aggregate(cls, results):
        results = cls._safe_results(results)
        valid_results = []

        for item in results:
            if not isinstance(item, dict):
                continue
            agent = item.get("agent")
            if not isinstance(agent, dict):
                continue
            role = agent.get("role")
            if not role or "result" not in item:
                continue
            valid_results.append({
                "role": role,
                "agent": agent,
                "result": item["result"],
            })

        return {
            "count": len(valid_results),
            "results": valid_results,
            "aggregated": bool(valid_results),
        }

    @classmethod
    def roles(cls, results):
        aggregated = cls.aggregate(results)
        return [item["role"] for item in aggregated["results"]]

    @classmethod
    def values(cls, results):
        aggregated = cls.aggregate(results)
        return [item["result"] for item in aggregated["results"]]

    @classmethod
    def validate(cls, aggregation):
        if not isinstance(aggregation, dict):
            return False
        if not isinstance(aggregation.get("count"), int):
            return False
        if not isinstance(aggregation.get("results"), list):
            return False
        if aggregation["count"] != len(aggregation["results"]):
            return False
        if aggregation.get("aggregated") is not bool(aggregation["count"]):
            return False
        return True


result_aggregation = ResultAggregation()
