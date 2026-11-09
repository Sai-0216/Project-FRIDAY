import re

import reasoning_context
from decision_memory import decision_memory


class RecommendationEngine:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):
        pass

    # =========================================================
    # DOMAIN DETECTION
    # =========================================================

    def detect_domain(self, prompt):
        text = str(prompt).lower().strip()

        project_markers = (
            "my project",
            "the project",
            "for my project",
            "project",
            "build my",
            "building my",
            "develop my",
        )

        if any(marker in text for marker in project_markers):
            return "project"

        language_markers = (
            "programming language",
            "which language",
            "what language",
            "language should",
            "language to learn",
            "language to study",
            "python",
            "java",
            "c++",
            "javascript",
            "typescript",
            "programming",
        )

        if any(marker in text for marker in language_markers):
            return "language"

        learning_markers = (
            "learn",
            "learning",
            "study",
            "studying",
            "practice",
            "practicing",
            "skill",
            "skills",
        )

        if any(marker in text for marker in learning_markers):
            return "learning"

        editor_markers = (
            "editor",
            "coding",
            "code",
            "programming environment",
            "ide",
            "development environment",
        )

        if any(marker in text for marker in editor_markers):
            return "editor"

        priority_markers = (
            "focus",
            "priority",
            "prioritize",
            "what should i do next",
            "what should i focus on",
            "what should i work on",
            "next step",
            "next steps",
        )

        if any(marker in text for marker in priority_markers):
            return "priority"

        return "general"

    # =========================================================
    # DECISION TYPE
    # =========================================================

    def get_decision_type(self, prompt):
        text = str(prompt).lower().strip()

        # -----------------------------------------------------
        # PRIORITY FIRST
        # -----------------------------------------------------

        priority_markers = (
            "what should i focus on",
            "what should i do next",
            "what should i prioritize",
            "what should i work on",
            "what do i need to focus on",
            "what is my priority",
            "what should be my priority",
            "what next",
            "what's next",
            "then what",
        )

        if any(marker in text for marker in priority_markers):
            return "priority"

        # -----------------------------------------------------
        # COMPARISON SECOND
        # -----------------------------------------------------

        comparison_markers = (
            "compare",
            "comparison",
            "difference between",
            "which is better",
            "what is better",
            "what's better",
            "better option",
            "better for me",
            "better choice",
            "versus",
            " vs ",
            " vs.",
            "compared to",
            " or ",
        )

        if any(marker in text for marker in comparison_markers):
            return "comparison"

        # -----------------------------------------------------
        # RECOMMENDATION
        # -----------------------------------------------------

        recommendation_markers = (
            "what do you recommend",
            "what would you recommend",
            "what should i choose",
            "which one should i choose",
            "what should i use",
            "which one should i use",
            "what should i learn",
            "what should i study",
            "what should i pick",
            "which should i pick",
            "which one is best",
            "what is best for me",
            "what do you suggest",
            "what would you suggest",
            "what should i go with",
        )

        language_recommendation_markers = (
            "what programming language should i choose",
            "which programming language should i choose",
            "what language should i choose",
            "which language should i choose",
            "what programming language should i use",
            "which programming language should i use",
            "what language should i use",
            "which language should i use",
            "what programming language should i learn",
            "which programming language should i learn",
            "what language should i learn",
            "which language should i learn",
            "what programming language should i study",
            "which programming language should i study",
            "what language should i study",
            "which language should i study",
        )

        if any(
            marker in text
            for marker in language_recommendation_markers
        ):
            return "recommendation"

        if any(
            marker in text
            for marker in recommendation_markers
        ):
            return "recommendation"

        return "unknown"

    # =========================================================
    # GOAL DETECTION
    # =========================================================

    def detect_goal(self, prompt):
        text = str(prompt).lower().strip()

        learning_markers = (
            "learn",
            "learning",
            "study",
            "studying",
            "practice",
            "practicing",
            "improve my skills",
            "skill",
            "skills",
        )

        if any(marker in text for marker in learning_markers):
            return "learning"

        project_markers = (
            "my project",
            "the project",
            "for my project",
            "build",
            "building",
            "develop",
            "development",
            "application",
            "app",
            "website",
            "system",
        )

        if any(marker in text for marker in project_markers):
            return "project"

        career_markers = (
            "career",
            "job",
            "jobs",
            "placement",
            "placements",
            "internship",
            "internships",
            "resume",
            "work",
            "professional",
        )

        if any(marker in text for marker in career_markers):
            return "career"

        return "general"

    # =========================================================
    # EXPLICIT GOAL OVERRIDE
    # =========================================================

    def detect_goal_override(self, prompt):
        text = str(prompt).lower().strip()

        java_learning_markers = (
            "learn java",
            "learning java",
            "study java",
            "studying java",
            "practice java",
            "practicing java",
        )

        if any(
            marker in text
            for marker in java_learning_markers
        ):
            return "java"

        python_learning_markers = (
            "learn python",
            "learning python",
            "study python",
            "studying python",
            "practice python",
            "practicing python",
        )

        if any(
            marker in text
            for marker in python_learning_markers
        ):
            return "python"

        python_usage_markers = (
            "build with python",
            "built with python",
            "project with python",
            "use python",
            "using python",
            "python for my project",
        )

        if any(
            marker in text
            for marker in python_usage_markers
        ):
            return "python"

        java_usage_markers = (
            "build with java",
            "built with java",
            "project with java",
            "use java",
            "using java",
            "java for my project",
        )

        if any(
            marker in text
            for marker in java_usage_markers
        ):
            return "java"

        return None

    # =========================================================
    # ADAPTIVE LANGUAGE CHOICE
    # =========================================================

    def adaptive_language_choice(
        self,
        prompt,
        goal=None,
    ):
        override = self.detect_goal_override(prompt)

        if override:
            return override

        favourite_language = reasoning_context.memory.recall(
            "my favourite language"
        )

        learning_language = reasoning_context.memory.recall(
            "my learning language"
        )

        if goal == "learning":
            if learning_language:
                return learning_language

            if favourite_language:
                return favourite_language

        elif goal == "project":
            if favourite_language:
                return favourite_language

            if learning_language:
                return learning_language

        elif goal == "career":
            if learning_language:
                return learning_language

            if favourite_language:
                return favourite_language

        else:
            if favourite_language:
                return favourite_language

            if learning_language:
                return learning_language

        return "python"

    # =========================================================
    # PROJECT RECOMMENDATION
    # =========================================================

    def recommend_project(self, prompt):
        goal = self.detect_goal(prompt)

        language = self.adaptive_language_choice(
            prompt,
            goal
        )

        editor = reasoning_context.memory.recall(
            "my favourite editor"
        )

        project = reasoning_context.memory.recall(
            "my project"
        )

        parts = []

        parts.append(
            f"I would recommend {language}"
        )

        if project:
            parts.append(
                f" for your project {project}"
            )

        if editor:
            parts.append(
                f" and use {editor} as your editor"
            )

        response = "".join(parts)

        if goal == "learning":

            learning_language = (
                reasoning_context.memory.recall(
                    "my learning language"
                )
            )

            if learning_language:
                response += (
                    f". Since you're currently learning "
                    f"{learning_language}, keep using it for "
                    f"practice while building the project."
                )
            else:
                response += (
                    ". This keeps the project aligned with "
                    "your current development goals."
                )

        else:
            response += (
                ". This matches your stored preferences "
                "and current context."
            )

        return response

    # =========================================================
    # LANGUAGE RECOMMENDATION
    # =========================================================

    def recommend_language(self, prompt):
        goal = self.detect_goal(prompt)

        language = self.adaptive_language_choice(
            prompt,
            goal
        )

        favourite_language = reasoning_context.memory.recall(
            "my favourite language"
        )

        learning_language = reasoning_context.memory.recall(
            "my learning language"
        )

        if goal == "learning":

            if (
                learning_language
                and language.lower()
                == learning_language.lower()
            ):
                return (
                    f"I would recommend {language} for you "
                    f"because you're already learning it, "
                    f"so continuing with it will give you "
                    f"better consistency and progress."
                )

        if (
            favourite_language
            and language.lower()
            == favourite_language.lower()
        ):
            return (
                f"I would recommend {language} because "
                f"it's your favourite programming language, "
                f"which should make it easier to stay "
                f"motivated and productive."
            )

        return (
            f"I would recommend {language} based on "
            f"your current goal and stored preferences."
        )

    # =========================================================
    # COMPARISON RECOMMENDATION
    # =========================================================

    def recommend_comparison(self, prompt):
        goal = self.detect_goal(prompt)

        favourite_language = reasoning_context.memory.recall(
            "my favourite language"
        )

        learning_language = reasoning_context.memory.recall(
            "my learning language"
        )

        language = self.adaptive_language_choice(
            prompt,
            goal
        )

        if goal == "learning":

            if learning_language:
                return (
                    f"I would choose {learning_language} "
                    f"for your learning goal because "
                    f"you're already learning it and "
                    f"continuing with it gives you better "
                    f"consistency."
                )

        if goal == "project":

            if favourite_language:
                return (
                    f"I would choose {favourite_language} "
                    f"for your project because it matches "
                    f"your existing preference and should "
                    f"let you work more comfortably."
                )

        if favourite_language:
            return (
                f"I would lean toward {favourite_language} "
                f"for you because it is your preferred "
                f"programming language."
            )

        return (
            f"I would choose {language} based on "
            f"your current context and goal."
        )

    # =========================================================
    # PRIORITY RECOMMENDATION
    # =========================================================

    def recommend_priority(self, prompt):
        learning_language = reasoning_context.memory.recall(
            "my learning language"
        )

        project = reasoning_context.memory.recall(
            "my project"
        )

        if project and learning_language:
            return (
                f"I would prioritize your {project} project "
                f"while continuing your {learning_language} "
                f"learning in parallel."
            )

        if project:
            return (
                f"I would prioritize your {project} project "
                f"next."
            )

        if learning_language:
            return (
                f"I would prioritize continuing with "
                f"{learning_language}."
            )

        return (
            "I would prioritize the task that moves "
            "your main current goal forward."
        )

    # =========================================================
    # GENERAL RECOMMENDATION
    # =========================================================

    def recommend_general(self, prompt):
        language = self.adaptive_language_choice(
            prompt,
            "general"
        )

        return (
            f"Based on what I know about your preferences, "
            f"I would lean toward {language}."
        )

    # =========================================================
    # GENERATE RECOMMENDATION
    # =========================================================

    def generate_recommendation(
        self,
        prompt,
        decision_type=None,
        domain=None,
        goal=None,
    ):
        if decision_type is None:
            decision_type = self.get_decision_type(
                prompt
            )

        if domain is None:
            domain = self.detect_domain(
                prompt
            )

        if goal is None:
            goal = self.detect_goal(
                prompt
            )

        if decision_type == "priority":
            return self.recommend_priority(
                prompt
            )

        if decision_type == "comparison":

            if domain == "language":
                return self.recommend_comparison(
                    prompt
                )

            return self.recommend_general(
                prompt
            )

        if decision_type == "recommendation":

            if domain == "project":
                return self.recommend_project(
                    prompt
                )

            if domain == "language":
                return self.recommend_language(
                    prompt
                )

            if domain == "editor":

                editor = reasoning_context.memory.recall(
                    "my favourite editor"
                )

                if editor:
                    return (
                        f"I would recommend {editor} "
                        f"for your coding work because "
                        f"it's your preferred editor."
                    )

                return (
                    "I would recommend using a modern "
                    "editor that fits your workflow."
                )

            return self.recommend_general(
                prompt
            )

        return ""

    # =========================================================
    # EXTRACT ALTERNATIVES
    # =========================================================

    def extract_alternatives(self, prompt):
        text = str(prompt).lower().strip()

        # -----------------------------------------------------
        # python or java
        # python vs java
        # python versus java
        # -----------------------------------------------------

        match = re.search(
            r"\b([a-zA-Z0-9+#.-]+)\s+"
            r"(?:or|vs|versus)\s+"
            r"([a-zA-Z0-9+#.-]+)\b",
            text
        )

        if match:

            first = match.group(1).strip()
            second = match.group(2).strip()

            if (
                first
                and second
                and first != second
            ):
                return [
                    first,
                    second,
                ]

        # -----------------------------------------------------
        # python and java
        # -----------------------------------------------------

        match = re.search(
            r"\b([a-zA-Z0-9+#.-]+)\s+"
            r"and\s+"
            r"([a-zA-Z0-9+#.-]+)\b",
            text
        )

        if match:

            first = match.group(1).strip()
            second = match.group(2).strip()

            if (
                first
                and second
                and first != second
            ):
                return [
                    first,
                    second,
                ]

        return []

    # =========================================================
    # EXTRACT CHOSEN OPTION
    # =========================================================

    def extract_chosen_option(
        self,
        recommendation,
        alternatives,
    ):
        """
        Convert a full recommendation sentence into
        the actual selected option.

        Example:

            recommendation =
                "I would choose java for your learning goal..."

            alternatives =
                ["python", "java"]

            result =
                "java"
        """

        if not alternatives:
            return str(
                recommendation
            ).strip()

        text = str(
            recommendation
        ).lower().strip()

        # -----------------------------------------------------
        # Direct matching
        # -----------------------------------------------------

        for option in alternatives:

            option_lower = option.lower().strip()

            choose_patterns = (
                f"choose {option_lower}",
                f"recommend {option_lower}",
                f"pick {option_lower}",
                f"select {option_lower}",
                f"go with {option_lower}",
                f"lean toward {option_lower}",
                f"prefer {option_lower}",
            )

            if any(
                pattern in text
                for pattern in choose_patterns
            ):
                return option

        # -----------------------------------------------------
        # Fallback: exact option appears in response
        # -----------------------------------------------------

        sorted_options = sorted(
            alternatives,
            key=len,
            reverse=True,
        )

        for option in sorted_options:

            option_lower = option.lower().strip()

            pattern = (
                r"\b"
                + re.escape(option_lower)
                + r"\b"
            )

            if re.search(
                pattern,
                text
            ):
                return option

        return str(
            recommendation
        ).strip()

    # =========================================================
    # CONFIDENCE
    # =========================================================

    def get_confidence(
        self,
        prompt,
        decision_type,
        domain,
        goal,
    ):
        if decision_type == "unknown":
            return "none"

        override = self.detect_goal_override(
            prompt
        )

        if override:
            return "high"

        relevant_memory = False

        if domain == "project":

            relevant_memory = bool(
                reasoning_context.memory.recall(
                    "my project"
                )
                or reasoning_context.memory.recall(
                    "my favourite language"
                )
            )

        elif domain == "language":

            relevant_memory = bool(
                reasoning_context.memory.recall(
                    "my favourite language"
                )
                or reasoning_context.memory.recall(
                    "my learning language"
                )
            )

        elif domain == "editor":

            relevant_memory = bool(
                reasoning_context.memory.recall(
                    "my favourite editor"
                )
            )

        elif domain == "priority":

            relevant_memory = bool(
                reasoning_context.memory.recall(
                    "my project"
                )
                or reasoning_context.memory.recall(
                    "my learning language"
                )
            )

        if domain != "general" and relevant_memory:
            return "high"

        if decision_type in (
            "priority",
            "comparison",
            "recommendation",
        ):
            return "medium"

        return "low"

    # =========================================================
    # CONFIDENCE SCORE
    # =========================================================

    def get_confidence_score(self, confidence):
        scores = {
            "high": 90,
            "medium": 70,
            "low": 45,
            "none": 0,
        }

        return scores.get(
            str(confidence).lower(),
            0
        )

    # =========================================================
    # EXPLANATION
    # =========================================================

    def get_explanation(
        self,
        prompt,
        domain,
        goal,
        recommendation,
    ):
        reasons = []

        if goal == "learning":
            reasons.append(
                "it matches your current learning goal"
            )

        elif goal == "project":
            reasons.append(
                "it fits your current project"
            )

        elif goal == "career":
            reasons.append(
                "it aligns with your career direction"
            )

        if domain == "language":

            learning_language = (
                reasoning_context.memory.recall(
                    "my learning language"
                )
            )

            favourite_language = (
                reasoning_context.memory.recall(
                    "my favourite language"
                )
            )

            if (
                learning_language
                and recommendation.lower()
                == learning_language.lower()
            ):
                reasons.append(
                    f"you are already learning "
                    f"{learning_language}"
                )

            if (
                favourite_language
                and recommendation.lower()
                == favourite_language.lower()
            ):
                reasons.append(
                    f"{favourite_language} is your "
                    f"preferred programming language"
                )

        elif domain == "project":

            project = reasoning_context.memory.recall(
                "my project"
            )

            editor = reasoning_context.memory.recall(
                "my favourite editor"
            )

            if project:
                reasons.append(
                    f"it supports your {project} project"
                )

            if editor:
                reasons.append(
                    f"it fits your {editor} workflow"
                )

        elif domain == "editor":

            editor = reasoning_context.memory.recall(
                "my favourite editor"
            )

            if editor:
                reasons.append(
                    f"{editor} is your preferred editor"
                )

        unique_reasons = []

        for reason in reasons:
            if reason not in unique_reasons:
                unique_reasons.append(reason)

        if not unique_reasons:
            return (
                "it is the best fit based on the "
                "current context"
            )

        return "; ".join(
            unique_reasons
        )

    # =========================================================
    # SAVE DECISION
    # =========================================================

    def save_decision(
        self,
        prompt,
        decision_type,
        domain,
        goal,
        recommendation,
    ):
        latest = decision_memory.latest()

        # -----------------------------------------------------
        # CONFIDENCE
        # -----------------------------------------------------

        confidence = self.get_confidence(
            prompt,
            decision_type,
            domain,
            goal,
        )

        confidence_score = self.get_confidence_score(
            confidence
        )

        # -----------------------------------------------------
        # EXPLANATION
        # -----------------------------------------------------

        explanation = self.get_explanation(
            prompt,
            domain,
            goal,
            recommendation,
        )

        # -----------------------------------------------------
        # ALTERNATIVES
        # -----------------------------------------------------

        alternatives = self.extract_alternatives(
            prompt
        )

        # -----------------------------------------------------
        # CHOSEN OPTION
        # -----------------------------------------------------

        chosen_option = self.extract_chosen_option(
            recommendation,
            alternatives,
        )

        # -----------------------------------------------------
        # DUPLICATE / UPGRADE PROTECTION
        # -----------------------------------------------------

        if latest:

            same_request = (
                str(
                    latest.get(
                        "request",
                        ""
                    )
                ).strip().lower()
                ==
                str(prompt).strip().lower()
            )

            same_recommendation = (
                str(
                    latest.get(
                        "recommendation",
                        ""
                    )
                ).strip().lower()
                ==
                str(recommendation).strip().lower()
            )

            if (
                same_request
                and same_recommendation
            ):

                existing_alternatives = latest.get(
                    "alternatives",
                    []
                )

                existing_chosen = str(
                    latest.get(
                        "chosen_option",
                        ""
                    )
                ).strip()

                # -------------------------------------------------
                # Already fully upgraded
                # -------------------------------------------------

                if (
                    existing_alternatives
                    == alternatives
                    and existing_chosen
                    == chosen_option
                ):
                    print(
                        "[RECOMMENDATION] "
                        "Duplicate decision not saved."
                    )

                    return latest

                # -------------------------------------------------
                # Upgrade old decision
                # -------------------------------------------------

                print(
                    "[RECOMMENDATION] "
                    "Existing decision found. "
                    "Upgrading comparison memory."
                )

                latest["alternatives"] = alternatives
                latest["chosen_option"] = chosen_option
                latest["confidence"] = confidence
                latest["confidence_score"] = confidence_score
                latest["explanation"] = explanation

                decisions = decision_memory.all()

                if decisions:

                    decisions[-1] = latest

                    decision_memory.save(
                        decisions
                    )

                print(
                    "[RECOMMENDATION] "
                    "Existing decision upgraded."
                )

                return latest

        # -----------------------------------------------------
        # NEW DECISION
        # -----------------------------------------------------

        decision_memory.remember(
            request=prompt,
            decision_type=decision_type,
            domain=domain,
            goal=goal,
            recommendation=recommendation,
            confidence=confidence,
            confidence_score=confidence_score,
            explanation=explanation,
            alternatives=alternatives,
            chosen_option=chosen_option,
        )

        if alternatives:
            print(
                f"[RECOMMENDATION] "
                f"Alternatives: {alternatives}"
            )

            print(
                f"[RECOMMENDATION] "
                f"Chosen option: {chosen_option}"
            )

        print(
            "[RECOMMENDATION] "
            "Decision stored in memory."
        )

        return decision_memory.latest()

    # =========================================================
    # RECOMMEND
    # =========================================================

    def recommend(self, prompt):
        decision_type = self.get_decision_type(
            prompt
        )

        domain = self.detect_domain(
            prompt
        )

        goal = self.detect_goal(
            prompt
        )

        print(
            f"[RECOMMENDATION] "
            f"Decision type: {decision_type}"
        )

        print(
            f"[RECOMMENDATION] "
            f"Domain: {domain}"
        )

        print(
            f"[RECOMMENDATION] "
            f"Goal: {goal}"
        )

        if decision_type == "unknown":
            return ""

        recommendation = (
            self.generate_recommendation(
                prompt,
                decision_type,
                domain,
                goal,
            )
        )

        if not recommendation:
            return ""

        self.save_decision(
            prompt=prompt,
            decision_type=decision_type,
            domain=domain,
            goal=goal,
            recommendation=recommendation,
        )

        return recommendation

    # =========================================================
    # FULL ANALYSIS
    # =========================================================

    def analyze(self, prompt):
        decision_type = self.get_decision_type(
            prompt
        )

        domain = self.detect_domain(
            prompt
        )

        goal = self.detect_goal(
            prompt
        )

        is_decision = (
            decision_type != "unknown"
        )

        if not is_decision:

            return {
                "is_decision": False,
                "decision_type": "unknown",
                "domain": domain,
                "goal": goal,
                "recommendation": "",
                "confidence": "none",
                "confidence_score": 0,
                "explanation": "",
            }

        recommendation = (
            self.recommend(prompt)
        )

        confidence = self.get_confidence(
            prompt,
            decision_type,
            domain,
            goal,
        )

        confidence_score = (
            self.get_confidence_score(
                confidence
            )
        )

        explanation = self.get_explanation(
            prompt,
            domain,
            goal,
            recommendation,
        )

        return {
            "is_decision": True,
            "decision_type": decision_type,
            "domain": domain,
            "goal": goal,
            "recommendation": recommendation,
            "confidence": confidence,
            "confidence_score": confidence_score,
            "explanation": explanation,
        }


recommendation_engine = RecommendationEngine()