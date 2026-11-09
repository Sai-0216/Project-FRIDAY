"""
FRIDAY security approval manager.

Approvals are short-lived, single-use capabilities bound to an exact
canonical action sequence. Issuing an approval must only be exposed
through a separately verified trusted-user interaction.
"""

import hashlib
import json
import math
import secrets
import threading
import time


class ApprovalManager:
    DEFAULT_TTL_SECONDS = 60.0
    MAX_TTL_SECONDS = 300.0

    def __init__(self, *, _clock=None, _token_factory=None):
        self._clock = _clock or time.monotonic
        self._token_factory = _token_factory or secrets.token_urlsafe
        self._lock = threading.RLock()
        self._approvals = {}

    @staticmethod
    def _action_digest(actions):
        if not isinstance(actions, (list, tuple)) or not actions:
            raise ValueError("Actions must be a non-empty list or tuple")

        try:
            canonical = json.dumps(
                actions,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("Actions are not safely serializable") from exc

        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _token_key(token):
        if not isinstance(token, str) or not token:
            return None
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _purge_expired_locked(self, now):
        expired = [
            key
            for key, approval in self._approvals.items()
            if now >= approval["expires_at"]
        ]
        for key in expired:
            self._approvals.pop(key, None)

    def issue(self, actions, *, ttl_seconds=DEFAULT_TTL_SECONDS):
        """Issue a token. Call only after a trusted user explicitly approves."""
        try:
            ttl = float(ttl_seconds)
        except (TypeError, ValueError) as exc:
            raise ValueError("Approval lifetime must be numeric") from exc

        if (
            not math.isfinite(ttl)
            or ttl <= 0
            or ttl > self.MAX_TTL_SECONDS
        ):
            raise ValueError(
                f"Approval lifetime must be greater than 0 and at most "
                f"{self.MAX_TTL_SECONDS} seconds"
            )

        digest = self._action_digest(actions)
        now = self._clock()

        with self._lock:
            self._purge_expired_locked(now)

            for _ in range(5):
                token = self._token_factory(32)
                key = self._token_key(token)
                if key is not None and key not in self._approvals:
                    self._approvals[key] = {
                        "digest": digest,
                        "expires_at": now + ttl,
                    }
                    return token

        raise RuntimeError("Could not generate a unique approval token")

    def consume(self, token, actions):
        """
        Consume an approval exactly once.

        A valid token is invalidated even when presented with altered actions.
        """
        key = self._token_key(token)
        if key is None:
            return False

        try:
            digest = self._action_digest(actions)
        except ValueError:
            digest = None

        now = self._clock()

        with self._lock:
            self._purge_expired_locked(now)
            approval = self._approvals.pop(key, None)

        if approval is None or digest is None:
            return False

        return secrets.compare_digest(approval["digest"], digest)

    def deny(self, token):
        """Revoke an outstanding approval."""
        key = self._token_key(token)
        if key is None:
            return False

        with self._lock:
            return self._approvals.pop(key, None) is not None

    def pending_count(self):
        """Return the number of currently valid, unconsumed approvals."""
        now = self._clock()
        with self._lock:
            self._purge_expired_locked(now)
            return len(self._approvals)
