"""
FRIDAY Decision Recall
Phase 15.7 - Decision Memory

Handles:
- Natural decision recall
- Recommendation recall
- Choice recall
- Alternatives recall
- Reason recall
- Latest decision recall
- Topic-aware decision matching
- Multi-decision recall
- Contextual follow-up recall
- Comparison-aware "why not?" handling
"""

import re

from decision_memory import decision_memory


class DecisionRecall:

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):
        pass

    # ============================================================
    # NORMALIZATION
    # ============================================================

    def normalize(self, command):
        command = str(command or "").lower().strip()

        command = re.sub(
            r"\s+",
            " ",
            command
        )

        command = command.rstrip(
            " .,!?:;"
        )

        return command

    # ============================================================
    # RECALL REQUEST DETECTION
    # ============================================================

    def is_recall_request(self, command):
        normalized = self.normalize(command)

        if not normalized:
            return False

        # ----------------------------------------
        # Recommendation
        # ----------------------------------------

        recommendation_phrases = (
            "what did you recommend",
            "what did you suggest",
            "what was your recommendation",
            "what was your suggestion",
            "what recommendation did you give",
            "what suggestion did you give",
            "what did you advise",
            "what advice did you give",
            "remind me what you recommended",
            "remind me what you suggested",
        )

        if any(
            phrase in normalized
            for phrase in recommendation_phrases
        ):
            return True

        # ----------------------------------------
        # Decision / choice
        # ----------------------------------------

        decision_phrases = (
            "what did i choose",
            "what did i pick",
            "which one did i choose",
            "which one did i pick",
            "what choice did i make",
            "what did we choose",
            "what decision did i make",
            "what did i decide",
            "which did i choose",
            "which did i pick",
        )

        if any(
            phrase in normalized
            for phrase in decision_phrases
        ):
            return True

        # ----------------------------------------
        # Alternatives
        # ----------------------------------------

        alternatives_phrases = (
            "what were my options",
            "what were the options",
            "what were my choices",
            "what choices did i have",
            "what alternatives did i have",
            "what were the alternatives",
            "what were my alternatives",
            "what were the other options",
            "what were the other choices",
            "what was the other option",
            "what was the other choice",
        )

        if any(
            phrase in normalized
            for phrase in alternatives_phrases
        ):
            return True

        # ----------------------------------------
        # Reason
        # ----------------------------------------

        reason_phrases = (
            "why did you recommend",
            "why did you suggest",
            "why did you choose",
            "why did you pick",
            "why was this recommended",
            "why was this suggested",
            "why this choice",
            "why this option",
            "why did we choose",
            "why did we pick",
            "why not",
        )

        if any(
            phrase in normalized
            for phrase in reason_phrases
        ):
            return True

        # ----------------------------------------
        # Latest
        # ----------------------------------------

        latest_phrases = (
            "what was your last recommendation",
            "what was your latest recommendation",
            "what was your last suggestion",
            "what was your latest suggestion",
            "what was the last recommendation",
            "what was the latest recommendation",
            "what did you last recommend",
            "what did you last suggest",
            "what did you suggest last",
            "what did you recommend last",
            "what did you suggest",
            "what did you recommend",
        )

        if any(
            phrase in normalized
            for phrase in latest_phrases
        ):
            return True

        return False

    # ============================================================
    # QUESTION TYPE
    # ============================================================

    def detect_question_type(self, command):
        normalized = self.normalize(command)

        # ----------------------------------------
        # Reason
        # ----------------------------------------

        if (
            normalized == "why"
            or normalized == "why not"
            or normalized.startswith("why did")
            or normalized.startswith("why was")
            or normalized.startswith("why this")
            or normalized.startswith("why not")
            or "reason" in normalized
        ):
            return "reason"

        # ----------------------------------------
        # Alternatives
        # ----------------------------------------

        if (
            "options" in normalized
            or "alternatives" in normalized
            or "other option" in normalized
            or "other options" in normalized
            or "other choice" in normalized
            or "other choices" in normalized
        ):
            return "alternatives"

        # ----------------------------------------
        # Choice
        # ----------------------------------------

        if (
            "what did i choose" in normalized
            or "what did i pick" in normalized
            or "which one did i choose" in normalized
            or "which one did i pick" in normalized
            or "which did i choose" in normalized
            or "which did i pick" in normalized
            or "what choice did i make" in normalized
            or "what did i decide" in normalized
        ):
            return "choice"

        return "recommendation"

    # ============================================================
    # RECALL TYPE
    # ============================================================

    def detect_recall_type(self, command):
        normalized = self.normalize(command)

        # IMPORTANT:
        # Specific topics must be checked BEFORE latest.
        # Otherwise phrases such as:
        # "what did you recommend for learning?"
        # may incorrectly become "latest".

        # ----------------------------------------
        # Project
        # ----------------------------------------

        if (
            "for my project" in normalized
            or "for the project" in normalized
            or "for project" in normalized
            or "my project" in normalized
        ):
            return "project"

        # ----------------------------------------
        # Editor
        # ----------------------------------------

        if (
            "for coding" in normalized
            or "for code" in normalized
            or "for programming" in normalized
            or "for editor" in normalized
            or "my editor" in normalized
        ):
            return "editor"

        # ----------------------------------------
        # Learning
        # ----------------------------------------

        if (
            "for learning" in normalized
            or "for study" in normalized
            or "for studying" in normalized
            or "to learn" in normalized
            or "while learning" in normalized
        ):
            return "learning"

        # ----------------------------------------
        # Language
        # ----------------------------------------

        if (
            "programming language" in normalized
            or "language" in normalized
            or "python or java" in normalized
            or "java or python" in normalized
        ):
            return "language"

        # ----------------------------------------
        # Career
        # ----------------------------------------

        if (
            "for career" in normalized
            or "career" in normalized
            or "for job" in normalized
            or "for jobs" in normalized
        ):
            return "career"

        # ----------------------------------------
        # Latest
        # ----------------------------------------

        if (
            "last" in normalized
            or "latest" in normalized
            or normalized in (
                "what did you suggest",
                "what did you recommend",
            )
        ):
            return "latest"

        return None

    # ============================================================
    # OPTION EXTRACTION
    # ============================================================

    def extract_referenced_options(self, command):
        normalized = self.normalize(command)

        known_options = (
            "python",
            "java",
            "javascript",
            "typescript",
            "c",
            "c++",
            "c#",
            "go",
            "rust",
            "kotlin",
            "swift",
            "cursor",
            "vscode",
            "vs code",
            "visual studio code",
            "pycharm",
            "intellij",
            "intellij idea",
        )

        found = []

        for option in known_options:

            pattern = (
                r"(?<!\w)"
                + re.escape(option)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalized
            ):
                normalized_option = option

                if option == "vs code":
                    normalized_option = "vscode"

                elif option == "visual studio code":
                    normalized_option = "vscode"

                elif option == "intellij idea":
                    normalized_option = "intellij"

                if normalized_option not in found:
                    found.append(
                        normalized_option
                    )

        return found

    # ============================================================
    # GOAL HINT
    # ============================================================

    def detect_goal_hint(self, command):
        normalized = self.normalize(command)

        if (
            "learn" in normalized
            or "learning" in normalized
            or "study" in normalized
            or "studying" in normalized
        ):
            return "learning"

        if "project" in normalized:
            return "project"

        if (
            "career" in normalized
            or "job" in normalized
            or "jobs" in normalized
        ):
            return "career"

        return None

    # ============================================================
    # DECISION SCORING
    # ============================================================

    def score_decision(
        self,
        decision,
        command,
        recall_type=None,
        question_type="recommendation"
    ):
        normalized = self.normalize(command)

        request = self.normalize(
            decision.get(
                "request",
                ""
            )
        )

        domain = self.normalize(
            decision.get(
                "domain",
                ""
            )
        )

        goal = self.normalize(
            decision.get(
                "goal",
                ""
            )
        )

        recommendation = self.normalize(
            decision.get(
                "recommendation",
                ""
            )
        )

        chosen_option = self.normalize(
            decision.get(
                "chosen_option",
                ""
            )
        )

        alternatives = decision.get(
            "alternatives",
            []
        )

        if not isinstance(
            alternatives,
            list
        ):
            alternatives = []

        alternatives = [
            self.normalize(option)
            for option in alternatives
            if option
        ]

        score = 0

        # ----------------------------------------
        # Exact request similarity
        # ----------------------------------------

        if normalized == request:
            score += 30

        elif (
            normalized
            and request
            and (
                normalized in request
                or request in normalized
            )
        ):
            score += 15

        # ----------------------------------------
        # Recall topic
        # ----------------------------------------

        if recall_type:

            if recall_type == domain:
                score += 20

            if recall_type == goal:
                score += 20

        # ----------------------------------------
        # Goal hint
        # ----------------------------------------

        goal_hint = self.detect_goal_hint(
            normalized
        )

        if goal_hint:

            if goal_hint == goal:
                score += 20

        # ----------------------------------------
        # Explicit options
        # ----------------------------------------

        referenced_options = (
            self.extract_referenced_options(
                normalized
            )
        )

        for option in referenced_options:

            if option == chosen_option:
                score += 10

            elif option in alternatives:
                score += 5

        # ----------------------------------------
        # Both comparison options present
        # ----------------------------------------

        matched_alternatives = [
            option
            for option in alternatives
            if option
            and option in normalized
        ]

        if len(matched_alternatives) >= 2:
            score += 20

        # ----------------------------------------
        # Question-specific matching
        # ----------------------------------------

        if question_type == "choice":

            if chosen_option:
                score += 15

        elif question_type == "alternatives":

            if alternatives:
                score += 15

        elif question_type == "reason":

            if decision.get(
                "explanation"
            ):
                score += 10

            if decision.get(
                "confidence"
            ):
                score += 5

        # ----------------------------------------
        # Recency
        # ----------------------------------------

        score += 1

        return score

    # ============================================================
    # BEST DECISION MATCH
    # ============================================================

    def find_best_decision(
        self,
        command,
        recall_type=None,
        question_type="recommendation"
    ):
        decisions = decision_memory.all()

        if not decisions:
            return None

        scored = []

        for index, decision in enumerate(
            decisions
        ):

            score = self.score_decision(
                decision,
                command,
                recall_type,
                question_type
            )

            scored.append(
                (
                    score,
                    index,
                    decision
                )
            )

        scored.sort(
            key=lambda item: (
                item[0],
                item[1]
            ),
            reverse=True
        )

        best_score, _, best_decision = (
            scored[0]
        )

        print(
            "[DECISION RECALL] Best match score:",
            best_score
        )

        if best_score > 0:

            print(
                "[DECISION RECALL] "
                "Best matching saved decision found."
            )

            return best_decision

        return None

    # ============================================================
    # DECISION RETRIEVAL
    # ============================================================

    def get_decision(
        self,
        command,
        recall_type=None,
        question_type="recommendation"
    ):
        # ----------------------------------------
        # Intelligent matching
        # ----------------------------------------

        decision = self.find_best_decision(
            command,
            recall_type,
            question_type
        )

        if decision:
            return decision

        # ----------------------------------------
        # Topic fallback
        # ----------------------------------------

        if recall_type == "project":

            decisions = (
                decision_memory.find_by_domain(
                    "project"
                )
            )

            if decisions:
                return decisions[0]

        if recall_type == "editor":

            decisions = (
                decision_memory.find_by_domain(
                    "editor"
                )
            )

            if decisions:
                return decisions[0]

        if recall_type == "learning":

            decisions = (
                decision_memory.find_by_goal(
                    "learning"
                )
            )

            if decisions:
                return decisions[0]

        if recall_type == "language":

            decisions = (
                decision_memory.find_by_domain(
                    "language"
                )
            )

            if decisions:
                return decisions[0]

        if recall_type == "career":

            decisions = (
                decision_memory.find_by_goal(
                    "career"
                )
            )

            if decisions:
                return decisions[0]

        # ----------------------------------------
        # Latest fallback
        # ----------------------------------------

        return decision_memory.latest()

    # ============================================================
    # FORMAT RECOMMENDATION
    # ============================================================

    def format_recommendation(
        self,
        decision
    ):
        recommendation = str(
            decision.get(
                "recommendation",
                ""
            )
        ).strip()

        if not recommendation:
            return None

        return (
            "I recommended "
            + recommendation
        )

    # ============================================================
    # FORMAT CHOICE
    # ============================================================

    def format_choice(
        self,
        decision
    ):
        chosen = str(
            decision.get(
                "chosen_option",
                ""
            )
        ).strip()

        if chosen:
            return (
                f"You chose {chosen}."
            )

        recommendation = str(
            decision.get(
                "recommendation",
                ""
            )
        ).strip()

        if recommendation:
            return (
                "The recommendation was "
                + recommendation
            )

        return None

    # ============================================================
    # FORMAT ALTERNATIVES
    # ============================================================

    def format_alternatives(
        self,
        decision
    ):
        alternatives = decision.get(
            "alternatives",
            []
        )

        if not isinstance(
            alternatives,
            list
        ):
            alternatives = []

        alternatives = [
            str(option).strip()
            for option in alternatives
            if str(option).strip()
        ]

        if alternatives:
            return (
                "The options were "
                + ", ".join(alternatives)
                + "."
            )

        return None

    # ============================================================
    # FORMAT REASON
    # ============================================================

    def format_reason(
        self,
        decision,
        why_not=False
    ):
        chosen = str(
            decision.get(
                "chosen_option",
                ""
            )
        ).strip()

        explanation = str(
            decision.get(
                "explanation",
                ""
            )
        ).strip()

        recommendation = str(
            decision.get(
                "recommendation",
                ""
            )
        ).strip()

        alternatives = decision.get(
            "alternatives",
            []
        )

        if not isinstance(
            alternatives,
            list
        ):
            alternatives = []

        alternatives = [
            str(option).strip()
            for option in alternatives
            if str(option).strip()
        ]

        # ----------------------------------------
        # WHY NOT
        # ----------------------------------------

        if why_not:

            rejected = [
                option
                for option in alternatives
                if option.lower()
                != chosen.lower()
            ]

            if rejected:

                rejected_text = ", ".join(
                    rejected
                )

                if explanation:
                    return (
                        f"I didn't choose "
                        f"{rejected_text} because "
                        f"{explanation}."
                    )

                if recommendation:
                    return (
                        f"I rejected "
                        f"{rejected_text} in favor of "
                        f"{chosen or recommendation}."
                    )

            if chosen:

                if explanation:
                    return (
                        f"I chose {chosen} because "
                        f"{explanation}."
                    )

                return (
                    f"I chose {chosen} because it "
                    "was the stronger option."
                )

        # ----------------------------------------
        # NORMAL WHY
        # ----------------------------------------

        if chosen and explanation:
            return (
                f"I chose {chosen} because "
                f"{explanation}."
            )

        if explanation:
            return (
                "The reason was "
                + explanation
                + "."
            )

        if recommendation:
            return (
                "I recommended it because "
                "it best matched your situation."
            )

        return None

    # ============================================================
    # RECALL
    # ============================================================

    def recall(
        self,
        command
    ):
        normalized = self.normalize(
            command
        )

        # IMPORTANT:
        # Contextual phrases such as:
        # "why"
        # "why not"
        # "which one did you choose"
        # "what about the other option"
        #
        # must be handled by contextual_recall().
        #
        # Returning None here prevents the generic
        # recall engine from stealing those requests.

        if self.is_contextual_recall(
            normalized
        ):
            return None

        if not self.is_recall_request(
            normalized
        ):
            return None

        question_type = (
            self.detect_question_type(
                normalized
            )
        )

        recall_type = (
            self.detect_recall_type(
                normalized
            )
        )

        print(
            "[DECISION RECALL] Question:",
            question_type
        )

        print(
            "[DECISION RECALL] Type:",
            recall_type
        )

        decision = self.get_decision(
            normalized,
            recall_type,
            question_type
        )

        if not decision:

            print(
                "[DECISION RECALL] "
                "No saved decision found."
            )

            return None

        # ----------------------------------------
        # Format answer
        # ----------------------------------------

        if question_type == "reason":

            return self.format_reason(
                decision,
                why_not=(
                    normalized == "why not"
                    or normalized.startswith(
                        "why not"
                    )
                )
            )

        if question_type == "alternatives":

            return self.format_alternatives(
                decision
            )

        if question_type == "choice":

            return self.format_choice(
                decision
            )

        return self.format_recommendation(
            decision
        )

    # ============================================================
    # CONTEXTUAL RECALL DETECTION
    # ============================================================

    def is_contextual_recall(
        self,
        command
    ):
        normalized = self.normalize(
            command
        )

        contextual_phrases = (
            "why",
            "why not",

            "why did you choose",
            "why did you pick",
            "why did you recommend",
            "why did you suggest",

            "what about the other one",
            "what about the other option",

            "which one",
            "which one did you choose",
            "which one did you pick",

            "which did you choose",
            "which did you pick",

            "what did you choose",
            "what did you pick",

            "what were the other options",
            "what was the other option",

            "tell me why",
            "explain why",
        )

        if normalized in contextual_phrases:
            return True

        return False

    # ============================================================
    # CONTEXTUAL RECALL
    # ============================================================

    def contextual_recall(
        self,
        command
    ):
        normalized = self.normalize(
            command
        )

        if not self.is_contextual_recall(
            normalized
        ):
            return None

        question_type = (
            self.detect_question_type(
                normalized
            )
        )

        # ----------------------------------------
        # Force contextual question types
        # ----------------------------------------

        if normalized in (
            "why",
            "tell me why",
            "explain why",
            "why not",
        ):
            question_type = "reason"

        elif normalized in (
            "which one",
            "which one did you choose",
            "which one did you pick",
            "which did you choose",
            "which did you pick",
            "what did you choose",
            "what did you pick",
        ):
            question_type = "choice"

        elif normalized in (
            "what were the other options",
            "what was the other option",
            "what about the other option",
            "what about the other one",
        ):
            question_type = "alternatives"

        print(
            "[DECISION RECALL] "
            "Contextual question:",
            question_type
        )

        # ----------------------------------------
        # Select contextual decision
        # ----------------------------------------

        decision = None

        # IMPORTANT:
        #
        # "why not?" specifically refers to the
        # latest comparison decision.
        #
        # This prevents another unrelated decision
        # from being selected when multiple decisions
        # exist in memory.

        if normalized == "why not":

            comparisons = (
                decision_memory.find_by_type(
                    "comparison"
                )
            )

            if comparisons:

                decision = (
                    comparisons[0]
                )

                print(
                    "[DECISION RECALL] "
                    "Latest comparison decision selected."
                )

        # ----------------------------------------
        # Fallback to latest decision
        # ----------------------------------------

        if decision is None:

            decision = (
                decision_memory.latest()
            )

        if not decision:

            print(
                "[DECISION RECALL] "
                "No contextual decision found."
            )

            return None

        print(
            "[DECISION RECALL] "
            "Using latest contextual decision."
        )

        # ----------------------------------------
        # Format contextual response
        # ----------------------------------------

        if question_type == "reason":

            return self.format_reason(
                decision,
                why_not=(
                    normalized == "why not"
                )
            )

        if question_type == "choice":

            return self.format_choice(
                decision
            )

        if question_type == "alternatives":

            return self.format_alternatives(
                decision
            )

        return self.format_recommendation(
            decision
        )


# ============================================================
# GLOBAL DECISION RECALL INSTANCE
# ============================================================

decision_recall = DecisionRecall()