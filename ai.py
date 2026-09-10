"""
Project FRIDAY
AI Manager

Phase 15.4
Recommendation Engine Integration
"""

import ollama

from conversation import conversation
from memory_context import memory_context
from recommendation_engine import recommendation_engine


class AI:

    # ============================================================
    # CONFIGURATION
    # ============================================================

    MODEL = "qwen2.5:1.5b"

    # Keep conversation context small for speed.
    MAX_HISTORY_MESSAGES = 4

    # Prevent conversation history from growing too large.
    MAX_HISTORY_CHARS = 2500

    # Response limits
    SHORT_RESPONSE_TOKENS = 80
    PERSONALIZED_RESPONSE_TOKENS = 120
    DETAILED_RESPONSE_TOKENS = 220

    # Keep Ollama model loaded.
    KEEP_ALIVE = "30m"

    # ============================================================
    # PERSONALIZATION DETECTION
    # ============================================================

    def _get_personalization_context(self, prompt: str) -> str:
        """
        Detect whether the current request benefits from
        personal preference memory.

        This does not decide the final answer.
        It only gives the AI additional guidance.
        """

        lower_prompt = str(prompt).lower().strip()

        relevant_preferences = memory_context.relevant_preferences(prompt, limit=5)
        profile = memory_context.profile()
        routines = memory_context.routine_profile()
        adaptive_context = memory_context.adaptive_profile_context(prompt)
        adaptive_relevance = memory_context.adaptive_context_relevance(prompt)
        adaptive_sources = adaptive_context.get("selected", {})
        adaptive_weights = adaptive_context.get("weights", {})
        if adaptive_sources:
            ranked_sources = sorted(adaptive_weights.items(), key=lambda item: (-item[1], item[0]))
            source_order = [source for source, _weight in ranked_sources]
        else:
            source_order = []

        editor_markers = (
            "editor",
            "ide",
            "coding editor",
            "code editor",
            "for coding",
            "while coding",
            "when coding",
            "for programming",
            "while programming",
            "when programming",
            "where should i code",
            "what should i code with",
        )

        language_markers = (
            "programming language",
            "programming languages",
            "what language",
            "which language",
            "language should i",
            "language do i",
            "python or java",
            "java or python",
        )

        learning_markers = (
            "what am i learning",
            "what am i studying",
            "which one am i learning",
            "which one am i studying",
            "what language am i learning",
            "which language am i learning",
            "what language am i studying",
            "which language am i studying",
            "learning",
            "studying",
        )

        project_markers = (
            "my project",
            "the project",
            "for my project",
            "in my project",
            "project",
        )

        recommendation_markers = (
            "what should i use",
            "which should i use",
            "what should i choose",
            "which should i choose",
            "which one should i use",
            "which one should i choose",
            "what do you recommend",
            "what would you recommend",
            "what would you suggest",
            "which one do you recommend",
            "best option for me",
            "best choice for me",
        )

        needs_personalization = (
            any(marker in lower_prompt for marker in editor_markers)
            or any(marker in lower_prompt for marker in language_markers)
            or any(marker in lower_prompt for marker in learning_markers)
            or any(marker in lower_prompt for marker in project_markers)
            or any(marker in lower_prompt for marker in recommendation_markers)
            or bool(relevant_preferences)
            or bool(adaptive_relevance.get("relevant"))
            or any(item.get("strength") in ("moderate", "strong") for item in routines.get("routine_candidates", []))
            or bool(relevant_preferences)
        )

        if not needs_personalization:
            return ""

        guidance = []
        trust = profile.get('trust', {})
        weights = profile.get('weights', {})
        evidence_priority = profile.get('evidence_priority', {})
        arbitration = profile.get('arbitration', {})
        arbitration_winner = arbitration.get('winner')
        arbitration_confidence = arbitration.get('confidence', 0.0)
        arbitration_reason = arbitration.get('reason', '')
        decision_confidence = profile.get('decision_confidence', {})
        decision_score = decision_confidence.get('score', 0.5)
        decision_level = str(decision_confidence.get('level', 'medium')).lower()
        personalization_mode = profile.get('personalization_mode', {})
        mode = str(personalization_mode.get('mode', 'selective')).lower()
        mode_score = personalization_mode.get('score', 0.5)
        if mode == 'strong':
            guidance.append(f"Personalization mode is strong (score: {mode_score}); use relevant trusted profile evidence naturally and confidently.")
        elif mode == 'selective':
            guidance.append(f"Personalization mode is selective (score: {mode_score}); use only clearly relevant profile evidence.")
        else:
            guidance.append(f"Personalization mode is cautious (score: {mode_score}); minimize assumptions and rely on explicit current evidence.")
        if decision_level == 'high':
            guidance.append(f"Profile decision confidence is high (score: {decision_score}); personalization decisions can be stated confidently.")
        elif decision_level == 'medium':
            guidance.append(f"Profile decision confidence is medium (score: {decision_score}); personalize with measured confidence.")
        else:
            guidance.append(f"Profile decision confidence is low (score: {decision_score}); avoid overconfident personalization.")
        if arbitration_winner:
            guidance.append(f"Evidence arbitration selected {arbitration_winner} as the preferred profile source (confidence: {arbitration_confidence}). {arbitration_reason}")
        priority_items = evidence_priority.get('priority', [])
        priority_order = [str(item.get('source')).lower() for item in priority_items if isinstance(item, dict) and item.get('source') ]
        if priority_order:
            guidance.append("Profile evidence priority: " + " > ".join(priority_order) + ". Prefer higher-weight evidence when signals compete.")
        preference_weight = weights.get('preferences', 0.5)
        behavior_weight = weights.get('behavior', 0.5)
        memory_weight = weights.get('memories', 0.5)
        if preference_weight >= 0.85:
            guidance.append(f"Preference evidence weight is strong ({preference_weight}); relevant preferences should be prioritized.")
        elif preference_weight >= 0.6:
            guidance.append(f"Preference evidence weight is moderate ({preference_weight}); use relevant preferences selectively.")
        else:
            guidance.append(f"Preference evidence weight is low ({preference_weight}); avoid relying heavily on stored preferences.")
        if behavior_weight >= 0.85:
            guidance.append(f"Behavior evidence weight is strong ({behavior_weight}); recurring behavior can meaningfully guide personalization.")
        elif behavior_weight >= 0.6:
            guidance.append(f"Behavior evidence weight is moderate ({behavior_weight}); use behavioral patterns with some caution.")
        if memory_weight >= 0.85:
            guidance.append(f"Memory evidence weight is strong ({memory_weight}); relevant long-term facts can be used confidently.")
        trust_level = str(trust.get('level', 'medium')).lower()
        trust_score = trust.get('score', 0.5)
        if trust_level == 'high':
            guidance.append(f"Unified profile trust is high (score: {trust_score}). Personalization can rely strongly on relevant profile evidence.")
        elif trust_level == 'medium':
            guidance.append(f"Unified profile trust is medium (score: {trust_score}). Personalize selectively and favor stronger recent evidence.")
        else:
            guidance.append(f"Unified profile trust is low (score: {trust_score}). Avoid strong personalization assumptions.")
        reliability = profile.get('reliability', {})
        consistency = profile.get('consistency', {})
        consistency_level = str(consistency.get('level', 'medium')).lower()
        consistency_score = consistency.get('score', 0.5)
        conflicts = consistency.get('conflicts', 0)
        if consistency_level == 'high':
            guidance.append(f"Profile consistency is high (score: {consistency_score}; conflicts: {conflicts}). Related profile signals agree.")
        elif consistency_level == 'medium':
            guidance.append(f"Profile consistency is medium (score: {consistency_score}; conflicts: {conflicts}). Prefer profile signals supported by multiple pieces of evidence.")
        else:
            guidance.append(f"Profile consistency is low (score: {consistency_score}; conflicts: {conflicts}). Avoid strong personalization assumptions when profile signals disagree.")
        reliability_level = str(reliability.get('level', 'medium')).lower()
        reliability_score = reliability.get('score', 0.5)
        if reliability_level == 'high':
            guidance.append(f"Profile reliability is high (score: {reliability_score}). Relevant profile information can be trusted strongly.")
        elif reliability_level == 'medium':
            guidance.append(f"Profile reliability is medium (score: {reliability_score}). Use relevant profile information selectively and prefer stronger evidence.")
        else:
            guidance.append(f"Profile reliability is low (score: {reliability_score}). Treat profile information cautiously and avoid strong assumptions.")
        freshness = profile.get('freshness', {})
        preference_freshness = freshness.get('preferences', {}).get('status', 'unknown')
        behavior_freshness = freshness.get('behavior', {}).get('status', 'unknown')
        if preference_freshness == 'stale' or behavior_freshness == 'stale':
            guidance.append("Some profile data is stale; treat it cautiously and prefer newer evidence.")
        elif preference_freshness == 'aging' or behavior_freshness == 'aging':
            guidance.append("Some profile data is aging; prefer newer evidence when personalizing.")
        elif preference_freshness == 'fresh' and behavior_freshness == 'fresh':
            guidance.append("Profile data is fresh; recent preferences and behavior can be used confidently when relevant.")

        for routine in routines.get("routine_candidates", []):
            if routine.get("strength") in ("moderate", "strong"):
                guidance.append(f"The user has a recurring routine: {routine.get("command")} around {routine.get("time_window")} (confidence: {routine.get("confidence", 0.0)}).")

        for preference in relevant_preferences:
            preference_text = preference.get("preference")
            if preference_text:
                confidence = str(preference.get("confidence", "MEDIUM")).upper(); strength = "strongly respect" if confidence == "HIGH" else "consider normally" if confidence == "MEDIUM" else "treat cautiously"; trust_strength = ""; trust_level = str(profile.get("trust", {}).get("level", "medium")).lower(); trust_strength = " However, use it cautiously because overall profile trust is low." if trust_level == "low" else " Prefer corroborating profile evidence because overall profile trust is medium." if trust_level == "medium" else ""; guidance.append(f"The user has a stored preference: {preference_text} (confidence: {confidence}). {strength.capitalize()} this preference when it is relevant.{trust_strength}")

        if relevant_preferences and profile.get("memories"):
            guidance.append("Relevant existing user profile context may also be considered when directly relevant.")

        if any(marker in lower_prompt for marker in editor_markers):
            guidance.append(
                "The user's preferred editor is relevant when discussing coding tools."
            )

        if any(marker in lower_prompt for marker in language_markers):
            guidance.append(
                "The user's favourite and learning languages may be relevant."
            )

        if any(marker in lower_prompt for marker in learning_markers):
            guidance.append(
                "The user's learning language is especially relevant."
            )

        if any(marker in lower_prompt for marker in project_markers):
            guidance.append(
                "The user's project should be considered when making a recommendation."
            )

        if any(
            marker in lower_prompt
            for marker in recommendation_markers
        ):
            guidance.append(
                "Personal preferences should be used naturally rather than forcefully."
            )

        if not guidance:
            return ""

        return "\n".join(
            f"- {item}"
            for item in guidance
        )

    # ============================================================
    # RELEVANT MEMORY
    # ============================================================

    def _get_memory_text(self, prompt: str) -> str:
        """
        Retrieve relevant permanent memory.
        """

        try:
            relevant_memory = (
                memory_context.get_context(
                    prompt
                )
            )

        except Exception as memory_error:

            print(
                "[AI] Memory lookup failed:",
                repr(memory_error)
            )

            return "No relevant permanent memory found."

        if relevant_memory:

            print(
                "[AI] Relevant memory loaded."
            )

            return str(
                relevant_memory
            )[:2000]

        print(
            "[AI] No relevant memory."
        )

        return (
            "No relevant permanent memory found."
        )

    # ============================================================
    # RECOMMENDATION CONTEXT
    # ============================================================

    def _get_recommendation_context(self, prompt: str) -> str:
        """
        Ask the Recommendation Engine for a grounded recommendation.

        The engine does not execute commands.
        It only provides reasoning that can guide Ollama.
        """

        try:

            recommendation = (
                recommendation_engine.recommend(
                    prompt
                )
            )

        except Exception as recommendation_error:

            print(
                "[AI] Recommendation lookup failed:",
                repr(recommendation_error)
            )

            return ""

        if recommendation:

            print(
                "[AI] Recommendation context loaded."
            )

            return str(
                recommendation
            )[:1800]

        return ""

    # ============================================================
    # CONVERSATION HISTORY
    # ============================================================

    def _get_history(self, prompt: str):

        history = (
            conversation.get_messages()
        )

        # Brain already stored the current user message.
        # Do not send it twice.
        if (
            history
            and history[-1].get("role") == "user"
            and history[-1].get("content") == prompt
        ):
            history = history[:-1]

        recent_history = (
            history[
                -self.MAX_HISTORY_MESSAGES:
            ]
        )

        limited_history = []
        total_chars = 0

        for message in reversed(
            recent_history
        ):

            content = str(
                message.get(
                    "content",
                    ""
                )
            )

            message_chars = len(
                content
            )

            if (
                total_chars
                + message_chars
                > self.MAX_HISTORY_CHARS
            ):
                break

            limited_history.insert(
                0,
                {
                    "role": message.get(
                        "role",
                        "user"
                    ),
                    "content": content
                }
            )

            total_chars += (
                message_chars
            )

        if limited_history:

            print(
                "[AI] Conversation history: "
                f"{len(limited_history)} messages "
                f"({total_chars} chars)"
            )

        else:

            print(
                "[AI] Conversation history: empty"
            )

        return limited_history

    # ============================================================
    # RESPONSE MODE
    # ============================================================

    def _get_response_mode(self, prompt: str, recommendation_context: str):
        lower_prompt = (
            str(prompt)
            .lower()
            .strip()
        )

        detailed_keywords = (
            "explain",
            "detailed",
            "details",
            "step by step",
            "steps",
            "how does",
            "how do",
            "how to",
            "why",
            "difference between",
            "compare",
            "comparison",
            "example",
            "examples",
            "teach me",
            "describe",
            "elaborate",
            "tell me more",
            "continue",
            "go on",
        )

        personalized_keywords = (
            "recommend",
            "recommendation",
            "what should i use",
            "which should i use",
            "what should i choose",
            "which should i choose",
            "which one should i use",
            "which one should i choose",
            "what do you recommend",
            "what would you recommend",
            "what would you suggest",
            "best option for me",
            "best choice for me",
        )

        needs_detail = any(
            keyword in lower_prompt
            for keyword in detailed_keywords
        )

        needs_personalized = (
            bool(recommendation_context)
            or any(
                keyword in lower_prompt
                for keyword in personalized_keywords
            )
        )

        if needs_detail:

            num_predict = (
                self.DETAILED_RESPONSE_TOKENS
            )

            print(
                "[AI] Response mode: "
                f"detailed ({num_predict} tokens)"
            )

            return (
                "detailed",
                num_predict
            )

        if needs_personalized:

            num_predict = (
                self.PERSONALIZED_RESPONSE_TOKENS
            )

            print(
                "[AI] Response mode: "
                f"personalized ({num_predict} tokens)"
            )

            return (
                "personalized",
                num_predict
            )

        num_predict = (
            self.SHORT_RESPONSE_TOKENS
        )

        print(
            "[AI] Response mode: "
            f"short ({num_predict} tokens)"
        )

        return (
            "short",
            num_predict
        )

    # ============================================================
    # LIGHTWEIGHT MEMORY PERSONALIZATION
    # ============================================================

    def _apply_memory_personalization(
        self,
        prompt: str,
        reply: str,
        relevant_memory: str
    ) -> str:
        """
        Small deterministic personalization layer.

        This exists as a safety net in case the model ignores
        relevant memory in a recommendation question.
        """

        if not relevant_memory:
            return reply

        lower_prompt = (
            str(prompt)
            .lower()
            .strip()
        )

        personalization_request = any(
            phrase in lower_prompt
            for phrase in (
                "recommend for me",
                "recommend to me",
                "for me personally",
                "what should i use",
                "which should i use",
                "what should i choose",
                "which should i choose",
                "what do you recommend",
                "which do you recommend",
                "what would you recommend",
            )
        )

        if not personalization_request:
            return reply

        # --------------------------------------------------------
        # Do not modify responses that already naturally use
        # the stored preference.
        # --------------------------------------------------------

        memory_lines = (
            str(
                relevant_memory
            ).splitlines()
        )

        favourite_facts = []

        for line in memory_lines:

            line_lower = line.lower()

            if (
                "favourite "
                in line_lower
                and " is "
                in line_lower
            ):
                favourite_facts.append(
                    line.strip()
                )

        if not favourite_facts:
            return reply

        # --------------------------------------------------------
        # Only add a lightweight prefix when the model gave a
        # generic recommendation.
        # --------------------------------------------------------

        if (
            reply.lower().startswith(
                "sorry"
            )
            or len(reply) < 5
        ):
            return reply

        return reply

    # ============================================================
    # ASK
    # ============================================================

    def ask(
        self,
        prompt: str
    ) -> str:

        try:

            print(
                "Calling Ollama..."
            )

            # ====================================================
            # MEMORY
            # ====================================================

            memory_text = (
                self._get_memory_text(
                    prompt
                )
            )

            # ====================================================
            # RECOMMENDATION ENGINE
            # ====================================================

            recommendation_context = (
                self._get_recommendation_context(
                    prompt
                )
            )

            # ====================================================
            # PERSONALIZATION GUIDANCE
            # ====================================================

            personalization_context = (
                self._get_personalization_context(
                    prompt
                )
            )

            if personalization_context:

                print(
                    "[AI] Personalization guidance loaded."
                )

            # ====================================================
            # SYSTEM PROMPT
            # ====================================================

            system_prompt = f"""
You are FRIDAY, a helpful desktop AI assistant.

Address the user as Sir.

Be natural, friendly, and concise.

When relevant user memory clearly applies to the current request,
personalize the answer naturally.

Do not force unrelated memories into the response.

When a grounded recommendation is provided below, it is FRIDAY's
decision for the current request.

Treat it as authoritative.

Do not contradict it.
Do not replace it with a generic "it depends" answer.
Do not ignore it.
You may explain the reasoning behind it naturally.

When comparing options, clearly state the recommended option first,
then explain when the alternative would make sense.

When the grounded recommendation uses the user's stored preferences,
respect those preferences exactly.

For normal questions, answer in 1-2 short sentences.

Only give detailed explanations when the user asks for
details, steps, examples, comparisons, or an explanation.

Do not use long lists unless the user asks for them.

Do not return JSON during normal conversation.

========================================
RELEVANT USER MEMORY
========================================

{memory_text}

========================================
PERSONALIZATION GUIDANCE
========================================

{personalization_context if personalization_context else "No special personalization guidance."}

========================================
GROUNDED RECOMMENDATION
========================================

{recommendation_context if recommendation_context else "No grounded recommendation is available for this request."}
"""

            # ====================================================
            # HISTORY
            # ====================================================

            limited_history = (
                self._get_history(
                    prompt
                )
            )

            # ====================================================
            # RESPONSE MODE
            # ====================================================

            (
                response_mode,
                num_predict
            ) = self._get_response_mode(
                prompt,
                recommendation_context
            )

            # ====================================================
            # BUILD MESSAGES
            # ====================================================

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            messages.extend(
                limited_history
            )

            messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            # ====================================================
            # ASK OLLAMA
            # ====================================================

            response = ollama.chat(

                model=self.MODEL,

                messages=messages,

                options={
                    "temperature": 0.3,
                    "num_predict": num_predict,
                },

                keep_alive=self.KEEP_ALIVE,
            )

            print(
                "Returned from Ollama"
            )

            # ====================================================
            # EXTRACT RESPONSE
            # ====================================================

            reply = (
                response
                .message
                .content
                .strip()
            )

            # ====================================================
            # MEMORY PERSONALIZATION SAFETY NET
            # ====================================================

            reply = (
                self._apply_memory_personalization(
                    prompt,
                    reply,
                    memory_text
                )
            )

            # ====================================================
            # FALLBACK
            # ====================================================

            if not reply:

                return (
                    "Sorry Sir, I couldn't generate a response."
                )

            return reply

        except Exception as e:

            print(
                "AI Error:",
                repr(e)
            )

            return (
                "Sorry Sir, I am having trouble "
                "processing that right now."
            )


# ================================================================
# GLOBAL INSTANCE
# ================================================================

ai = AI()