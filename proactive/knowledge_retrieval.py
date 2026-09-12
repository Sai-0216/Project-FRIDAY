import re


class KnowledgeRetrieval:
    """Retrieve the most relevant retained knowledge for a query."""

    def retrieve(self, knowledge_records, query):
        if not self._valid_input(knowledge_records, query):
            return None

        query_terms = set(re.findall(r"[a-z0-9_]+", query.lower()))
        ranked = []

        for record in knowledge_records:
            text = " ".join([
                str(record.get("lesson", "")),
                str(record.get("lesson_type", "")),
                " ".join(record.get("outcome_states", [])),
            ]).lower()
            text_terms = set(re.findall(r"[a-z0-9_]+", text))
            score = sum(1 for term in query_terms if term in text_terms)
            if record.get("retention_state") == "retain":
                score += 1
            ranked.append((score, record))

        ranked.sort(key=lambda item: item[0], reverse=True)
        best_score, best_record = ranked[0]

        result = {
            "query": query,
            "match_score": best_score,
            "lesson_type": best_record["lesson_type"],
            "lesson": best_record["lesson"],
            "retention_state": best_record["retention_state"],
            "sample_size": best_record["sample_size"],
        }
        return result if self.validate(result) else None

    def _valid_input(self, records, query):
        if not isinstance(records, list) or not records:
            return False
        if not isinstance(query, str) or not query.strip():
            return False
        for record in records:
            if not isinstance(record, dict):
                return False
            if record.get("lesson_type") not in ("reinforce", "warning", "improve", "observe"):
                return False
            if record.get("retention_state") not in ("retain", "review", "observe"):
                return False
            if not isinstance(record.get("lesson"), str) or not record["lesson"]:
                return False
            if not isinstance(record.get("sample_size"), int) or record["sample_size"] <= 0:
                return False
            if not isinstance(record.get("outcome_states"), list) or not record["outcome_states"]:
                return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        required = (
            "query", "match_score", "lesson_type", "lesson",
            "retention_state", "sample_size"
        )
        if any(key not in result for key in required):
            return False
        return (
            isinstance(result["query"], str)
            and bool(result["query"].strip())
            and isinstance(result["match_score"], int)
            and result["match_score"] >= 0
            and result["lesson_type"] in ("reinforce", "warning", "improve", "observe")
            and isinstance(result["lesson"], str)
            and bool(result["lesson"])
            and result["retention_state"] in ("retain", "review", "observe")
            and isinstance(result["sample_size"], int)
            and result["sample_size"] > 0
        )


knowledge_retrieval = KnowledgeRetrieval()
