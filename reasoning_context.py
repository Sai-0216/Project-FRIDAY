
"""
Project FRIDAY
Reasoning Context

Combines:
- Permanent memory
- Current semantic conversation topic
- Recent conversation
- Decision / recommendation detection

This module prepares grounded context.
It does not execute commands or make final decisions.
"""

from conversation import conversation
from conversation_context import conversation_context
from modules.memory import memory


class ReasoningContext:

    # ========================================
    # CONFIGURATION
    # ========================================

    MAX_HISTORY_MESSAGES = 6
    MAX_HISTORY_CHARS = 3000

    # ========================================
    # MEMORY
    # ========================================

    def get_memory(self):

        try:

            stored_memory = memory.all()

            if not isinstance(
                stored_memory,
                dict
            ):
                return {}

            return stored_memory

        except Exception as e:

            print(
                "[REASONING] Memory lookup failed:",
                repr(e)
            )

            return {}

    # ========================================
    # CURRENT TOPIC
    # ========================================

    def get_topic(self):

        try:

            topic = (
                conversation_context.get_topic()
            )

            if topic:

                return str(
                    topic
                ).strip()

            return None

        except Exception as e:

            print(
                "[REASONING] Topic lookup failed:",
                repr(e)
            )

            return None

    # ========================================
    # RECENT CONVERSATION
    # ========================================

    def get_recent_conversation(self):

        try:

            messages = (
                conversation.get_messages()
            )

            if not messages:

                return []

            recent_messages = (
                messages[
                    -self.MAX_HISTORY_MESSAGES:
                ]
            )

            result = []
            total_chars = 0

            for message in reversed(
                recent_messages
            ):

                role = str(
                    message.get(
                        "role",
                        ""
                    )
                ).strip()

                content = str(
                    message.get(
                        "content",
                        ""
                    )
                ).strip()

                if not content:

                    continue

                message_chars = len(
                    content
                )

                if (
                    total_chars
                    + message_chars
                    > self.MAX_HISTORY_CHARS
                ):

                    break

                result.insert(
                    0,
                    {
                        "role": role,
                        "content": content
                    }
                )

                total_chars += (
                    message_chars
                )

            return result

        except Exception as e:

            print(
                "[REASONING] Conversation lookup failed:",
                repr(e)
            )

            return []

    # ========================================
    # DECISION DETECTION
    # ========================================

    def detect_decision(
        self,
        prompt
    ):

        prompt = (
            str(prompt)
            .lower()
            .strip()
            .rstrip("?!.,;:")
        )

        # ====================================
        # STRONG DECISION PHRASES
        # ====================================

        strong_phrases = (

            "what should i do",
            "what should i use",
            "what should i choose",
            "what should i focus on",
            "what should i work on",

            "which should i use",
            "which should i choose",

            "which one should i use",
            "which one should i choose",
            "which one should i pick",

            "which is better for me",
            "what is better for me",

            "what would you recommend",
            "what do you recommend",
            "which do you recommend",

            "what would be best for me",
            "what is best for me",

            "what is the best option for me",
            "what option is best for me",

            "can you recommend",

            "recommend something for me",

            "help me choose",
            "help me decide",
            "help me pick",

        )

        if any(
            phrase in prompt
            for phrase in strong_phrases
        ):

            return True

        # ====================================
        # COMPARISON QUESTIONS
        # ====================================

        comparison_phrases = (

            "which is better",
            "which one is better",

            "what is better",
            "what's better",

            "should i use",
            "should i choose",
            "should i pick",
            "should i go with",

            "is it better to use",
            "would it be better to use",

            "compare",

            "difference between",

            "better option",

        )

        if any(
            phrase in prompt
            for phrase in comparison_phrases
        ):

            return True

        # ====================================
        # PRIORITY QUESTIONS
        # ====================================

        priority_phrases = (

            "what should i prioritize",
            "what should i prioritize first",

            "what should i do first",

            "what should i start with",

            "where should i start",

            "what should i tackle first",

            "what should i focus on first",

            "what is most important",
            "what's most important",

            "what matters most",

            "what should come first",

            "what should i work on first",

        )

        if any(
            phrase in prompt
            for phrase in priority_phrases
        ):

            return True

        return False

    # ========================================
    # DECISION TYPE
    # ========================================

    def get_decision_type(
        self,
        prompt
    ):

        prompt = (
            str(prompt)
            .lower()
            .strip()
            .rstrip("?!.,;:")
        )

        # ====================================
        # PRIORITY
        # ====================================

        priority_markers = (

            "prioritize",

            "do first",

            "start with",

            "focus on",

            "most important",

            "matters most",

            "work on first",

            "tackle first",

            "what should i focus on",

            "what should i focus on first",

            "what should i prioritize",

            "what should i prioritize first",

            "what should i do first",

            "what should i start with",

            "what should i work on first",

        )

        if any(
            marker in prompt
            for marker in priority_markers
        ):

            return "priority"

        # ====================================
        # EXPLICIT COMPARISON
        # ====================================
        #
        # Do not classify every "should I use"
        # question as a comparison.
        #
        # Example:
        #
        #   "what should i use for my project?"
        #
        # is a recommendation.
        #
        # Example:
        #
        #   "should i use python or java?"
        #
        # is a comparison.
        #
        # ====================================

        comparison_markers = (

            "compare",
            "comparison",

            "difference between",

            "which is better",
            "which one is better",

            "what is better",
            "what's better",

            "better option",

            "versus",
            " vs ",
            " vs.",

            "compared to",

        )

        # ------------------------------------
        # "or" means an actual choice between
        # alternatives in this context.
        # ------------------------------------

        has_or_choice = (
            " or " in prompt
        )

        if (
            any(
                marker in prompt
                for marker in comparison_markers
            )
            or has_or_choice
        ):

            return "comparison"

        # ====================================
        # RECOMMENDATION
        # ====================================

        recommendation_markers = (

            "what should i use",

            "what should i do",

            "what should i choose",

            "which should i use",

            "which should i choose",

            "which one should i use",

            "which one should i choose",

            "which one should i pick",

            "what do you recommend",

            "what would you recommend",

            "which do you recommend",

            "what can you recommend",

            "what would be best for me",

            "what is best for me",

            "what's best for me",

            "what is the best option for me",

            "what's the best option for me",

            "what option is best for me",

            "can you recommend",

            "recommend something for me",

            "help me choose",

            "help me decide",

            "help me pick",

            "what would you suggest",

            "what do you suggest",

        )

        if any(
            marker in prompt
            for marker in recommendation_markers
        ):

            return "recommendation"

        return None

    # ========================================
    # DECISION CONTEXT
    # ========================================

    def get_decision_context(
        self,
        prompt
    ):

        is_decision = (
            self.detect_decision(
                prompt
            )
        )

        if not is_decision:

            return {
                "is_decision": False,
                "type": None,
            }

        return {
            "is_decision": True,
            "type": self.get_decision_type(
                prompt
            ),
        }

    # ========================================
    # RELEVANT MEMORY
    # ========================================

    def get_relevant_memory(
        self,
        prompt
    ):

        prompt = (
            str(prompt)
            .lower()
            .strip()
        )

        stored_memory = (
            self.get_memory()
        )

        if not stored_memory:

            return {}

        relevant = {}

        # ====================================
        # EXPLICIT MEMORY REFERENCES
        # ====================================

        memory_rules = {

            "editor": (
                "my favourite editor",
            ),

            "favorite editor": (
                "my favourite editor",
            ),

            "favourite editor": (
                "my favourite editor",
            ),

            "language": (
                "my favourite language",
                "my learning language",
            ),

            "programming language": (
                "my favourite language",
                "my learning language",
            ),

            "learning": (
                "my learning language",
            ),

            "studying": (
                "my learning language",
            ),

            "project": (
                "my project",
            ),

            "building": (
                "my project",
            ),

            "working on": (
                "my project",
            ),

        }

        for keyword, keys in memory_rules.items():

            if keyword in prompt:

                for key in keys:

                    value = (
                        stored_memory.get(
                            key
                        )
                    )

                    if value is not None:

                        relevant[key] = value

        # ====================================
        # DECISION / RECOMMENDATION REQUESTS
        # ====================================

        decision_data = (
            self.get_decision_context(
                prompt
            )
        )

        if decision_data.get(
            "is_decision"
        ):

            decision_keys = (

                "my favourite editor",
                "my favourite language",
                "my learning language",
                "my project",

            )

            for key in decision_keys:

                value = (
                    stored_memory.get(
                        key
                    )
                )

                if value is not None:

                    relevant[key] = value

        # ====================================
        # PERSONAL / FOCUSED QUESTIONS
        # ====================================

        personal_markers = (

            "my project",
            "my editor",

            "my favourite",
            "my favorite",

            "i am learning",
            "i'm learning",

            "i am studying",
            "i'm studying",

            "i use",
            "i prefer",

        )

        if any(
            marker in prompt
            for marker in personal_markers
        ):

            for key, value in stored_memory.items():

                if value is not None:

                    relevant[key] = value

        return relevant

    # ========================================
    # BUILD REASONING CONTEXT
    # ========================================

    def build(
        self,
        prompt
    ):

        prompt = str(
            prompt
        ).strip()

        memory_data = (
            self.get_relevant_memory(
                prompt
            )
        )

        topic = (
            self.get_topic()
        )

        recent_history = (
            self.get_recent_conversation()
        )

        decision_data = (
            self.get_decision_context(
                prompt
            )
        )

        return {

            "request": prompt,

            "topic": topic,

            "memory": memory_data,

            "conversation": recent_history,

            "decision": decision_data,

        }

    # ========================================
    # TEXT FORMAT
    # ========================================

    def to_prompt(
        self,
        prompt
    ):

        context = (
            self.build(
                prompt
            )
        )

        sections = []

        # ====================================
        # DECISION INFORMATION
        # ====================================

        decision = context.get(
            "decision",
            {}
        )

        if decision.get(
            "is_decision"
        ):

            decision_type = (
                decision.get(
                    "type"
                )
            )

            if decision_type:

                sections.append(
                    "DECISION REQUEST:\n"
                    f"Type: {decision_type}"
                )

            else:

                sections.append(
                    "DECISION REQUEST:\n"
                    "Type: general"
                )

        # ====================================
        # ACTIVE TOPIC
        # ====================================

        topic = context.get(
            "topic"
        )

        if topic:

            sections.append(
                "ACTIVE CONVERSATION TOPIC:\n"
                f"{topic}"
            )

        # ====================================
        # RELEVANT MEMORY
        # ====================================

        memory_data = context.get(
            "memory",
            {}
        )

        if memory_data:

            memory_lines = []

            for key, value in memory_data.items():

                memory_lines.append(
                    f"- {key}: {value}"
                )

            sections.append(
                "RELEVANT PERMANENT MEMORY:\n"
                + "\n".join(
                    memory_lines
                )
            )

        # ====================================
        # RECENT CONVERSATION
        # ====================================

        recent_history = context.get(
            "conversation",
            []
        )

        if recent_history:

            history_lines = []

            for message in recent_history:

                role = (
                    message.get(
                        "role",
                        "user"
                    )
                )

                content = (
                    message.get(
                        "content",
                        ""
                    )
                )

                history_lines.append(
                    f"{role}: {content}"
                )

            sections.append(
                "RECENT CONVERSATION:\n"
                + "\n".join(
                    history_lines
                )
            )

        # ====================================
        # CURRENT REQUEST
        # ====================================

        sections.append(
            "CURRENT REQUEST:\n"
            f"{prompt}"
        )

        # ====================================
        # FINAL PROMPT
        # ====================================

        return (
            "REASONING CONTEXT\n"
            "=================\n"
            + "\n\n".join(
                sections
            )
        )


reasoning_context = ReasoningContext()