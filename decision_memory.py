import json
import os
from datetime import datetime


class DecisionMemory:
    MAX_DECISIONS = 50

    def __init__(self):
        self.file_path = os.path.join(
            "data",
            "decision_memory.json"
        )

        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.file_path):
            self.save([])

    # ---------------------------------------------------------
    # LOAD / SAVE
    # ---------------------------------------------------------

    def load(self):
        try:
            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

            if isinstance(data, list):
                return data

            return []

        except Exception as e:
            print(
                f"[DECISION MEMORY] Load error: {repr(e)}"
            )
            return []

    def save(self, data):
        try:
            with open(
                self.file_path,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except Exception as e:
            print(
                f"[DECISION MEMORY] Save error: {repr(e)}"
            )
            return False

    # ---------------------------------------------------------
    # STORE DECISION
    # ---------------------------------------------------------

    def remember(
        self,
        request,
        decision_type,
        domain,
        goal,
        recommendation,
        confidence="unknown",
        confidence_score=0,
        explanation="",
        alternatives=None,
        chosen_option=None,
    ):
        decisions = self.load()

        if alternatives is None:
            alternatives = []

        if not isinstance(alternatives, list):
            alternatives = [str(alternatives)]

        # Clean alternatives
        cleaned_alternatives = []

        for option in alternatives:
            option = str(option).strip()

            if option and option not in cleaned_alternatives:
                cleaned_alternatives.append(option)

        # Preserve compatibility with older callers
        if chosen_option is None:
            chosen_option = recommendation

        chosen_option = str(
            chosen_option
        ).strip()

        decision = {
            "timestamp": datetime.now().isoformat(),
            "request": str(request),
            "decision_type": str(decision_type),
            "domain": str(domain),
            "goal": str(goal),
            "recommendation": str(recommendation),
            "chosen_option": chosen_option,
            "alternatives": cleaned_alternatives,
            "confidence": str(confidence),
            "confidence_score": int(confidence_score),
            "explanation": str(explanation),
        }

        decisions.append(decision)

        # Keep only the newest decisions
        if len(decisions) > self.MAX_DECISIONS:
            decisions = decisions[-self.MAX_DECISIONS:]

        if self.save(decisions):
            print("[DECISION MEMORY] Decision saved.")
            return decision

        return None

    # ---------------------------------------------------------
    # BASIC ACCESS
    # ---------------------------------------------------------

    def all(self):
        return self.load()

    def latest(self):
        decisions = self.load()

        if not decisions:
            return None

        return decisions[-1]

    # ---------------------------------------------------------
    # FILTERING
    # ---------------------------------------------------------

    def find_by_domain(self, domain):
        domain = str(domain).lower().strip()

        decisions = self.load()

        return [
            decision
            for decision in decisions
            if str(
                decision.get("domain", "")
            ).lower().strip() == domain
        ]

    def find_by_type(self, decision_type):
        decision_type = str(
            decision_type
        ).lower().strip()

        decisions = self.load()

        return [
            decision
            for decision in decisions
            if str(
                decision.get("decision_type", "")
            ).lower().strip() == decision_type
        ]

    def find_by_goal(self, goal):
        goal = str(goal).lower().strip()

        decisions = self.load()

        return [
            decision
            for decision in decisions
            if str(
                decision.get("goal", "")
            ).lower().strip() == goal
        ]

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search(self, query):
        query = str(query).lower().strip()

        if not query:
            return []

        decisions = self.load()

        results = []

        for decision in decisions:

            searchable = " ".join([
                str(decision.get("request", "")),
                str(decision.get("decision_type", "")),
                str(decision.get("domain", "")),
                str(decision.get("goal", "")),
                str(decision.get("recommendation", "")),
                str(decision.get("chosen_option", "")),
                str(decision.get("explanation", "")),
                " ".join(
                    str(x)
                    for x in decision.get(
                        "alternatives",
                        []
                    )
                ),
            ]).lower()

            words = query.split()

            if all(
                word in searchable
                for word in words
            ):
                results.append(decision)

        return results

    # ---------------------------------------------------------
    # LATEST MATCHES
    # ---------------------------------------------------------

    def latest_match(self, query):
        results = self.search(query)

        if not results:
            return None

        return results[-1]

    def latest_by_domain(self, domain):
        results = self.find_by_domain(domain)

        if not results:
            return None

        return results[-1]

    def latest_by_goal(self, goal):
        results = self.find_by_goal(goal)

        if not results:
            return None

        return results[-1]

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------

    def clear(self):
        if self.save([]):
            print("[DECISION MEMORY] Memory cleared.")
            return True

        return False


decision_memory = DecisionMemory()