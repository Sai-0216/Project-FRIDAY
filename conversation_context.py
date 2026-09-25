"""
Project FRIDAY
Conversation Context
"""

import re

from conversation import conversation
from modules.memory import memory


class ConversationContext:

    def __init__(self):
        self.topic = None
        self.topic_history = []

    # ========================================
    # GET LAST USER MESSAGE
    # ========================================

    def last_user_message(self):

        messages = conversation.get_messages()

        for message in reversed(messages):

            if message.get("role") == "user":

                return message.get(
                    "content",
                    ""
                )

        return None

    # ========================================
    # GET LAST ASSISTANT MESSAGE
    # ========================================

    def last_assistant_message(self):

        messages = conversation.get_messages()

        for message in reversed(messages):

            if message.get("role") == "assistant":

                return message.get(
                    "content",
                    ""
                )

        return None

    # ========================================
    # NORMALIZE
    # ========================================

    def normalize(self, text):

        text = (
            str(text)
            .lower()
            .strip()
        )

        text = text.rstrip(
            ".,!?;:"
        ).strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    # ========================================
    # DETECT FOLLOW-UP
    # ========================================

    def is_follow_up(self, command):

        command = self.normalize(
            command
        )

        follow_up_phrases = [

            # ----------------------------------------
            # Tell me more
            # ----------------------------------------

            "tell me more",
            "tell me more about it",
            "tell me more about that",

            # ----------------------------------------
            # Explain
            # ----------------------------------------

            "explain it",
            "explain that",

            # ----------------------------------------
            # What about
            # ----------------------------------------

            "what about it",
            "what about that",

            # ----------------------------------------
            # Why
            # ----------------------------------------

            "why",
            "why is it",
            "why is that",

            # ----------------------------------------
            # How
            # ----------------------------------------

            "how does it",
            "how does that",

            # ----------------------------------------
            # Next step
            # ----------------------------------------

            "what should i do next",
            "what should we do next",

            "what next",
            "then what",

            # ----------------------------------------
            # Continue
            # ----------------------------------------

            "and then",
            "continue",
            "go on",

        ]

        if command in follow_up_phrases:

            return True

        for phrase in follow_up_phrases:

            if command.startswith(
                phrase + " "
            ):

                return True

        return False

    # ========================================
    # DETECT PRONOUN REFERENCE
    # ========================================

    def has_reference(self, command):

        command = self.normalize(
            command
        )

        reference_words = [

            "it",
            "that",
            "this",
            "its",
            "they",
            "them",
            "he",
            "she",

        ]

        words = command.split()

        return any(
            word in reference_words
            for word in words
        )

    # ========================================
    # GET SEMANTIC TOPIC
    # ========================================

    def get_semantic_topic(self, topic):

        if not topic:
            return None

        try:

            stored_memory = (
                memory.all()
            )

        except Exception as memory_error:

            print(
                "[CONTEXT] Memory lookup failed:",
                repr(memory_error)
            )

            return topic

        # ----------------------------------------
        # Editor
        # ----------------------------------------

        if topic == "editor":

            editor = stored_memory.get(
                "my favourite editor"
            )

            if editor:

                return str(editor).strip()

        # ----------------------------------------
        # Project
        # ----------------------------------------

        if topic == "my project":

            project = stored_memory.get(
                "my project"
            )

            if project:

                return str(project).strip()

        # ----------------------------------------
        # Favourite programming language
        # ----------------------------------------

        if topic == "programming language":

            language = stored_memory.get(
                "my favourite language"
            )

            if language:

                return str(language).strip()

        # ----------------------------------------
        # Learning language
        # ----------------------------------------

        if topic == "learning language":

            language = stored_memory.get(
                "my learning language"
            )

            if language:

                return str(language).strip()

        return topic

    # ========================================
    # EXTRACT TOPIC
    # ========================================

    def extract_topic(self, command):

        command = self.normalize(
            command
        )

        # ----------------------------------------
        # Editor / IDE
        # ----------------------------------------

        if (
            "editor" in command
            or "ide" in command
        ):

            return "editor"

        # ----------------------------------------
        # Project
        # ----------------------------------------

        if "my project" in command:

            return "my project"

        if "the project" in command:

            return "the project"

        # ----------------------------------------
        # Programming language
        # ----------------------------------------

        if (
            "programming language"
            in command
        ):

            return "programming language"

        if (
            "favourite language"
            in command
            or "favorite language"
            in command
        ):

            return "programming language"

        # ----------------------------------------
        # Python
        # ----------------------------------------

        if "python" in command:

            return "python"

        # ----------------------------------------
        # Java
        # ----------------------------------------

        if "java" in command:

            return "java"

        # ----------------------------------------
        # FRIDAY
        # ----------------------------------------

        if "friday" in command:

            return "friday"

        # ----------------------------------------
        # Memory
        # ----------------------------------------

        if (
            "memory" in command
            or "remember" in command
        ):

            return "memory"

        # ----------------------------------------
        # Workflow
        # ----------------------------------------

        if "workflow" in command:

            return "workflow"

        # ----------------------------------------
        # Volume
        # ----------------------------------------

        if (
            "volume" in command
            or "louder" in command
            or "quieter" in command
        ):

            return "volume"

        # ----------------------------------------
        # Spotify
        # ----------------------------------------

        if "spotify" in command:

            return "spotify"

        # ----------------------------------------
        # Browser
        # ----------------------------------------

        if (
            "chrome" in command
            or "browser" in command
            or "google" in command
        ):

            return "browser"

        return None

    # ========================================
    # UPDATE TOPIC
    # ========================================

    def update_topic(self, command):

        topic = self.extract_topic(
            command
        )

        if not topic:

            return self.topic

        # ----------------------------------------
        # Resolve category to actual subject
        # ----------------------------------------

        semantic_topic = (
            self.get_semantic_topic(
                topic
            )
        )

        if not semantic_topic:

            semantic_topic = topic

        # ----------------------------------------
        # Same topic
        # ----------------------------------------

        if semantic_topic == self.topic:

            return self.topic

        # ----------------------------------------
        # Save previous topic
        # ----------------------------------------

        if self.topic:

            if (
                not self.topic_history
                or self.topic_history[-1]
                != self.topic
            ):

                self.topic_history.append(
                    self.topic
                )

        # ----------------------------------------
        # Set semantic topic
        # ----------------------------------------

        self.topic = semantic_topic

        return self.topic

    # ========================================
    # GET CURRENT TOPIC
    # ========================================

    def get_topic(self):

        return self.topic

    # ========================================
    # GET PREVIOUS TOPIC
    # ========================================

    def get_previous_topic(self):

        if not self.topic_history:

            return None

        return self.topic_history[-1]

    # ========================================
    # GET TOPIC HISTORY
    # ========================================

    def get_topic_history(self):

        return list(
            self.topic_history
        )

    # ========================================
    # DETECT GO-BACK COMMAND
    # ========================================

    def is_go_back(self, command):

        command = self.normalize(
            command
        )

        go_back_phrases = [

            "go back",
            "go back to it",
            "go back to that",

            "go back to my project",
            "go back to the project",

            "return to it",
            "return to that",

            "switch back",
            "switch back to it",
            "switch back to that",

            "talk about it again",
            "talk about that again",

        ]

        if command in go_back_phrases:

            return True

        return False

    # ========================================
    # RESOLVE GO-BACK
    # ========================================

    def resolve_go_back(self, command):

        command = self.normalize(
            command
        )

        # ========================================
        # EXPLICIT PROJECT
        # ========================================

        if (
            "my project"
            in command
            or "the project"
            in command
        ):

            return self.switch_to_topic(
                self.get_semantic_topic(
                    "my project"
                )
            )

        # ========================================
        # EXPLICIT LANGUAGE
        # ========================================

        if (
            "programming language"
            in command
            or "favourite language"
            in command
            or "favorite language"
            in command
        ):

            return self.switch_to_topic(
                self.get_semantic_topic(
                    "programming language"
                )
            )

        # ========================================
        # EXPLICIT EDITOR
        # ========================================

        if (
            "editor" in command
            or "ide" in command
        ):

            return self.switch_to_topic(
                self.get_semantic_topic(
                    "editor"
                )
            )

        # ========================================
        # EXPLICIT PYTHON
        # ========================================

        if "python" in command:

            return self.switch_to_topic(
                "python"
            )

        # ========================================
        # EXPLICIT JAVA
        # ========================================

        if "java" in command:

            return self.switch_to_topic(
                "java"
            )

        # ========================================
        # NORMAL GO-BACK
        # ========================================

        previous_topic = (
            self.get_previous_topic()
        )

        if not previous_topic:

            return None

        return self.switch_to_topic(
            previous_topic
        )

    # ========================================
    # SWITCH TOPIC
    # ========================================

    def switch_to_topic(self, topic):

        if not topic:

            return None

        old_topic = self.topic

        # ----------------------------------------
        # Already on topic
        # ----------------------------------------

        if old_topic == topic:

            return topic

        # ----------------------------------------
        # Remove requested topic from history
        # ----------------------------------------

        self.topic_history = [

            item

            for item in self.topic_history

            if item != topic

        ]

        # ----------------------------------------
        # Save current topic
        # ----------------------------------------

        if old_topic:

            self.topic_history.append(
                old_topic
            )

        # ----------------------------------------
        # Set new topic
        # ----------------------------------------

        self.topic = topic

        return topic

    # ========================================
    # RESOLVE COMMAND
    # ========================================

    def resolve(self, command):

        original_command = str(
            command
        ).strip()

        normalized = self.normalize(
            original_command
        )

        # ========================================
        # GO-BACK
        # ========================================

        if self.is_go_back(
            normalized
        ):

            previous_topic = (
                self.resolve_go_back(
                    normalized
                )
            )

            if previous_topic:

                print(
                    "[CONTEXT] Switching topic to:",
                    previous_topic
                )

                # IMPORTANT:
                #
                # Return a normal conversational
                # request.
                #
                # Do NOT return:
                #
                # "Let's go back to my project"
                #
                # because the planner may interpret
                # that as an action.
                #
                return (
                    f"Tell me about "
                    f"{previous_topic}"
                )

        # ========================================
        # EXPLICIT NEW TOPIC
        # ========================================

        detected_topic = (
            self.extract_topic(
                normalized
            )
        )

        if detected_topic:

            self.update_topic(
                normalized
            )

            return original_command

        # ========================================
        # NO CURRENT TOPIC
        # ========================================

        if not self.topic:

            return original_command

        # ========================================
        # FOLLOW-UP
        # ========================================

        if self.is_follow_up(
            normalized
        ):

            resolved = (
                self.build_follow_up(
                    normalized,
                    self.topic
                )
            )

            return resolved

        # ========================================
        # ========================================
        # REFERENCE RESOLUTION - PHASE 35.3
        # ========================================

        if (
            self.has_reference(normalized)
            or self.is_previous_reference(normalized)
        ):

            return self.resolve_reference(
                normalized
            )

        return original_command

    # ========================================
    # BUILD FOLLOW-UP
    # ========================================

    def build_follow_up(
        self,
        command,
        topic
    ):

        normalized = self.normalize(
            command
        )

        # ----------------------------------------
        # Tell me more
        # ----------------------------------------

        if normalized in (
            "tell me more",
            "tell me more about it",
            "tell me more about that",
        ):

            return (
                f"Tell me more about "
                f"{topic}"
            )

        # ----------------------------------------
        # Explain
        # ----------------------------------------

        if normalized in (
            "explain it",
            "explain that",
        ):

            return (
                f"Explain "
                f"{topic}"
            )

        # ----------------------------------------
        # What about
        # ----------------------------------------

        if normalized in (
            "what about it",
            "what about that",
        ):

            return (
                f"What about "
                f"{topic}?"
            )

        # ----------------------------------------
        # Why
        # ----------------------------------------

        if normalized == "why":

            return (
                f"Why is "
                f"{topic} useful?"
            )

        # ----------------------------------------
        # Why is it
        # ----------------------------------------

        if normalized.startswith(
            "why is it"
        ):

            remainder = normalized[
                len("why is it"):
            ].strip()

            if remainder:

                return (
                    f"Why is "
                    f"{topic} "
                    f"{remainder}?"
                )

            return (
                f"Why is "
                f"{topic}?"
            )

        # ----------------------------------------
        # Why is that
        # ----------------------------------------

        if normalized.startswith(
            "why is that"
        ):

            remainder = normalized[
                len("why is that"):
            ].strip()

            if remainder:

                return (
                    f"Why is "
                    f"{topic} "
                    f"{remainder}?"
                )

            return (
                f"Why is "
                f"{topic}?"
            )

        # ----------------------------------------
        # How does it
        # ----------------------------------------

        if normalized.startswith(
            "how does it"
        ):

            remainder = normalized[
                len("how does it"):
            ].strip()

            if remainder:

                return (
                    f"How does "
                    f"{topic} "
                    f"{remainder}?"
                )

            return (
                f"How does "
                f"{topic} work?"
            )

        # ----------------------------------------
        # How does that
        # ----------------------------------------

        if normalized.startswith(
            "how does that"
        ):

            remainder = normalized[
                len("how does that"):
            ].strip()

            if remainder:

                return (
                    f"How does "
                    f"{topic} "
                    f"{remainder}?"
                )

            return (
                f"How does "
                f"{topic} work?"
            )

        # ----------------------------------------
        # What should I do next
        # ----------------------------------------

        if (
            normalized
            == "what should i do next"
        ):

            return (
                f"What should I do next "
                f"with {topic}?"
            )

        # ----------------------------------------
        # What should we do next
        # ----------------------------------------

        if (
            normalized
            == "what should we do next"
        ):

            return (
                f"What should we do next "
                f"with {topic}?"
            )

        # ----------------------------------------
        # What next
        # ----------------------------------------

        if normalized == "what next":

            return (
                f"What should I do next "
                f"with {topic}?"
            )

        # ----------------------------------------
        # Then what
        # ----------------------------------------

        if normalized == "then what":

            return (
                f"What should I do next "
                f"with {topic}?"
            )

        # ----------------------------------------
        # Continue
        # ----------------------------------------

        if normalized in (
            "continue",
            "go on",
            "and then",
        ):

            return (
                f"Continue talking about "
                f"{topic}"
            )

        return normalized

    # ========================================
    # REPLACE REFERENCES
    # ========================================

    def replace_reference(
        self,
        command,
        topic
    ):

        normalized = self.normalize(
            command
        )

        words = normalized.split()

        result = []

        for word in words:

            if word in (
                "it",
                "that",
                "this",
            ):

                result.append(
                    topic
                )

            else:

                result.append(
                    word
                )

        resolved = " ".join(
            result
        )

        resolved = re.sub(
            r"\s+",
            " ",
            resolved
        ).strip()

        return resolved

    # ========================================
    # CLEAR CONTEXT
    # ========================================

    # ========================================
    # REFERENCE RESOLUTION - PHASE 35.3
    # ========================================

    def is_previous_reference(self, command):

        normalized = self.normalize(
            command
        )

        previous_phrases = (
            "the previous one",
            "previous one",
            "the last one",
            "last one",
            "previous",
            "last",
        )

        return any(
            phrase in normalized
            for phrase in previous_phrases
        )

    def get_reference_target(self, command):

        normalized = self.normalize(
            command
        )

        if self.is_previous_reference(
            normalized
        ):

            return self.get_previous_topic()

        if self.has_reference(
            normalized
        ):

            return self.get_topic()

        return None

    def resolve_reference(
        self,
        command
    ):

        normalized = self.normalize(
            command
        )

        target = self.get_reference_target(
            normalized
        )

        if not target:

            return command

        # ----------------------------------------
        # Previous-item reference
        # ----------------------------------------

        if self.is_previous_reference(
            normalized
        ):

            words = normalized.split()

            result = []

            skip = 0

            for index, word in enumerate(words):

                if skip:
                    skip -= 1
                    continue

                if (
                    word == "the"
                    and index + 2 < len(words)
                    and words[index + 1] == "previous"
                    and words[index + 2] == "one"
                ):

                    result.append(target)
                    skip = 2
                    continue

                if (
                    word == "the"
                    and index + 2 < len(words)
                    and words[index + 1] == "last"
                    and words[index + 2] == "one"
                ):

                    result.append(target)
                    skip = 2
                    continue

                if (
                    word == "previous"
                    and index + 1 < len(words)
                    and words[index + 1] == "one"
                ):

                    result.append(target)
                    skip = 1
                    continue

                if (
                    word == "last"
                    and index + 1 < len(words)
                    and words[index + 1] == "one"
                ):

                    result.append(target)
                    skip = 1
                    continue

                if word in (
                    "previous",
                    "last",
                ):

                    result.append(target)
                    continue

                result.append(word)

            return " ".join(
                result
            )

        # ----------------------------------------
        # Current-topic references
        # ----------------------------------------

        return self.replace_reference(
            normalized,
            target
        )

    def clear(self):

        self.topic = None

        self.topic_history.clear()


conversation_context = (
    ConversationContext()
)



