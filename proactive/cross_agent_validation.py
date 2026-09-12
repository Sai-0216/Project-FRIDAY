"""FRIDAY V3 - Phase 23.5 Cross-Agent Validation."""


class CrossAgentValidation:

    @staticmethod
    def _safe_results(results):
        return results if isinstance(results, list) else []

    @staticmethod
    def _valid_result(result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("agent"), dict):
            return False
        if not result["agent"].get("role"):
            return False
        if "result" not in result:
            return False
        return True

    @classmethod
    def validate_structure(cls, results):
        results = cls._safe_results(results)
        if not results:
            return False
        return all(cls._valid_result(result) for result in results)

    @classmethod
    def compare_results(cls, results):
        results = cls._safe_results(results)

        if not cls.validate_structure(results):
            return {
                "valid": False,
                "agreement": 0.0,
                "roles": [],
                "result_values": [],
            }

        roles = [item["agent"]["role"] for item in results]
        values = [item["result"] for item in results]
        unique_values = []

        for value in values:
            if value not in unique_values:
                unique_values.append(value)

        agreement = 1.0 if len(unique_values) <= 1 else 1.0 / len(unique_values)

        return {
            "valid": True,
            "agreement": agreement,
            "roles": roles,
            "result_values": values,
            "unique_results": unique_values,
        }

    @classmethod
    def validate(cls, results):
        comparison = cls.compare_results(results)
        return comparison["valid"]

    @classmethod
    def assess(cls, results):
        comparison = cls.compare_results(results)

        if not comparison["valid"]:
            level = "INVALID"
        elif comparison["agreement"] >= 0.8:
            level = "HIGH"
        elif comparison["agreement"] >= 0.5:
            level = "MEDIUM"
        else:
            level = "LOW"

        comparison["agreement_level"] = level
        return comparison


cross_agent_validation = CrossAgentValidation()
