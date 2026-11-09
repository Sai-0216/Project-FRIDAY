"""
Project FRIDAY
Brain / Command Controller
"""

import re

from commands import router
from planner import planner
from intent_dispatcher import dispatcher, approval_manager
from security.authorization import authorize_intent, CONFIRMATION_INTENTS
from speech import speaker
from intent import intent_engine
from ai import ai
from conversation import conversation
from response_manager import response_manager
from gui import gui
from modules.memory import remember_statement, memory
from decision_recall import decision_recall
from proactive.outcome_memory import proactive_outcome_memory
from proactive.state_manager import state_manager
from proactive.conversation_state import conversation_state
from proactive.conversational_memory import conversational_memory
from proactive.intent_continuity import intent_continuity
from proactive.slot_filling import slot_filler
from proactive.context_fusion import ContextFusion


class Brain:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):
        self.pending_confirmation = None
        self.state_manager = state_manager
        self.conversation_state = conversation_state
        self.conversational_memory = conversational_memory
        self.intent_continuity = intent_continuity
        self.slot_filler = slot_filler
        self.context_fusion = None
        self.fused_context = {}

    # =========================================================
    # MAIN PROCESSOR
    # =========================================================

    def process(
        self,
        command: str,
        source: str = "unknown",
    ) -> bool:

        if not isinstance(source, str) or source not in {
            "local_voice", "remote", "unknown"
        }:
            source = "unknown"

        if getattr(self, "pending_confirmation", None) and source != "local_voice":
            print(
                "[BRAIN] Blocked non-local command while "
                "confirmation is pending:",
                source,
            )
            return True


        print(
            f"Brain received: '{command}'"
        )

        self.state_manager.begin(command)
        print("[COGNITIVE] State: UNDERSTANDING")

        # =====================================================
        # GET PREVIOUS USER COMMAND
        # =====================================================

        previous_command = (
            conversation.get_last_user_message()
        )

        self.conversation_state.begin_turn(
            command,
            previous_user_message=previous_command,
        )

        print(
            "[CONVERSATION] Turn:",
            self.conversation_state.turn_count,
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

                    approval_token = None
                    proactive_authorization = authorize_intent(
                        dispatcher_intent
                    )

                    if proactive_authorization["status"] == "CONFIRM":
                        if dispatcher_intent.get("intent") == "run_workflow":
                            workflow_approval_payload = dispatcher.approval_actions(
                                dispatcher_intent
                            )
                            if not workflow_approval_payload:
                                response = (
                                    "I cannot run that workflow because its action list "
                                    "is empty or contains an invalid action, Sir."
                                )
                                speaker.speak(response)
                                conversation.add_assistant(response)
                                return True

                            workflow_actions = workflow_approval_payload[1]["workflow_actions"]
                            action_lines = "\n".join(
                                f"{index}. {action!r}"
                                for index, action in enumerate(workflow_actions, start=1)
                            )
                            confirmed_workflow = gui.confirm(
                                "The proactive request needs separate approval for "
                                "this exact workflow action sequence:\n" + action_lines
                            )
                            if not confirmed_workflow:
                                response = "Workflow execution cancelled, Sir."
                                speaker.speak(response)
                                conversation.add_assistant(response)
                                return True

                            approval_token = approval_manager.issue(
                                workflow_approval_payload
                            )
                        else:
                            approval_token = approval_manager.issue(
                                [dispatcher_intent]
                            )

                    self.state_manager.transition("EXECUTING")
                    print("[COGNITIVE] State: EXECUTING")
                    response = dispatcher.execute(
                        dispatcher_intent,
                        approval_token=approval_token,
                    )
                    self.state_manager.add_execution_result({
                        "intent": dispatcher_intent,
                        "response": response,
                        "error": getattr(dispatcher, "last_execution_error", None),
                    })

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
        from proactive.dialogue_context import dialogue_context

        self.context_fusion = ContextFusion(
            conversation_state=self.conversation_state,
            dialogue_context=dialogue_context,
            intent_continuity=self.intent_continuity,
            conversational_memory=self.conversational_memory,
            conversation_context=conversation_context,
        )


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

        self.state_manager.update(resolved_command=command)

        self.conversation_state.update_resolved_command(
            command
        )

        print("[COGNITIVE] Resolved command:", repr(command))
        self.state_manager.transition("PLANNING")
        print("[COGNITIVE] State: PLANNING")

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

            continuity = self.intent_continuity.resolve(
                command,
                "knowledge",
                {},
                dialogue_context,
            )

            if continuity["continued"]:

                print(
                    "[COGNITIVE] "
                    "Intent continuity:",
                    continuity["previous_intent"],
                    "→",
                    continuity["intent"],
                )

            self.conversation_state.update_intent(
                continuity["intent"],
                continuity["parameters"],
            )

            self.intent_continuity.update(
                continuity["intent"],
                continuity["parameters"],
                dialogue_context.get_topic(),
            )

            self.fused_context = (
                self.context_fusion.build(
                    command=original_command
                )
            )

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

        parameters = intent.get("parameters", {})

        continuity = self.intent_continuity.resolve(
            command,
            intent_name,
            parameters,
            dialogue_context,
        )

        intent_name = continuity["intent"]
        parameters = continuity["parameters"]

        # =====================================================
        # MULTI-TURN SLOT FILLING
        # =====================================================

        pending_state = (
            self.conversation_state.snapshot()
            .get("pending_slots")
            or {}
        )

        if (
            pending_state.get("active")
            and not self.slot_filler.has_pending()
        ):
            self.slot_filler.restore_pending(
                pending_state.get("intent"),
                pending_state.get("parameters"),
                pending_state.get("missing"),
            )
        slot_result = self.slot_filler.resolve(
            command,
            intent_name,
            parameters,
            self.intent_continuity.previous_intent,
            self.intent_continuity.previous_parameters,
        )

        if slot_result.get("transitioned"):
            self.conversation_state.clear_pending_slots()
            print(
                "[BRAIN] Slot filling transitioned:",
                slot_result.get("previous_intent"),
                "->",
                slot_result.get("intent"),
            )

        if slot_result.get("cancelled"):
            self.conversation_state.clear_pending_slots()
            print(
                "[BRAIN] Slot filling cancelled."
            )
            speaker.speak(
                "Okay, cancelled."
            )
            return True

        intent_name = slot_result["intent"]
        parameters = slot_result["parameters"]
        missing_slots = slot_result["missing"]
        validation = slot_result.get("validation")

        # Keep the detected intent synchronized with the
        # slot-filled parameters before execution.
        intent["intent"] = intent_name
        intent["parameters"] = parameters

        pending_lifecycle = slot_result.get("pending", bool(missing_slots))

        if pending_lifecycle and missing_slots:
            self.slot_filler.arm(
                intent_name,
                parameters,
            )
            self.conversation_state.update_pending_slots(
                intent_name,
                parameters,
                missing_slots,
            )
        else:
            self.conversation_state.clear_pending_slots()

        if continuity["continued"]:

            print(
                "[COGNITIVE] "
                "Intent continuity:",
                continuity["previous_intent"],
                "->",
                intent_name,
            )

        self.state_manager.update(
            intent=intent_name,
            parameters=parameters,
        )

        self.conversation_state.update_intent(
            intent_name,
            parameters,
        )

        self.intent_continuity.update(
            intent_name,
            parameters,
            dialogue_context.get_topic(),
        )

        self.fused_context = (
            self.context_fusion.build(
                command=original_command
            )
        )

        print("[COGNITIVE] Intent:", intent_name)

        # =====================================================
        # DIRECT INTENT EXECUTION
        # =====================================================

        if (
            validation
            and not validation.get("valid")
        ):
            prompt = validation.get(
                "prompt"
            )

            if prompt:
                print(
                    "[BRAIN] Slot validation:",
                    validation.get("reason")
                )

                speaker.speak(
                    prompt
                )

                return True
        if missing_slots:
            slot_name = missing_slots[0].replace(
                "_",
                " "
            )

            print(
                "[BRAIN] Awaiting required slot:",
                slot_name
            )

            speaker.speak(
                f"I need the {slot_name}."
            )

            return True
        if intent_name != "unknown":
            approval_token = None
            approval_payload = None

            # -------------------------------------------------
            # DISRUPTIVE ACTION CONFIRMATION
            # -------------------------------------------------

            if intent_name in CONFIRMATION_INTENTS:

                if intent_name == "run_workflow":
                    approval_payload = dispatcher.approval_actions(intent)
                    if not approval_payload:
                        response = (
                            "I cannot run that workflow because its action list "
                            "is empty or contains an invalid action, Sir."
                        )
                        speaker.speak(response)
                        conversation.add_assistant(response)
                        return True

                    workflow_actions = approval_payload[1]["workflow_actions"]
                    action_lines = "\n".join(
                        f"{index}. {action!r}"
                        for index, action in enumerate(workflow_actions, start=1)
                    )
                    confirmation_message = (
                        f"Approve running workflow '{intent.get('parameters', {}).get('workflow', '')}' "
                        "with this exact action sequence?\n" + action_lines
                    )

                elif intent_name == "lock_computer":

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

                elif intent_name == "shutdown":

                    confirmation_message = (
                        "Are you sure you want to "
                        "shut down the computer?"
                    )

                else:

                    action_label = intent_name.replace("_", " ")
                    confirmation_message = (
                        f"Are you sure you want to {action_label}?"
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

                confirmation_authorization = authorize_intent(intent)

                if confirmation_authorization["status"] == "CONFIRM":
                    if approval_payload is None:
                        approval_payload = dispatcher.approval_actions(intent)
                    if approval_payload is not None:
                        approval_token = approval_manager.issue(approval_payload)

            # -------------------------------------------------
            # EXECUTE INTENT
            # -------------------------------------------------

            self.state_manager.transition("EXECUTING")
            print("[COGNITIVE] State: EXECUTING")

            response = dispatcher.execute(
                intent,
                approval_token=approval_token,
            )
            self.state_manager.add_execution_result({
                "intent": intent,
                "response": response,
                "error": getattr(dispatcher, "last_execution_error", None),
            })

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

            if self.state_manager.current().lifecycle != "EVALUATING":
                self.state_manager.complete()

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

        self.state_manager.transition("PLANNING")
        plan = planner.plan(
            command
        )
        self.state_manager.update(
            plan=plan.get("tasks", []) if isinstance(plan, dict) else []
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

        self.state_manager.update(plan=tasks)
        self.state_manager.transition("EXECUTING")
        print("[COGNITIVE] State: EXECUTING")

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
                execution_error = getattr(
                    dispatcher,
                    "last_execution_error",
                    None,
                )

                print(
                    "[BRAIN] Task response:",
                    repr(response)
                )

                self.state_manager.add_execution_result({
                    "task": task,
                    "response": response,
                    "error": execution_error,
                })

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

                authorization_result = getattr(
                    dispatcher,
                    "last_authorization_result",
                    None,
                )

                if (
                    isinstance(authorization_result, dict)
                    and authorization_result.get("status") != "ALLOW"
                ):
                    print(
                        "[SECURITY] Stopping plan after an "
                        "unauthorized or unapproved task."
                    )
                    break

                if execution_error:
                    print(
                        "[BRAIN] Stopping plan after task execution failure:",
                        repr(execution_error),
                    )
                    break

            return True

        except Exception as e:

            print(
                "[BRAIN] "
                "Planner execution error:",
                repr(e)
            )

            self.state_manager.fail(repr(e))
            print("[COGNITIVE] State: IDLE")

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

    def _remember_conversational_turn(
        self,
        user_message,
        assistant_message,
    ):
        self.conversational_memory.remember_turn(
            user_message=user_message,
            assistant_message=assistant_message,
            topic=self.conversation_state.active_topic,
            intent=self.conversation_state.last_intent,
            resolved_command=self.conversation_state.last_resolved_command,
        )

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

            # Explicit recall of the most recent free-form note.
            if lookup in {
                "what did i just say to remember",
                "what did i ask you to remember",
                "what did i tell you to remember",
                "what was the thing i asked you to remember",
                "what did i ask you to remember just now",
            }:
                note = memory.latest_remembered_note()
                response = (
                    f"You asked me to remember that {note}."
                    if note
                    else "I don't have a recently saved note to recall."
                )
                response = response_manager.ai(response)
                conversation.add_assistant(response)
                self._remember_conversational_turn(command, response)
                return response

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

                    self._remember_conversational_turn(
                        command,
                        response,
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
                command,
                fused_context=self.fused_context,
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

                self._remember_conversational_turn(
                    command,
                    response,
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
    command,
    source="unknown",
):

    if not isinstance(source, str) or source not in {
        "local_voice", "remote", "unknown"
    }:
        source = "unknown"

    if getattr(self, "pending_confirmation", None) and source != "local_voice":
        print(
            "[BRAIN] Blocked non-local command before lifecycle handling:",
            source,
        )
        return True

    try:

        result = _original_process(
            self,
            command,
            source=source,
        )

        state = self.state_manager.current()

        if state.lifecycle != "IDLE" and state.outcome != "failed":
            self.state_manager.complete()
            state = self.state_manager.current()

        if state.outcome == "failed":
            self.conversation_state.fail(
                getattr(state, "error", None) or "Execution failed"
            )
        else:
            self.conversation_state.complete_turn()

        if state.lifecycle == "IDLE":
            print("[COGNITIVE] State: IDLE")

        return result

    except Exception as e:

        print(
            "[BRAIN] Processing error:",
            repr(e)
        )

        # Recover cognitive state without blocking conversation recovery.
        try:
            state = self.state_manager.current()

            if state.lifecycle == "IDLE":
                if not state.outcome:
                    self.state_manager.begin(command)
                    self.state_manager.fail(repr(e))
            elif state.outcome != "failed":
                self.state_manager.fail(repr(e))

            print("[COGNITIVE] State: IDLE")
        except Exception as state_error:
            print("[COGNITIVE] State recovery error:", repr(state_error))

        # This must remain independent of cognitive-state recovery.
        try:
            self.conversation_state.fail(repr(e))
        except Exception as conversation_error:
            print(
                "[CONVERSATION] Recovery error:",
                repr(conversation_error)
            )

        return True


Brain.process = _safe_process


# =============================================================
# GLOBAL BRAIN INSTANCE
# =============================================================

brain = Brain()
