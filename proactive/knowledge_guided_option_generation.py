class KnowledgeGuidedOptionGeneration:
    """Generate decision options using contextual analysis and learned knowledge."""

    def generate(self, context_result, knowledge_result):
        if not self._valid_inputs(context_result, knowledge_result):
            return None

        options = list(context_result["available_options"])
        guidance = knowledge_result["guidance"]
        lesson_type = knowledge_result["generalized_lesson_type"]

        scored_options = []
        for index, option in enumerate(options, start=1):
            if guidance == "avoid" and lesson_type == "warning":
                recommendation = "avoid"
            elif guidance == "reinforce" and lesson_type == "reinforce":
                recommendation = "preferred"
            elif guidance == "improve" and lesson_type == "improve":
                recommendation = "consider"
            elif guidance == "consider":
                recommendation = "consider"
            else:
                recommendation = "observe"

            scored_options.append({
                "option_id": index,
                "option": option,
                "recommendation": recommendation,
            })

        result = {
            "goal": context_result["goal"],
            "options": scored_options,
            "guidance": guidance,
            "lesson_type": lesson_type,
            "option_count": len(scored_options),
        }

        return result if self.validate(result) else None

    def _valid_inputs(self, context_result, knowledge_result):
        if not isinstance(context_result, dict) or not isinstance(knowledge_result, dict):
            return False
        if not isinstance(context_result.get("goal"), str) or not context_result["goal"].strip():
            return False
        if not isinstance(context_result.get("available_options"), list) or not context_result["available_options"]:
            return False
        if not all(isinstance(item, str) and item.strip() for item in context_result["available_options"]):
            return False
        if knowledge_result.get("guidance") not in ("reinforce", "avoid", "improve", "consider", "observe"):
            return False
        if knowledge_result.get("generalized_lesson_type") not in ("reinforce", "warning", "improve", "observe"):
            return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False
        if not isinstance(result.get("options"), list) or not result["options"]:
            return False
        if result.get("guidance") not in ("reinforce", "avoid", "improve", "consider", "observe"):
            return False
        if result.get("lesson_type") not in ("reinforce", "warning", "improve", "observe"):
            return False
        if not isinstance(result.get("option_count"), int) or result["option_count"] != len(result["options"]):
            return False

        for item in result["options"]:
            if not isinstance(item, dict):
                return False
            if not isinstance(item.get("option_id"), int) or item["option_id"] <= 0:
                return False
            if not isinstance(item.get("option"), str) or not item["option"].strip():
                return False
            if item.get("recommendation") not in ("preferred", "avoid", "consider", "observe"):
                return False

        return True


knowledge_guided_option_generation = KnowledgeGuidedOptionGeneration()
