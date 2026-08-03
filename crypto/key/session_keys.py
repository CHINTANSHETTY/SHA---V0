"""Session Key Lifecycle and Metadata Management.

This module provides the `SessionKeyManager` for managing session lifecycles, TTL expirations,
max usage counters, key rotations, replay attack prevention, and metadata tracking.

Security & Architectural Principles:
    - Metadata-Only Storage: To minimize long-lived secret exposure in memory, `SessionKeyManager`
      stores session metadata (IDs, creation/expiration timestamps, usage counters, key version IDs)
      rather than storing long-lived raw secret keys.
    - Replay Prevention: Usage limits (`max_uses`) and TTL timestamps (`ttl_seconds`) prevent replay attacks.
"""

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, Set

from .evolution import InvalidContextError, KeyErrorBase, KeyEvolutionEngine


# =========================================================
# EXCEPTION CLASSES
# =========================================================
class SessionError(KeyErrorBase, ValueError):
    """Base exception for session management errors."""
    pass


class InvalidSessionError(SessionError, KeyError):
    """Raised when session ID is missing, empty, or not found."""
    pass


class SessionExpiredError(SessionError, RuntimeError):
    """Raised when attempting to access an expired session (TTL or max uses exceeded)."""
    pass


class ReplayAttackError(SessionError, SecurityError if "SecurityError" in globals() else RuntimeError):
    """Raised when session usage limit has been exceeded or replay detected."""
    pass


# =========================================================
# SESSION METADATA STRUCTURE
# =========================================================
@dataclass
class SessionMetadata:
    """Stores session metadata without exposing raw key secrets in memory.

    Attributes:
        session_id: Unique string identifier.
        key_version: Key version index or identifier string.
        creation_timestamp: Epoch timestamp (seconds) when created.
        expiration_timestamp: Optional epoch timestamp (seconds) when expired.
        max_uses: Maximum allowed usage operations.
        usage_count: Current count of session usages.
        is_active: Boolean status flag.
        context_hash: Optional hex string digest of derivation context.
    """

    session_id: str
    key_version: str = "v1"
    creation_timestamp: float = field(default_factory=time.time)
    expiration_timestamp: Optional[float] = None
    max_uses: Optional[int] = 1000
    usage_count: int = 0
    is_active: bool = True
    context_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return asdict(self)


