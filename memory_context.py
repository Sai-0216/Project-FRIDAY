"""
Project FRIDAY
Memory Context

Provides relevant saved memories to the Brain/AI
without exposing the entire memory store unnecessarily.
"""

import re

import re

import re

import re

from modules.memory import memory
from proactive.preference_memory import preference_memory
from proactive.episodic_memory import episodic_memory


class MemoryContext:

    # ========================================
    # KEYWORD EXTRACTION
    # ========================================

    def _keywords(self, text):

        text = str(text).lower()

        stop_words = {
            "the", "a", "an", "is", "are", "am", "i", "my", "me",
            "you", "your", "what", "where", "when", "why", "how",
            "can", "could", "would", "please", "want", "need", "to",
            "for", "and", "or", "of", "on", "in", "with", "this",
            "that", "it", "do", "did", "does", "today", "now",
        }

        words = re.findall(r"[a-z0-9]+", text)
        result = set()

        for word in words:
            if len(word) <= 2 or word in stop_words:
                continue
            if word.endswith("ies") and len(word) > 4:
                word = word[:-3] + "y"
            elif word.endswith("es") and len(word) > 4:
                word = word[:-2]
            elif word.endswith("s") and len(word) > 3:
                word = word[:-1]
            result.add(word)

        return result

    # ========================================
    # FIND RELEVANT MEMORIES
    # ========================================

    def relevant(self, text, limit=5):

        data = memory.all()

        if not data:
            return {}

        query_words = self._keywords(text)

        if not query_words:
            return {}

        scored = []

        for key, value in data.items():
            key_text = str(key).lower()
            memory_text = f"{key} {value}".lower()
            key_words = self._keywords(key_text)
            memory_words = self._keywords(memory_text)
            overlap = query_words.intersection(memory_words)
            key_overlap = query_words.intersection(key_words)
            score = len(overlap) + (2 * len(key_overlap))
            if score > 0:
                scored.append((score, key, value))

        scored.sort(key=lambda item: (-item[0], str(item[1]).lower()))

        result = {}
        for score, key, value in scored[:limit]:
            result[key] = value

        return result

    # ========================================
    # FORMAT MEMORY FOR AI
    # ========================================

    def format_for_ai(
        self,
        memories
    ):

        if not memories:

            return ""

        lines = [
            "Relevant user information:",
            "Use this information when it is directly relevant to the user's request."
        ]

        for key, value in memories.items():

            lines.append(
                f"- The user's {key.removeprefix('my ')} is {value}."
            )

        return "\n".join(
            lines
        )

    # ========================================
    # BEHAVIORAL PROFILE
    # ========================================

    def behavioral_profile(self, limit=50):
        try:
            records = episodic_memory.recent(limit)
            commands = {}
            intents = {}
            outcomes = {"completed": 0, "partial": 0, "failed": 0}
            for record in records:
                if not isinstance(record, dict):
                    continue
                event = " ".join(str(record.get("event", "")).strip().lower().split())
                if event:
                    commands[event] = commands.get(event, 0) + 1
                context = record.get("context", {})
                if isinstance(context, dict):
                    intent = context.get("intent")
                    if intent:
                        intent = str(intent)
                        intents[intent] = intents.get(intent, 0) + 1
                outcome = record.get("outcome")
                if outcome in outcomes:
                    outcomes[outcome] += 1
            return {"total_experiences": len(records), "frequent_commands": dict(sorted(commands.items(), key=lambda item: (-item[1], item[0]))[:10]), "frequent_intents": dict(sorted(intents.items(), key=lambda item: (-item[1], item[0]))[:10]), "outcomes": outcomes}
        except Exception as e:
            print("[MEMORY CONTEXT] Behavioral profile error:", repr(e))
            return {"total_experiences": 0, "frequent_commands": {}, "frequent_intents": {}, "outcomes": {"completed": 0, "partial": 0, "failed": 0}}

    # ========================================
    # ROUTINE PROFILE
    # ========================================

    def routine_profile(self, limit=50):
        try:
            from datetime import datetime
            records = episodic_memory.recent(limit)
            routines = {}
            for record in records:
                if not isinstance(record, dict):
                    continue
                event = " ".join(str(record.get("event", "")).strip().lower().split())
                timestamp = record.get("timestamp")
                if not event or not timestamp:
                    continue
                try:
                    dt = datetime.fromisoformat(str(timestamp))
                except (TypeError, ValueError):
                    continue
                window = dt.hour * 2 + (1 if dt.minute >= 30 else 0)
                key = (event, window)
                routines[key] = routines.get(key, 0) + 1
            candidates = [{"command": event, "time_window": "{:02d}:{:02d}-{:02d}:{:02d}".format((window // 2), 30 if window % 2 else 0, ((window + 1) // 2) % 24, 0 if window % 2 else 30), "occurrences": count, "confidence": round(min(1.0, count / 5.0), 2), "strength": "strong" if count >= 5 else "moderate" if count >= 3 else "weak"} for (event, window), count in routines.items() if count >= 2]
            candidates.sort(key=lambda item: (-item["occurrences"], item["command"], item["time_window"]))
            return {"routine_candidates": candidates[:10]}
        except Exception as e:
            print("[MEMORY CONTEXT] Routine profile error:", repr(e))
            return {"routine_candidates": []}

    # ========================================
    # FIND RELEVANT PREFERENCES
    # ========================================

    def relevant_preferences(self, text, limit=5):
        try:
            keywords = self._keywords(text)
            matches = []
            seen = set()
            for keyword in keywords:
                for preference in preference_memory.search(keyword, limit=limit):
                    value = preference.get("preference")
                    if value and value not in seen:
                        seen.add(value)
                        matches.append(preference)
            return matches[:int(limit)]
        except Exception as e:
            print("[MEMORY CONTEXT] Preference retrieval error:", repr(e))
            return []
    # ========================================
    # PERSONAL PROFILE
    # ========================================

    def profile(self):
        try:
            memories = memory.all()
            preferences = preference_memory.recent(20)
            behavior = self.behavioral_profile()
            routines = self.routine_profile()
            freshness = self.profile_freshness()
            reliability = self.profile_reliability()
            consistency = self.profile_consistency()
            trust = self.profile_trust_score()
            weights = self.profile_signal_weights()
            evidence_priority = self.profile_evidence_priority()
            arbitration = self.profile_evidence_arbitration()
            decision_confidence = self.profile_decision_confidence()
            personalization_mode = self.personalization_mode()
            return {"memories": memories if isinstance(memories, dict) else {}, "preferences": preferences if isinstance(preferences, list) else [], "behavior": behavior if isinstance(behavior, dict) else {}, "routines": routines if isinstance(routines, dict) else {}, "freshness": freshness, "reliability": reliability, "consistency": consistency, "trust": trust, "weights": weights, "evidence_priority": evidence_priority, "arbitration": arbitration, "decision_confidence": decision_confidence, "personalization_mode": personalization_mode}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile error:", repr(e))
            return {"memories": {}, "preferences": []}

    # ========================================
    # UNIFIED PERSONALIZATION PROFILE
    # ========================================

    def unified_personalization_profile(self, text):
        try:
            profile = self.profile()
            adaptive = self.adaptive_context_package(text)
            guard = self.adaptive_context_guard(text)
            health = self.profile_intelligence_health()
            return {"query": str(text), "mode": profile.get("personalization_mode", {}).get("mode", "cautious"), "trust": profile.get("trust", {}).get("score", 0.5), "health": health.get("status", "degraded"), "adaptive": adaptive, "guard": guard}
        except Exception as e:
            print("[MEMORY CONTEXT] Unified personalization profile error:", repr(e))
            return {"query": str(text), "mode": "cautious", "trust": 0.5, "health": "degraded", "adaptive": {}, "guard": {"allowed": False}}

    # ========================================
    # PHASE 22 PROFILE SUMMARY
    # ========================================

    def phase22_profile_summary(self):
        try:
            completeness = self.profile_completeness()
            health = self.profile_intelligence_health()
            readiness = self.profile_wide_readiness()
            trust = self.profile_trust_score()
            consistency = self.profile_consistency()
            reliability = self.profile_reliability()
            mode = self.personalization_mode()
            return {"phase": 22, "status": "ready" if readiness.get("ready") else "needs_attention", "completeness": completeness.get("score", 0.0), "health": health.get("status", "degraded"), "trust": trust.get("score", 0.5), "consistency": consistency.get("score", 0.5), "reliability": reliability.get("score", 0.5), "personalization_mode": mode.get("mode", "cautious"), "readiness": readiness.get("level", "not_ready") }
        except Exception as e:
            print("[MEMORY CONTEXT] Phase 22 profile summary error:", repr(e))
            return {"phase": 22, "status": "needs_attention", "completeness": 0.0, "health": "degraded", "trust": 0.5, "consistency": 0.5, "reliability": 0.5, "personalization_mode": "cautious", "readiness": "not_ready"}

    # ========================================
    # PROFILE COMPLETENESS
    # ========================================

    def profile_completeness(self):
        try:
            memories = memory.all()
            preferences = preference_memory.recent(20)
            experiences = episodic_memory.recent(20)
            checks = {
                "memories": bool(memories),
                "preferences": bool(preferences),
                "behavior": bool(experiences),
            }
            score = round(sum(1.0 for value in checks.values() if value) / len(checks), 2)
            level = "high" if score >= 0.85 else "medium" if score >= 0.5 else "low"
            missing = [source for source, present in checks.items() if not present]
            return {"score": score, "level": level, "sources": checks, "missing": missing}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile completeness error:", repr(e))
            return {"score": 0.0, "level": "low", "sources": {"memories": False, "preferences": False, "behavior": False}, "missing": ["memories", "preferences", "behavior"]}

    # ========================================
    # PROFILE PERSONALIZATION STATUS
    # ========================================

    def profile_personalization_status(self, text):
        try:
            readiness = self.personalization_readiness(text)
            guard = self.adaptive_context_guard(text)
            health = self.profile_intelligence_health()
            mode = self.personalization_mode()
            return {"ready": readiness.get("ready", False), "status": readiness.get("level", "not_ready"), "source": readiness.get("source"), "confidence": readiness.get("confidence", 0.0), "mode": mode.get("mode", "cautious"), "health": health.get("status", "degraded"), "trust": health.get("trust", 0.5), "guarded": guard.get("allowed", False)}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile personalization status error:", repr(e))
            return {"ready": False, "status": "not_ready", "source": None, "confidence": 0.0, "mode": "cautious", "health": "degraded", "trust": 0.5, "guarded": False}

    # ========================================
    # READINESS-AWARE CONTEXT
    # ========================================

    def readiness_aware_context(self, text):
        try:
            readiness = self.personalization_readiness(text)
            package = self.adaptive_context_package(text)
            if readiness.get("ready"):
                return {"ready": True, "level": readiness.get("level", "ready"), "source": readiness.get("source"), "confidence": readiness.get("confidence", 0.0), "decision": readiness.get("mode", "selective"), "adaptive": package}
            return {"ready": False, "level": readiness.get("level", "not_ready"), "source": None, "confidence": 0.0, "decision": "do_not_personalize", "adaptive": {}}
        except Exception as e:
            print("[MEMORY CONTEXT] Readiness-aware context error:", repr(e))
            return {"ready": False, "level": "not_ready", "source": None, "confidence": 0.0, "decision": "do_not_personalize", "adaptive": {}}

    # ========================================
    # PROFILE-WIDE READINESS
    # ========================================

    def profile_wide_readiness(self):
        try:
            health = self.profile_intelligence_health()
            trust = self.profile_trust_score()
            consistency = self.profile_consistency()
            mode = self.personalization_mode()
            score = round((health.get("overall_score", 0.5) * 0.35) + (trust.get("score", 0.5) * 0.30) + (consistency.get("score", 0.5) * 0.20) + (mode.get("score", 0.5) * 0.15), 2)
            ready = health.get("status") == "healthy" and trust.get("level") == "high" and consistency.get("level") == "high" and mode.get("mode") == "strong"
            level = "ready" if ready and score >= 0.85 else "conditional" if score >= 0.6 else "not_ready"
            return {"ready": ready, "level": level, "score": score, "health": health.get("status", "degraded"), "trust": trust.get("score", 0.5), "consistency": consistency.get("score", 0.5), "mode": mode.get("mode", "cautious")}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile-wide readiness error:", repr(e))
            return {"ready": False, "level": "not_ready", "score": 0.5, "health": "degraded", "trust": 0.5, "consistency": 0.5, "mode": "cautious"}

    # ========================================
    # PERSONALIZATION READINESS
    # ========================================

    def personalization_readiness(self, text):
        try:
            audit = self.adaptive_context_audit(text)
            health = self.profile_intelligence_health()
            mode = self.personalization_mode()
            ready = bool(audit.get("audit_ok")) and health.get("status") == "healthy" and mode.get("mode") in ("strong", "selective")
            level = "ready" if ready and mode.get("mode") == "strong" else "conditional" if ready else "not_ready"
            return {"ready": ready, "level": level, "source": audit.get("source"), "confidence": audit.get("confidence", 0.0), "mode": mode.get("mode", "cautious"), "health": health.get("status", "degraded")}
        except Exception as e:
            print("[MEMORY CONTEXT] Personalization readiness error:", repr(e))
            return {"ready": False, "level": "not_ready", "source": None, "confidence": 0.0, "mode": "cautious", "health": "degraded"}

    # ========================================
    # PROFILE INTELLIGENCE HEALTH
    # ========================================

    def profile_intelligence_health(self):
        try:
            trust = self.profile_trust_score()
            consistency = self.profile_consistency()
            reliability = self.profile_reliability()
            freshness = self.profile_freshness()
            mode = self.personalization_mode()
            decision = self.profile_decision_confidence()
            scores = [trust.get("score", 0.5), consistency.get("score", 0.5), reliability.get("score", 0.5), mode.get("score", 0.5), decision.get("score", 0.5)]
            overall = round(sum(scores) / len(scores), 2)
            status = "healthy" if overall >= 0.85 else "stable" if overall >= 0.6 else "degraded"
            return {"status": status, "overall_score": overall, "trust": trust.get("score", 0.5), "consistency": consistency.get("score", 0.5), "reliability": reliability.get("score", 0.5), "decision_confidence": decision.get("score", 0.5), "personalization_mode": mode.get("mode", "cautious"), "freshness": freshness}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile intelligence health error:", repr(e))
            return {"status": "degraded", "overall_score": 0.5, "trust": 0.5, "consistency": 0.5, "reliability": 0.5, "decision_confidence": 0.5, "personalization_mode": "cautious", "freshness": {}}

    # ========================================
    # ADAPTIVE CONTEXT GUARD
    # ========================================

    def adaptive_context_guard(self, text):
        try:
            audit = self.adaptive_context_audit(text)
            if audit.get("audit_ok"):
                return {"allowed": True, "source": audit.get("source"), "confidence": audit.get("confidence", 0.0), "decision": audit.get("decision", "none"), "mode": audit.get("mode", "cautious"), "reason": "Adaptive profile evidence passed validation."}
            return {"allowed": False, "source": None, "confidence": 0.0, "decision": "none", "mode": "cautious", "reason": "Adaptive profile evidence failed validation and must not be relied upon."}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive context guard error:", repr(e))
            return {"allowed": False, "source": None, "confidence": 0.0, "decision": "none", "mode": "cautious", "reason": "Adaptive profile evidence is unavailable."}

    # ========================================
    # ADAPTIVE CONTEXT AUDIT
    # ========================================

    def adaptive_context_audit(self, text):
        try:
            snapshot = self.adaptive_profile_snapshot(text)
            validation = self.validate_adaptive_snapshot(text)
            package = snapshot.get("evidence", {})
            decision = package.get("decision", {})
            source = decision.get("source")
            confidence = decision.get("confidence", 0.0)
            audit_ok = validation.get("valid", False) and validation.get("source") == source and validation.get("confidence") == confidence
            return {"audit_ok": audit_ok, "source": source, "confidence": confidence, "decision": decision.get("decision", "none"), "mode": snapshot.get("profile_mode", "cautious"), "profile_trust": snapshot.get("profile_trust", 0.5)}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive context audit error:", repr(e))
            return {"audit_ok": False, "source": None, "confidence": 0.0, "decision": "none", "mode": "cautious", "profile_trust": 0.5}

    # ========================================
    # ADAPTIVE SNAPSHOT VALIDATION
    # ========================================

    def validate_adaptive_snapshot(self, text):
        try:
            snapshot = self.adaptive_profile_snapshot(text)
            evidence = snapshot.get("evidence", {})
            decision = evidence.get("decision", {})
            confidence = evidence.get("confidence", {})
            source = decision.get("source")
            score = decision.get("confidence", 0.0)
            valid = bool(source) and source in confidence.get("confidence", {}) and score >= 0.6 and decision.get("decision") in ("use_strongly", "use_selectively", "use_cautiously")
            return {"valid": valid, "source": source, "confidence": score, "decision": decision.get("decision"), "mode": snapshot.get("profile_mode", "cautious")}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive snapshot validation error:", repr(e))
            return {"valid": False, "source": None, "confidence": 0.0, "decision": "none", "mode": "cautious"}

    # ========================================
    # ADAPTIVE PROFILE SNAPSHOT
    # ========================================

    def adaptive_profile_snapshot(self, text):
        try:
            from datetime import datetime
            package = self.adaptive_context_package(text)
            profile = self.profile()
            return {"timestamp": datetime.now().isoformat(), "query": str(text), "profile_mode": profile.get("personalization_mode", {}).get("mode", "selective"), "profile_trust": profile.get("trust", {}).get("score", 0.5), "evidence": package}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive profile snapshot error:", repr(e))
            return {"timestamp": None, "query": str(text), "profile_mode": "cautious", "profile_trust": 0.5, "evidence": {}}

    # ========================================
    # ADAPTIVE CONTEXT PACKAGE
    # ========================================

    def adaptive_context_package(self, text):
        try:
            relevance = self.adaptive_context_relevance(text)
            decision = self.adaptive_evidence_decision(text)
            confidence = self.adaptive_context_confidence(text)
            summary = self.adaptive_evidence_summary(text)
            return {"relevance": relevance, "decision": decision, "confidence": confidence, "summary": summary}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive context package error:", repr(e))
            return {"relevance": {"relevant": [], "level": "low", "count": 0}, "decision": {"decision": "none", "source": None, "confidence": 0.0, "mode": "cautious"}, "confidence": {"confidence": {}, "strongest_source": None, "score": 0.0, "level": "low"}, "summary": {"summary": "Adaptive profile evidence is unavailable.", "source": None, "confidence": 0.0, "mode": "cautious", "decision": "none"}}

    # ========================================
    # ADAPTIVE CONTEXT RELEVANCE
    # ========================================

    def adaptive_context_relevance(self, text):
        try:
            adaptive = self.adaptive_profile_context(text)
            confidence = self.adaptive_context_confidence(text)
            selected = adaptive.get("selected", {})
            scores = confidence.get("confidence", {})
            relevant_sources = []
            for source in selected:
                score = scores.get(source, 0.0)
                if score >= 0.6:
                    relevant_sources.append({"source": source, "confidence": score})
            relevant_sources.sort(key=lambda item: (-item["confidence"], item["source"]))
            level = "high" if relevant_sources and relevant_sources[0]["confidence"] >= 0.85 else "medium" if relevant_sources else "low"
            return {"relevant": relevant_sources, "level": level, "count": len(relevant_sources)}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive context relevance error:", repr(e))
            return {"relevant": [], "level": "low", "count": 0}

    # ========================================
    # ADAPTIVE EVIDENCE SUMMARY
    # ========================================

    def adaptive_evidence_summary(self, text):
        try:
            decision = self.adaptive_evidence_decision(text)
            confidence = self.adaptive_context_confidence(text)
            source = decision.get("source")
            score = decision.get("confidence", 0.0)
            mode = decision.get("mode", "cautious")
            action = decision.get("decision", "none")
            if not source:
                return {"summary": "No adaptive profile evidence was selected for this request.", "source": None, "confidence": 0.0, "mode": mode, "decision": action}
            source_confidence = confidence.get("confidence", {}).get(source, score)
            summary = f"Selected {source} as the primary profile evidence with confidence {source_confidence}; personalization mode is {mode}, so FRIDAY should {action.replace(chr(95), chr(32))}."
            return {"summary": summary, "source": source, "confidence": source_confidence, "mode": mode, "decision": action}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive evidence summary error:", repr(e))
            return {"summary": "Adaptive profile evidence is unavailable.", "source": None, "confidence": 0.0, "mode": "cautious", "decision": "none"}

    # ========================================
    # ADAPTIVE EVIDENCE DECISION
    # ========================================

    def adaptive_evidence_decision(self, text):
        try:
            adaptive = self.adaptive_profile_context(text)
            confidence = self.adaptive_context_confidence(text)
            profile = self.profile()
            mode = profile.get("personalization_mode", {}).get("mode", "selective")
            strongest = confidence.get("strongest_source")
            score = confidence.get("score", 0.0)
            selected = adaptive.get("selected", {})
            if not strongest or strongest not in selected:
                return {"decision": "none", "source": None, "confidence": 0.0, "mode": mode}
            if mode == "strong" and score >= 0.85:
                decision = "use_strongly"
            elif mode == "selective" and score >= 0.6:
                decision = "use_selectively"
            else:
                decision = "use_cautiously"
            return {"decision": decision, "source": strongest, "confidence": score, "mode": mode}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive evidence decision error:", repr(e))
            return {"decision": "none", "source": None, "confidence": 0.0, "mode": "cautious"}

    # ========================================
    # ADAPTIVE CONTEXT CONFIDENCE
    # ========================================

    def adaptive_context_confidence(self, text):
        try:
            adaptive = self.adaptive_profile_context(text)
            profile = self.profile()
            weights = adaptive.get("weights", {})
            decision = profile.get("decision_confidence", {})
            decision_score = decision.get("score", 0.5)
            selected = adaptive.get("selected", {})
            confidence = {}
            for source in selected:
                weight = weights.get(source, 0.5)
                confidence[source] = round((weight * 0.6) + (decision_score * 0.4), 2)
            strongest = max(confidence.items(), key=lambda item: item[1]) if confidence else (None, 0.0)
            level = "high" if strongest[1] >= 0.85 else "medium" if strongest[1] >= 0.6 else "low"
            return {"confidence": confidence, "strongest_source": strongest[0], "score": strongest[1], "level": level}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive context confidence error:", repr(e))
            return {"confidence": {}, "strongest_source": None, "score": 0.0, "level": "low"}

    # ========================================
    # ADAPTIVE PROFILE CONTEXT
    # ========================================

    def adaptive_profile_context(self, text):
        try:
            lower_text = str(text).lower().strip()
            profile = self.profile()
            weights = profile.get("weights", {})
            selected = {}
            if any(term in lower_text for term in ("prefer", "preference", "like", "favorite", "favourite", "choose", "recommend", "use")):
                selected["preferences"] = profile.get("preferences", [])
            if any(term in lower_text for term in ("usually", "often", "normally", "routine", "habit", "every day", "always")):
                selected["behavior"] = profile.get("behavior", {})
            if any(term in lower_text for term in ("my project", "project", "coding", "programming", "learning", "studying", "language", "editor")):
                selected["memories"] = profile.get("memories", {})
            if not selected:
                ranked = sorted(weights.items(), key=lambda item: (-item[1], item[0]))
                for source, _weight in ranked[:2]:
                    selected[source] = profile.get(source, {})
            return {"selected": selected, "weights": {source: weights.get(source, 0.5) for source in selected}}
        except Exception as e:
            print("[MEMORY CONTEXT] Adaptive profile context error:", repr(e))
            return {"selected": {}, "weights": {}}

    # ========================================
    # PERSONALIZATION MODE
    # ========================================

    def personalization_mode(self):
        try:
            decision = self.profile_decision_confidence()
            trust = self.profile_trust_score()
            decision_score = decision.get("score", 0.5)
            trust_score = trust.get("score", 0.5)
            combined = round((decision_score * 0.55) + (trust_score * 0.45), 2)
            if combined >= 0.85:
                mode = "strong"
            elif combined >= 0.6:
                mode = "selective"
            else:
                mode = "cautious"
            return {"mode": mode, "score": combined, "decision_confidence": decision_score, "trust": trust_score}
        except Exception as e:
            print("[MEMORY CONTEXT] Personalization mode error:", repr(e))
            return {"mode": "cautious", "score": 0.5, "decision_confidence": 0.5, "trust": 0.5}

    # ========================================
    # PROFILE DECISION CONFIDENCE
    # ========================================

    def profile_decision_confidence(self):
        try:
            arbitration = self.profile_evidence_arbitration()
            trust = self.profile_trust_score()
            consistency = self.profile_consistency()
            base = arbitration.get("confidence", 0.5)
            trust_score = trust.get("score", 0.5)
            consistency_score = consistency.get("score", 0.5)
            score = round((base * 0.5) + (trust_score * 0.3) + (consistency_score * 0.2), 2)
            level = "high" if score >= 0.85 else "medium" if score >= 0.6 else "low"
            return {"score": score, "level": level, "winner": arbitration.get("winner"), "arbitration_confidence": base}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile decision confidence error:", repr(e))
            return {"score": 0.5, "level": "medium", "winner": None, "arbitration_confidence": 0.5}

    # ========================================
    # PROFILE EVIDENCE ARBITRATION
    # ========================================

    def profile_evidence_arbitration(self):
        try:
            priority = self.profile_evidence_priority()
            trust = self.profile_trust_score()
            consistency = self.profile_consistency()
            items = priority.get("priority", [])
            top_source = priority.get("top_source")
            conflicts = consistency.get("conflicts", 0)
            trust_level = str(trust.get("level", "medium")).lower()
            if not items:
                return {"winner": None, "reason": "No profile evidence is available.", "confidence": 0.0}
            winner_weight = items[0].get("weight", 0.5)
            if trust_level == "low":
                confidence = round(min(winner_weight, 0.5), 2)
                reason = "Overall profile trust is low, so the highest-weight source is only cautiously preferred."
            elif conflicts > 0:
                confidence = round(winner_weight * 0.8, 2)
                reason = "Profile signals contain conflicts, so the highest-weight source wins with reduced confidence."
            else:
                confidence = round(winner_weight, 2)
                reason = "The highest-weight profile source is selected because the available signals are consistent."
            return {"winner": top_source, "reason": reason, "confidence": confidence}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile evidence arbitration error:", repr(e))
            return {"winner": None, "reason": "Unable to arbitrate profile evidence.", "confidence": 0.0}

    # ========================================
    # PROFILE EVIDENCE PRIORITY
    # ========================================

    def profile_evidence_priority(self):
        try:
            weights = self.profile_signal_weights()
            ranked = sorted(weights.items(), key=lambda item: (-item[1], item[0]))
            priorities = []
            for rank, (source, weight) in enumerate(ranked, 1):
                priorities.append({"source": source, "weight": weight, "rank": rank})
            return {"priority": priorities, "top_source": priorities[0]["source"] if priorities else None}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile evidence priority error:", repr(e))
            return {"priority": [], "top_source": None}

    # ========================================
    # PROFILE SIGNAL WEIGHTS
    # ========================================

    def profile_signal_weights(self):
        try:
            freshness = self.profile_freshness()
            trust = self.profile_trust_score()
            status_values = {"fresh": 1.0, "aging": 0.75, "stale": 0.4, "unknown": 0.5}
            preference_freshness = status_values.get(freshness.get("preferences", {}).get("status", "unknown"), 0.5)
            behavior_freshness = status_values.get(freshness.get("behavior", {}).get("status", "unknown"), 0.5)
            trust_score = trust.get("score", 0.5)
            preference_weight = round(min(1.0, (trust_score * 0.6) + (preference_freshness * 0.4)), 2)
            behavior_weight = round(min(1.0, (trust_score * 0.6) + (behavior_freshness * 0.4)), 2)
            memory_weight = round(min(1.0, (trust_score * 0.8) + 0.2), 2)
            return {"preferences": preference_weight, "behavior": behavior_weight, "memories": memory_weight}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile signal weight error:", repr(e))
            return {"preferences": 0.5, "behavior": 0.5, "memories": 0.5}

    # ========================================
    # UNIFIED PROFILE TRUST
    # ========================================

    def profile_trust_score(self):
        try:
            reliability = self.profile_reliability()
            consistency = self.profile_consistency()
            freshness = self.profile_freshness()
            freshness_values = {'fresh': 1.0, 'aging': 0.75, 'stale': 0.4, 'unknown': 0.5}
            preference_freshness = freshness_values.get(freshness.get('preferences', {}).get('status', 'unknown'), 0.5)
            behavior_freshness = freshness_values.get(freshness.get('behavior', {}).get('status', 'unknown'), 0.5)
            freshness_score = (preference_freshness + behavior_freshness) / 2.0
            score = round((reliability.get('score', 0.5) * 0.4) + (consistency.get('score', 0.5) * 0.4) + (freshness_score * 0.2), 2)
            level = 'high' if score >= 0.85 else 'medium' if score >= 0.6 else 'low'
            return {'score': score, 'level': level, 'reliability': round(reliability.get('score', 0.5), 2), 'consistency': round(consistency.get('score', 0.5), 2), 'freshness': round(freshness_score, 2)}
        except Exception as e:
            print("[MEMORY CONTEXT] Unified profile trust error:", repr(e))
            return {'score': 0.5, 'level': 'medium', 'reliability': 0.5, 'consistency': 0.5, 'freshness': 0.5}

    # ========================================
    # PROFILE CONSISTENCY
    # ========================================

    def profile_consistency(self):
        try:
            preferences = preference_memory.recent(50)
            experiences = episodic_memory.recent(50)
            conflicts = 0
            preference_groups = {}
            for item in preferences:
                category = str(item.get("category", "general")).strip().lower()
                preference_groups.setdefault(category, []).append(item)
            for items in preference_groups.values():
                normalized = {str(item.get("preference", "")).strip().lower() for item in items if item.get("preference") }
                if len(normalized) > 1:
                    conflicts += len(normalized) - 1
            preference_consistency = 1.0 if not preferences else max(0.0, 1.0 - (conflicts / max(1, len(preferences))))
            command_groups = {}
            for item in experiences:
                command = str(item.get("event", "")).strip().lower()
                if command:
                    command_groups.setdefault(command, []).append(str(item.get("outcome", "unknown")).lower())
            command_scores = []
            for outcomes in command_groups.values():
                counts = {}
                for outcome in outcomes:
                    counts[outcome] = counts.get(outcome, 0) + 1
                command_scores.append(max(counts.values()) / len(outcomes))
            behavior_consistency = sum(command_scores) / len(command_scores) if command_scores else 0.5
            score = round((preference_consistency * 0.5) + (behavior_consistency * 0.5), 2)
            level = "high" if score >= 0.85 else "medium" if score >= 0.6 else "low"
            return {"score": score, "level": level, "preference_consistency": round(preference_consistency, 2), "behavior_consistency": round(behavior_consistency, 2), "conflicts": conflicts}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile consistency error:", repr(e))
            return {"score": 0.5, "level": "medium", "preference_consistency": 0.5, "behavior_consistency": 0.5, "conflicts": 0}

    # ========================================
    # PROFILE RELIABILITY
    # ========================================

    def profile_reliability(self):
        try:
            preferences = preference_memory.recent(20)
            experiences = episodic_memory.recent(20)
            freshness = self.profile_freshness()
            confidence_values = {"LOW": 0.33, "MEDIUM": 0.66, "HIGH": 1.0}
            if preferences:
                confidence_score = sum(confidence_values.get(str(item.get("confidence", "MEDIUM")).upper(), 0.66) for item in preferences) / len(preferences)
            else:
                confidence_score = 0.5
            if experiences:
                outcomes = [str(item.get("outcome", "")).lower() for item in experiences]
                outcome_score = sum(1.0 if outcome == "completed" else 0.5 if outcome == "partial" else 0.0 if outcome == "failed" else 0.5 for outcome in outcomes) / len(outcomes)
            else:
                outcome_score = 0.5
            freshness_values = {"fresh": 1.0, "aging": 0.75, "stale": 0.4, "unknown": 0.5}
            preference_freshness = freshness_values.get(freshness.get("preferences", {}).get("status", "unknown"), 0.5)
            behavior_freshness = freshness_values.get(freshness.get("behavior", {}).get("status", "unknown"), 0.5)
            freshness_score = (preference_freshness + behavior_freshness) / 2.0
            reliability = round((confidence_score * 0.35) + (outcome_score * 0.35) + (freshness_score * 0.30), 2)
            level = "high" if reliability >= 0.8 else "medium" if reliability >= 0.55 else "low"
            return {"score": reliability, "level": level, "confidence": round(confidence_score, 2), "outcome_consistency": round(outcome_score, 2), "freshness": round(freshness_score, 2)}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile reliability error:", repr(e))
            return {"score": 0.5, "level": "medium", "confidence": 0.5, "outcome_consistency": 0.5, "freshness": 0.5}

    # ========================================
    # PROFILE FRESHNESS
    # ========================================

    def profile_freshness(self):
        try:
            from datetime import datetime
            now = datetime.now()
            preferences = preference_memory.recent(20)
            experiences = episodic_memory.recent(20)
            def freshness(records):
                timestamps = []
                for record in records:
                    timestamp = record.get("timestamp") if isinstance(record, dict) else None
                    try:
                        timestamps.append(datetime.fromisoformat(str(timestamp)))
                    except (TypeError, ValueError):
                        continue
                if not timestamps:
                    return {"latest": None, "age_hours": None, "status": "unknown"}
                latest = max(timestamps)
                age_hours = round(max(0.0, (now - latest).total_seconds()) / 3600.0, 2)
                status = "fresh" if age_hours <= 24 else "aging" if age_hours <= 168 else "stale"
                return {"latest": latest.isoformat(), "age_hours": age_hours, "status": status}
            return {"preferences": freshness(preferences), "behavior": freshness(experiences)}
        except Exception as e:
            print("[MEMORY CONTEXT] Profile freshness error:", repr(e))
            return {"preferences": {"latest": None, "age_hours": None, "status": "unknown"}, "behavior": {"latest": None, "age_hours": None, "status": "unknown"}}

    # ========================================
    # GET AI CONTEXT
    # ========================================

    def get_context(
        self,
        text
    ):

        memories = self.relevant(
            text
        )

        context = self.format_for_ai(
            memories
        )

        preferences = self.relevant_preferences(
            text
        )

        if preferences:
            lines = [context] if context else []
            lines.append("Relevant user preferences:")
            lines.append("Use these preferences only when directly relevant.")
            for preference in preferences:
                lines.append(f"- The user prefers: {preference.get("preference")} (confidence: {preference.get("confidence", "MEDIUM")})")
            context = "\\n".join(lines)

        adaptive_relevance = self.adaptive_context_relevance(text)
        adaptive_guard = self.adaptive_context_guard(text)
        adaptive_summary = self.adaptive_evidence_summary(text) if adaptive_guard.get("allowed") else {"summary": ""}
        summary_text = adaptive_summary.get("summary", "")
        relevant_sources = [item.get("source") for item in adaptive_relevance.get("relevant", []) if item.get("source")]
        if relevant_sources:
            selected_sources = set(relevant_sources)
            if selected_sources and context:
                filtered_lines = []
                for line in context.split("\\n"):
                    lower_line = line.lower()
                    if "preference" in selected_sources and ("prefer" in lower_line or "preference" in lower_line):
                        filtered_lines.append(line)
                    elif "memories" in selected_sources and ("user" in lower_line or "language" in lower_line or "project" in lower_line or "editor" in lower_line):
                        filtered_lines.append(line)
                    elif "behavior" in selected_sources and ("routine" in lower_line or "usual" in lower_line or "behavior" in lower_line):
                        filtered_lines.append(line)
                    elif not any(token in lower_line for token in ("preference", "prefer", "language", "project", "editor", "routine", "usual", "behavior")):
                        filtered_lines.append(line)
                context = "\\n".join(filtered_lines)
        if summary_text:
            if context:
                context += "\\n" + "Adaptive profile guidance:" + "\\n" + "- " + summary_text
            else:
                context = "Adaptive profile guidance:" + "\\n" + "- " + summary_text

        return context


memory_context = MemoryContext()