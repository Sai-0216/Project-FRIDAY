"""
Project FRIDAY
Brain / Command Controller
"""

import re

from commands import router
from planner import planner
from intent_dispatcher import dispatcher
from speech import speaker
from intent import intent_engine
from ai import ai
from conversation import conversation
from response_manager import response_manager
from gui import gui
from modules.memory import remember_statement, memory
from decision_recall import decision_recall
from proactive.outcome_memory import proactive_outcome_memory


class Brain:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):
        self.pending_confirmation = None

    # =========================================================
    # MAIN PROCESSOR
    # =========================================================

    def process(
        self,
        command: str
    ) -> bool:

        print(
            f"Brain received: '{command}'"
        )

        # =====================================================
        # GET PREVIOUS USER COMMAND
        # =====================================================

        previous_command = (
            conversation.get_last_user_message()
        )

        # =====================================================
        # SAVE CURRENT USER COMMAND
        # =====================================================

        conversation.add_user(
            command
        )

        # =====================================================
        # NORMALIZE
        # =====================================================

        normalized = (
            str(command)
            .lower()
            .strip()
        )

        # =====================================================
        # PROACTIVE CONFIRMATION
        #
        # A proactive decision may be waiting for
        # confirmation.
        #
        # The decision contains structured metadata.
        #
        # Outcome memory records:
        #
        #   YES -> confirmed
        #   NO  -> rejected
        #
        # Only proactive CONFIRM decisions are recorded here.
        # Normal confirmations elsewhere in FRIDAY are not
        # treated as proactive outcomes.
        # =====================================================

        if self.pending_confirmation:

            confirmation_words = (
                "yes",
                "yeah",
                "yep",
                "yes sir",
                "sure",
                "okay",
                "ok",
                "do it",
                "confirm",
                "go ahead",
            )

            rejection_words = (
                "no",
                "nope",
                "no sir",
                "cancel",
                "stop",
                "don't",
                "dont",
                "never mind",
                "nevermind",
            )

            # =================================================
            # USER ACCEPTED
            # =================================================

            if normalized in confirmation_words:

                pending = (
                    self.pending_confirmation
                )

                # -------------------------------------------------
                # RECORD PROACTIVE CONFIRMATION OUTCOME
                # -------------------------------------------------

                if (
                    isinstance(
                        pending,
                        dict
                    )
                    and pending.get(
                        "action"
                    ) == "CONFIRM"
                    and pending.get(
                        "_proactive",
                        False
                    )
                ):

                    context = pending.get(
                        "context",
                        {}
                    )

                    attention = context.get(
                        "attention",
                        {}
                    )

                    proactive_outcome_memory.record(
                        event_type=pending.get(
                            "event_type",
                            "UNKNOWN"
                        ),
                        action=pending.get(
                            "action",
                            "CONFIRM"
                        ),
                        attention_level=attention.get(
                            "level",
                            "UNKNOWN"
                        ),
                        outcome="confirmed",
                        intent=pending.get(
                            "intent"
                        ),
                        reason=pending.get(
                            "reason"
                        )
                    )

                # -------------------------------------------------
                # CLEAR CONFIRMATION STATE
                #
                # This prevents the same confirmation from
                # being executed more than once.
                # -------------------------------------------------

                self.pending_confirmation = None

                # -------------------------------------------------
                # VERIFY PROACTIVE DECISION
                # -------------------------------------------------

                if (
                    isinstance(
                        pending,
                        dict
                    )
                    and pending.get(
                        "action"
                    ) == "CONFIRM"
                ):

                    intent_name = pending.get(
                        "intent"
                    )

                    parameters = pending.get(
                        "parameters",
                        {}
                    )

                    # -------------------------------------------------
                    # NO INTENT
                    # -------------------------------------------------

                    if not intent_name:

                        print(
                            "[BRAIN] Proactive confirmation "
                            "has no executable intent."
                        )

                        response = (
                            "Sorry Sir, I don't have "
                            "an action to execute."
                        )

                        speaker.speak(
                            response
                        )

                        conversation.add_assistant(
                            response
                        )

                        return True

                    # -------------------------------------------------
                    # VALIDATE PARAMETERS
                    # -------------------------------------------------

                    if not isinstance(
                        parameters,
                        dict
                    ):

                        parameters = {}
                        
                        
                    # -------------------------------------------------
                    # RECORD PROACTIVE OUTCOME
                    # -------------------------------------------------

                    proactive_outcome_memory.record(
                        event_type=pending.get(
                            "event_type",
                            "UNKNOWN"
                        ),
                        action=pending.get(
                            "action",
                            "CONFIRM"
                        ),
                        attention_level=(
                            pending.get(
                                "context",
                                {}
                            )
                            .get(
                                "attention",
                                {}
                            )
                            .get(
                                "level",
                                "UNKNOWN"
                            )
                        ),
                        outcome="confirmed",
                        intent=intent_name,
                        reason="User accepted proactive confirmation."
                    )

                    # -------------------------------------------------
                    # BUILD NORMAL DISPATCHER INTENT
                    # -------------------------------------------------

                    dispatcher_intent = {
                        "intent": intent_name,
                        "parameters": parameters,
                    }

                    print(
                        "[BRAIN] Proactive confirmation "
                        "accepted."
                    )
                    

                    print(
                        "[BRAIN] Structured intent:",
                        dispatcher_intent
                    )

                    # -------------------------------------------------
                    # EXISTING DISPATCHER
                    # -------------------------------------------------

                    response = dispatcher.execute(
                        dispatcher_intent
                    )

                    print(
                        "[BRAIN] Proactive dispatcher "
                        "response:",
                        repr(response)
                    )

                    if response:

                        formatted_response = (
                            response_manager.command(
                                response
                            )
                        )

                        if formatted_response:

                            speaker.speak(
                                formatted_response
                            )

                            conversation.add_assistant(
                                formatted_response
                            )

                    return True

                # -------------------------------------------------
                # INVALID PENDING OBJECT
                # -------------------------------------------------

                print(
                    "[BRAIN] Confirmation accepted, "
                    "but pending object is not a "
                    "proactive decision."
                )

                return True

            # =================================================
            # USER REJECTED
            # =================================================

            if normalized in rejection_words:

                
                    
                pending = self.pending_confirmation

                if (
                    isinstance(
                        pending,
                        dict
                    )
                    and pending.get(
                        "action"
                    ) == "CONFIRM"
                ):
                    proactive_outcome_memory.record(
                        event_type=pending.get(
                            "event_type",
                            "UNKNOWN"
                        ),
                        action=pending.get(
                            "action",
                            "CONFIRM"
                        ),
                        attention_level=(
                            pending.get(
                                "context",
                                {}
                            )
                            .get(
                                "attention",
                                {}
                            )
                            .get(
                                "level",
                                "UNKNOWN"
                            )
                        ),
                        outcome="rejected",
                        intent=pending.get(
                            "intent"
                        ),
                        reason="User rejected proactive confirmation."
                    )
                self.pending_confirmation
                

                # -------------------------------------------------
                # RECORD PROACTIVE REJECTION
                # -------------------------------------------------

                if (
                    isinstance(
                        pending,
                        dict
                    )
                    and pending.get(
                        "action"
                    ) == "CONFIRM"
                    and pending.get(
                        "_proactive",
                        False
                    )
                ):

                    context = pending.get(
                        "context",
                        {}
                    )

                    attention = context.get(
                        "attention",
                        {}
                    )

                    proactive_outcome_memory.record(
                        event_type=pending.get(
                            "event_type",
                            "UNKNOWN"
                        ),
                        action=pending.get(
                            "action",
                            "CONFIRM"
                        ),
                        attention_level=attention.get(
                            "level",
                            "UNKNOWN"
                        ),
                        outcome="rejected",
                        intent=pending.get(
                            "intent"
                        ),
                        reason=pending.get(
                            "reason"
                        )
                    )

                print(
                    "[BRAIN] Proactive confirmation "
                    "rejected."
                )

                self.pending_confirmation = None

                response = (
                    "Cancelled, Sir."
                )

                speaker.speak(
                    response
                )

                conversation.add_assistant(
                    response
                )

                return True

            # =================================================
            # INVALID CONFIRMATION RESPONSE
            # =================================================

            print(
                "[BRAIN] Expected yes or no "
                "for pending confirmation."
            )

            speaker.speak(
                "Please say yes or no, Sir."
            )

            return True

        # =====================================================
        # SAVE EXPLICIT PERSONAL MEMORY
        # =====================================================

        remember_statement(
            command
        )

        # =====================================================
        # DECISION MEMORY RECALL
        # =====================================================

        recalled = decision_recall.recall(
            command
        )

        if recalled:

            print(
                "[BRAIN] "
                "Decision memory recall handled."
            )

            speaker.speak(
                recalled
            )

            conversation.add_assistant(
                recalled
            )

            return True

        # =====================================================
        # CONTEXTUAL DECISION RECALL
        # =====================================================

        contextual_recall = (
            decision_recall.contextual_recall(
                command
            )
        )

        if contextual_recall:

            print(
                "[BRAIN] "
                "Contextual decision recall handled."
            )

            speaker.speak(
                contextual_recall
            )

            conversation.add_assistant(
                contextual_recall
            )

            return True

        # =====================================================
        # CONVERSATION CONTEXT
        # =====================================================

        from conversation_context import conversation_context

        original_command = command

        resolved_command = (
            conversation_context.resolve(
                command
            )
        )

        context_was_resolved = (
            resolved_command != command
        )

        if context_was_resolved:

            print(
                "[BRAIN] Context resolved:",
                repr(resolved_command)
            )

            command = resolved_command

            normalized = (
                str(command)
                .lower()
                .strip()
            )

        # =====================================================
        # FAST LOCAL COMMAND PATH
        # =====================================================

        result = router.route(
            command
        )

        if result:

            print(
                "[BRAIN] "
                "Fast local command handled."
            )

            return True

        # =====================================================
        # FAST ARITHMETIC PATH
        # =====================================================

        math_match = re.fullmatch(
            r"(?:what is |calculate )?"
            r"([0-9]+(?:\.[0-9]+)?)"
            r"[ ]*"
            r"(plus|minus|times|multiplied by|divided by|[+\-*/])"
            r"[ ]*"
            r"([0-9]+(?:\.[0-9]+)?)"
            r"\??",
            normalized
        )

        if math_match:

            left = float(
                math_match.group(1)
            )

            operator = (
                math_match.group(2)
            )

            right = float(
                math_match.group(3)
            )

            if operator in (
                "plus",
                "+"
            ):

                result = (
                    left + right
                )

            elif operator in (
                "minus",
                "-"
            ):

                result = (
                    left - right
                )

            elif operator in (
                "times",
                "multiplied by",
                "*"
            ):

                result = (
                    left * right
                )

            elif operator in (
                "divided by",
                "/"
            ):

                if right == 0:

                    result = None

                else:

                    result = (
                        left / right
                    )

            else:

                result = None

            if result is not None:

                if result.is_integer():

                    result = int(
                        result
                    )

                response = (
                    f"The answer is {result}, Sir."
                )

                speaker.speak(
                    response
                )

                conversation.add_assistant(
                    response
                )

                return True

        # =====================================================
        # FAST GREETING PATH
        # =====================================================

        greetings = {
            "hello",
            "hi",
            "hey",
            "hello friday",
            "hi friday",
            "hey friday",
            "good morning",
            "good afternoon",
            "good evening",
        }

        if normalized in greetings:

            response = (
                response_manager.greeting()
            )

            if response:

                speaker.speak(
                    response
                )

                conversation.add_assistant(
                    response
                )

            return True

        # =====================================================
        # CONTEXT-RESOLVED CONVERSATION
        # =====================================================

        if context_was_resolved:

            print(
                "[BRAIN] "
                "Context-resolved conversation."
            )

            print(
                "[BRAIN] "
                "Bypassing Intent Engine and Planner."
            )

            response = self.chat(
                command,
                already_saved=True
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # =====================================================
        # DIRECT AI / KNOWLEDGE PATH
        # =====================================================

        if self.is_conversational(
            normalized
        ):

            print(
                "[BRAIN] "
                "Knowledge/conversation request."
            )

            print(
                "[BRAIN] "
                "Bypassing Intent Engine and Planner."
            )

            response = self.chat(
                command,
                already_saved=True
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # =====================================================
        # DIRECT INTENT DETECTION
        # =====================================================

        intent = intent_engine.detect(
            command
        )

        intent_name = intent.get(
            "intent"
        )

        print(
            f"[BRAIN] Detected Intent: {intent_name}"
        )

        # =====================================================
        # DIRECT INTENT EXECUTION
        # =====================================================

        if intent_name != "unknown":

            # -------------------------------------------------
            # DISRUPTIVE ACTION CONFIRMATION
            # -------------------------------------------------

            if intent_name in (
                "lock_computer",
                "sleep",
                "restart",
                "shutdown",
            ):

                if intent_name == "lock_computer":

                    confirmation_message = (
                        "Are you sure you want to "
                        "lock the computer?"
                    )

                elif intent_name == "sleep":

                    confirmation_message = (
                        "Are you sure you want to "
                        "put the computer to sleep?"
                    )

                elif intent_name == "restart":

                    confirmation_message = (
                        "Are you sure you want to "
                        "restart the computer?"
                    )

                else:

                    confirmation_message = (
                        "Are you sure you want to "
                        "shut down the computer?"
                    )

                print(
                    "[BRAIN] "
                    "Confirmation required."
                )

                confirmed = gui.confirm(
                    confirmation_message
                )

                if not confirmed:

                    print(
                        "[BRAIN] "
                        "Confirmation rejected."
                    )

                    response = (
                        "Cancelled, Sir."
                    )

                    speaker.speak(
                        response
                    )

                    conversation.add_assistant(
                        response
                    )

                    return True

                print(
                    "[BRAIN] "
                    "Confirmation accepted."
                )

            # -------------------------------------------------
            # EXECUTE INTENT
            # -------------------------------------------------

            response = dispatcher.execute(
                intent
            )

            print(
                "Dispatcher Response:",
                repr(response)
            )

            if response:

                formatted_response = (
                    response_manager.command(
                        response
                    )
                )

                if formatted_response:

                    speaker.speak(
                        formatted_response
                    )

                    conversation.add_assistant(
                        formatted_response
                    )

            return True

        # =====================================================
        # CONTEXTUAL COMMANDS
        # =====================================================

        if self.is_contextual(
            normalized
        ):

            if previous_command:

                print(
                    "[BRAIN] "
                    "Context detected."
                )

                print(
                    "[BRAIN] Previous command:",
                    repr(previous_command)
                )

                print(
                    "[BRAIN] Current command:",
                    repr(command)
                )

                contextual_command = (
                    self.resolve_context(
                        normalized,
                        previous_command
                    )
                )

                if contextual_command:

                    print(
                        "[BRAIN] "
                        "Resolved command:",
                        contextual_command
                    )

                    if (
                        contextual_command
                        == previous_command
                    ):

                        print(
                            "[BRAIN] "
                            "Repeating previous command."
                        )

                        plan = planner.plan(
                            previous_command
                        )

                    else:

                        plan = planner.plan(
                            contextual_command
                        )

                    if (
                        plan
                        and plan.get("tasks")
                    ):

                        return self.execute_plan(
                            plan
                        )

        # =====================================================
        # COMPOUND COMMAND
        # =====================================================

        if self.is_compound(
            normalized
        ):

            print(
                "[BRAIN] "
                "Creating execution plan..."
            )

            plan = planner.plan(
                command
            )

            if (
                plan
                and plan.get("tasks")
            ):

                return self.execute_plan(
                    plan
                )

            print(
                "[BRAIN] "
                "Planner returned no executable tasks."
            )

            return True

        # =====================================================
        # UNKNOWN → PLANNER
        # =====================================================

        print(
            "[BRAIN] "
            "Creating execution plan..."
        )

        plan = planner.plan(
            command
        )

        if (
            plan
            and plan.get("tasks")
        ):

            return self.execute_plan(
                plan
            )

        # =====================================================
        # FINAL AI FALLBACK
        # =====================================================

        print(
            "[BRAIN] "
            "No executable plan."
        )

        response = self.chat(
            command,
            already_saved=True
        )

        if response:

            speaker.speak(
                response
            )

        return True

    # =========================================================
    # COMPOUND DETECTION
    # =========================================================

    def is_compound(
        self,
        command
    ):

        command = (
            str(command)
            .lower()
            .strip()
        )

        return (
            "," in command
            or " and then " in command
            or " then " in command
        )

    # =========================================================
    # CONVERSATIONAL DETECTION
    # =========================================================

    def is_conversational(
        self,
        command
    ):

        command = (
            str(command)
            .lower()
            .strip()
        )

        if command.endswith("?"):

            return True

        question_starts = (
            "what ",
            "who ",
            "where ",
            "when ",
            "why ",
            "how ",
            "which ",
            "is ",
            "are ",
            "am i ",
            "can you ",
            "could you ",
            "do you ",
            "did you ",
        )

        if command.startswith(
            question_starts
        ):

            return True

        conversational_phrases = (
            "tell me ",
            "tell me something",
            "explain ",
            "describe ",
            "why do ",
            "how do ",
            "what do ",
            "what does ",
            "i want to know ",
            "i'd like to know ",
            "i would like to know ",
            "can you explain ",
            "could you explain ",
            "teach me ",
            "help me understand ",
        )

        if command.startswith(
            conversational_phrases
        ):

            return True

        return False

    # =========================================================
    # CONTEXTUAL COMMAND DETECTION
    # =========================================================

    def is_contextual(
        self,
        command
    ):

        contextual_phrases = (
            "make it",
            "turn it",
            "increase it",
            "decrease it",
            "raise it",
            "lower it",
            "make that",
            "turn that",
            "increase that",
            "decrease that",
            "do that again",
            "do it again",
            "again",
            "now do that",
            "now do it",
        )

        return any(
            phrase in command
            for phrase in contextual_phrases
        )

    # =========================================================
    # RESOLVE OLD COMMAND CONTEXT
    # =========================================================

    def resolve_context(
        self,
        command,
        previous
    ):

        command = (
            str(command)
            .lower()
            .strip()
        )

        if (
            "make it louder" in command
            or "make that louder" in command
            or "turn it up" in command
            or "turn that up" in command
            or "increase it" in command
            or "increase that" in command
            or "raise it" in command
        ):

            return "increase the volume"

        if (
            "make it quieter" in command
            or "make that quieter" in command
            or "turn it down" in command
            or "turn that down" in command
            or "decrease it" in command
            or "decrease that" in command
            or "lower it" in command
        ):

            return "decrease the volume"

        if (
            "capture it" in command
            or "capture that" in command
            or "screenshot it" in command
            or "screenshot that" in command
        ):

            return "take a screenshot"

        if (
            command == "again"
            or "do it again" in command
            or "do that again" in command
        ):

            return previous

        return None

    # =========================================================
    # EXECUTE PLAN
    # =========================================================

    def execute_plan(
        self,
        plan
    ):

        tasks = plan.get(
            "tasks",
            []
        )

        if not tasks:

            print(
                "[BRAIN] "
                "Plan contains no tasks."
            )

            return True

        print(
            f"[BRAIN] "
            f"Planned {len(tasks)} task(s)."
        )

        try:

            for task in tasks:

                print(
                    "[BRAIN] Executing:",
                    task
                )

                response = (
                    dispatcher.execute(
                        task
                    )
                )

                print(
                    "[BRAIN] Task response:",
                    repr(response)
                )

                if response:

                    formatted_response = (
                        response_manager.command(
                            response
                        )
                    )

                    if formatted_response:

                        speaker.speak(
                            formatted_response
                        )

                        conversation.add_assistant(
                            formatted_response
                        )

            return True

        except Exception as e:

            print(
                "[BRAIN] "
                "Planner execution error:",
                repr(e)
            )

            error_response = (
                response_manager.error(
                    "I couldn't complete that."
                )
            )

            if error_response:

                speaker.speak(
                    error_response
                )

            return True

    # =========================================================
    # AI CONVERSATION
    # =========================================================

    def chat(
        self,
        command: str,
        already_saved=False
    ) -> str:

        try:

            if not already_saved:

                conversation.add_user(
                    command
                )

            lookup = (
                str(command)
                .strip()
                .lower()
                .rstrip(
                    ".,!?;:"
                )
            )

            memory_key = None

            for prefix in (
                "what is my ",
                "what's my ",
                "whats my ",
            ):

                if lookup.startswith(
                    prefix
                ):

                    memory_key = (
                        lookup[
                            len(prefix):
                        ].strip()
                    )

                    break

            if memory_key:

                value = memory.recall(
                    memory_key
                )

                if value is None:

                    value = memory.recall(
                        f"my {memory_key}"
                    )

                    if value is not None:

                        memory_key = (
                            f"my {memory_key}"
                        )

                if value is not None:

                    response = (
                        f"{memory_key} is {value}."
                    )

                    response = (
                        response_manager.ai(
                            response
                        )
                    )

                    conversation.add_assistant(
                        response
                    )

                    print(
                        "[BRAIN] "
                        "Fast personal memory lookup."
                    )

                    return response

            print(
                "[BRAIN] "
                "Sending clean request to AI."
            )

            response = ai.ask(
                command
            )

            response = (
                response_manager.ai(
                    response
                )
            )

            if response:

                conversation.add_assistant(
                    response
                )

            return response

        except Exception as e:

            print(
                f"Conversation error: {e}"
            )

            return response_manager.error(
                "I'm having trouble connecting "
                "to my AI."
            )


# =============================================================
# BRAIN SAFETY WRAPPER
# =============================================================

_original_process = Brain.process


def _safe_process(
    self,
    command
):

    try:

        return _original_process(
            self,
            command
        )

    except Exception as e:

        print(
            "[BRAIN] Processing error:",
            repr(e)
        )

        return True


Brain.process = _safe_process


# =============================================================
# GLOBAL BRAIN INSTANCE
# =============================================================

brain = Brain()