# =========================================================
# SESSION KEY MANAGER
# =========================================================
class SessionKeyManager:
    """Session Key Lifecycle and Metadata Manager.

    Tracks session lifecycles, expirations, usage limits, key rotation, and replay prevention.
    """

    def __init__(self, key_engine: Optional[KeyEvolutionEngine] = None) -> None:
        """Initialize SessionKeyManager.

        Args:
            key_engine: KeyEvolutionEngine instance (creates default if None).
        """
        self._key_engine: KeyEvolutionEngine = key_engine if key_engine is not None else KeyEvolutionEngine()
        self._sessions: Dict[str, SessionMetadata] = {}

    def create_session(
        self,
        session_id: str,
        master_key: bytes,
        ttl_seconds: Optional[float] = 3600.0,
        max_uses: Optional[int] = 1000,
        context: Optional[bytes] = None,
        key_version: str = "v1",
    ) -> Dict[str, Any]:
        """Create and register a new session.

        Args:
            session_id: Unique session ID string.
            master_key: Valid master key bytes.
            ttl_seconds: Optional Time-To-Live in seconds (None for no time limit).
            max_uses: Optional maximum usage count (None for unlimited).
            context: Optional context bytes.
            key_version: Key version label string.

        Returns:
            Dict[str, Any]: Session metadata dictionary.

        Raises:
            InvalidSessionError: If session_id is empty or already registered.
            InvalidContextError: If master_key is invalid.
        """
        if not isinstance(session_id, str) or not session_id.strip():
            raise InvalidSessionError("session_id must be a non-empty string")

        sid = session_id.strip()
        if sid in self._sessions and self._sessions[sid].is_active:
            raise InvalidSessionError(f"Active session '{sid}' is already registered")

        # Validate master_key format using KeyEvolutionEngine
        _ = self._key_engine._validate_master_key(master_key)

        now = time.time()
        exp_time = (now + ttl_seconds) if ttl_seconds is not None and ttl_seconds > 0 else None

        meta = SessionMetadata(
            session_id=sid,
            key_version=key_version,
            creation_timestamp=now,
            expiration_timestamp=exp_time,
            max_uses=max_uses,
            usage_count=0,
            is_active=True,
            context_hash=context.hex() if context else None,
        )

        self._sessions[sid] = meta
        return meta.to_dict()

    def get_session(self, session_id: str) -> SessionMetadata:
        """Retrieve metadata object for a session ID.

        Args:
            session_id: Session ID string.

        Returns:
            SessionMetadata: Session metadata object.

        Raises:
            InvalidSessionError: If session ID is not found.
        """
        if not isinstance(session_id, str) or session_id.strip() not in self._sessions:
            raise InvalidSessionError(f"Session '{session_id}' not found")
        return self._sessions[session_id.strip()]

    def validate_session(self, session_id: str, increment_usage: bool = True) -> bool:
        """Validate if session is active, not expired, and within usage limits.

        Args:
            session_id: Session ID string.
            increment_usage: If True, increments the usage counter upon successful validation.

        Returns:
            bool: True if session is valid.

        Raises:
            InvalidSessionError: If session ID not found.
            SessionExpiredError: If session TTL has expired.
            ReplayAttackError: If session max uses limit has been reached.
        """
        meta = self.get_session(session_id)

        if not meta.is_active:
            raise SessionExpiredError(f"Session '{session_id}' is closed/inactive")

        now = time.time()
        if meta.expiration_timestamp is not None and now >= meta.expiration_timestamp:
            meta.is_active = False
            raise SessionExpiredError(f"Session '{session_id}' has expired (TTL exceeded)")

        if meta.max_uses is not None and meta.usage_count >= meta.max_uses:
            meta.is_active = False
            raise ReplayAttackError(f"Session '{session_id}' max uses limit ({meta.max_uses}) exceeded")

        if increment_usage:
            meta.usage_count += 1

        return True

    def renew_session(self, session_id: str, extension_ttl: Optional[float] = 3600.0) -> Dict[str, Any]:
        """Renew session expiration time and reset usage counter.

        Args:
            session_id: Session ID string.
            extension_ttl: TTL extension in seconds.

        Returns:
            Dict[str, Any]: Updated session metadata.
        """
        meta = self.get_session(session_id)
        now = time.time()

        meta.is_active = True
        meta.usage_count = 0
        if extension_ttl is not None and extension_ttl > 0:
            meta.expiration_timestamp = now + extension_ttl
        else:
            meta.expiration_timestamp = None

        return meta.to_dict()

    def rotate_keys(self, session_id: str, new_master_key: bytes, new_version: str = "v2") -> Dict[str, Any]:
        """Rotate key version for an existing session.

        Args:
            session_id: Session ID string.
            new_master_key: New master key bytes.
            new_version: New key version label string.

        Returns:
            Dict[str, Any]: Updated session metadata.
        """
        meta = self.get_session(session_id)
        _ = self._key_engine._validate_master_key(new_master_key)

        meta.key_version = new_version
        meta.usage_count = 0
        meta.is_active = True

        return meta.to_dict()

    def close_session(self, session_id: str) -> None:
        """Mark a session as closed and inactive.

        Args:
            session_id: Session ID string.
        """
        meta = self.get_session(session_id)
        meta.is_active = False

    def export_metadata(self, session_id: str) -> Dict[str, Any]:
        """Export session metadata dictionary.

        Args:
            session_id: Session ID string.

        Returns:
            Dict[str, Any]: Metadata dictionary.
        """
        meta = self.get_session(session_id)
        return meta.to_dict()
