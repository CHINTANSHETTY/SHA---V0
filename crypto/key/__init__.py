"""Key Evolution and Lifecycle Management Subsystem (`crypto.key`).

This package implements the Advanced Key Evolution Engine for the KDR-CA-AEAD cryptographic system,
supporting multi-round key ratcheting, forward-secure key chains, session-dependent key management,
adaptive key schedules, and RFC 5869-compliant HKDF key derivation with strict domain separation.

Subsystems:
    1. Key Evolution Engine (`crypto.key.evolution`):
       Master key ratcheting (`evolve`), context-aware subkey derivation (`derive_round_key`,
       `derive_session_key`, `derive_epoch_key`, `derive_context_key`, `derive_ca_key`, `derive_auth_key`,
       `derive_encryption_key`), and domain label constants.

    2. Adaptive Key Scheduling & Forward-Secure Chains (`crypto.key.adaptive_schedule`):
       Dynamic key scheduling (`AdaptiveKeyScheduler`) across 6 operational modes and one-way
       forward-secure key ratcheting (`ForwardKeyChain`).

    3. Session Key Lifecycle & Metadata Management (`crypto.key.session_keys`):
       Session creation, TTL expirations, usage counters, key rotation, and replay prevention (`SessionKeyManager`).
"""

__version__: str = "2.2.0"
__author__: str = "KDR-CA-AEAD Project"

# =========================================================
# RE-EXPORTS: EVOLUTION ENGINE & DOMAIN CONSTANTS
# =========================================================
from .evolution import (
    AUTH_KEY_LABEL,
    CA_KEY_LABEL,
    CONTEXT_KEY_LABEL,
    ENC_KEY_LABEL,
    NONCE_KEY_LABEL,
    EPOCH_KEY_LABEL,
    FORWARD_RATCHET_LABEL,
    MASTER_EVOLVE_LABEL,
    MAX_KEY_LENGTH,
    MIN_KEY_LENGTH,
    ROUND_KEY_LABEL,
    SESSION_KEY_LABEL,
    VERSION_LABEL,
    InvalidContextError,
    InvalidKeyLengthError,
    KeyErrorBase,
    KeyEvolutionEngine,
    KeyEvolutionError,
)

# =========================================================
# RE-EXPORTS: ADAPTIVE SCHEDULING & FORWARD KEY CHAIN
# =========================================================
from .adaptive_schedule import (
    AdaptiveKeyScheduler,
    ChainDepletedError,
    ForwardKeyChain,
    SchedulerError,
)

# =========================================================
# RE-EXPORTS: SESSION KEY LIFECYCLE & METADATA
# =========================================================
from .session_keys import (
    InvalidSessionError,
    ReplayAttackError,
    SessionExpiredError,
    SessionKeyManager,
    SessionMetadata,
)

# =========================================================
# EXPLICIT PUBLIC API
# =========================================================
__all__ = [
    # Metadata
    "__version__",
    "__author__",
    # Domain Separation Label Constants
    "VERSION_LABEL",
    "MASTER_EVOLVE_LABEL",
    "ROUND_KEY_LABEL",
    "SESSION_KEY_LABEL",
    "EPOCH_KEY_LABEL",
    "CONTEXT_KEY_LABEL",
    "CA_KEY_LABEL",
    "AUTH_KEY_LABEL",
    "ENC_KEY_LABEL",
    "NONCE_KEY_LABEL",
    "FORWARD_RATCHET_LABEL",
    "MIN_KEY_LENGTH",
    "MAX_KEY_LENGTH",
    # Exceptions
    "KeyErrorBase",
    "InvalidKeyLengthError",
    "InvalidContextError",
    "KeyEvolutionError",
    "SchedulerError",
    "ChainDepletedError",
    "SessionError",
    "InvalidSessionError",
    "SessionExpiredError",
    "ReplayAttackError",
    # Core Subsystems
    "KeyEvolutionEngine",
    "AdaptiveKeyScheduler",
    "ForwardKeyChain",
    "SessionKeyManager",
    "SessionMetadata",
]
