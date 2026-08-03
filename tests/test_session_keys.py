"""Unit tests for SessionKeyManager (crypto/key/session_keys.py)."""

import time
import pytest
from crypto.key.session_keys import (
    InvalidSessionError,
    ReplayAttackError,
    SessionExpiredError,
    SessionKeyManager,
)


class TestSessionKeyManager:
    """Tests for SessionKeyManager lifecycle, TTL, rotation, and replay prevention."""

    def test_session_lifecycle(self):
        """Verify session creation, validation, and metadata export."""
        mgr = SessionKeyManager()
        master = b"master_key_bytes_123456789012345"

        meta = mgr.create_session("sess_001", master_key=master, ttl_seconds=60, max_uses=5)
        assert meta["session_id"] == "sess_001"
        assert meta["is_active"] is True
        assert meta["usage_count"] == 0

        # Validate and increment usage
        assert mgr.validate_session("sess_001") is True
        info = mgr.export_metadata("sess_001")
        assert info["usage_count"] == 1

        # Close session
        mgr.close_session("sess_001")
        with pytest.raises(SessionExpiredError):
            mgr.validate_session("sess_001")

    def test_max_uses_replay_prevention(self):
        """Verify max uses limit triggers ReplayAttackError."""
        mgr = SessionKeyManager()
        master = b"master_key_bytes_123456789012345"

        mgr.create_session("sess_limit", master_key=master, max_uses=2)
        assert mgr.validate_session("sess_limit") is True  # use 1
        assert mgr.validate_session("sess_limit") is True  # use 2

        with pytest.raises(ReplayAttackError):
            mgr.validate_session("sess_limit")  # use 3 -> error

    def test_ttl_expiration(self):
        """Verify session expiration when TTL passes."""
        mgr = SessionKeyManager()
        master = b"master_key_bytes_123456789012345"

        mgr.create_session("sess_ttl", master_key=master, ttl_seconds=0.01)
        time.sleep(0.02)  # wait for TTL to expire

        with pytest.raises(SessionExpiredError):
            mgr.validate_session("sess_ttl")

    def test_renew_and_rotate_keys(self):
        """Verify session renewal and key version rotation."""
        mgr = SessionKeyManager()
        master1 = b"master_key_bytes_123456789012345"
        master2 = b"master_key_bytes_543210987654321"

        mgr.create_session("sess_rotate", master_key=master1, max_uses=1, key_version="v1")
        mgr.validate_session("sess_rotate")

        # Rotate key to v2
        rotated = mgr.rotate_keys("sess_rotate", new_master_key=master2, new_version="v2")
        assert rotated["key_version"] == "v2"
        assert rotated["usage_count"] == 0

        # Should validate successfully now
        assert mgr.validate_session("sess_rotate") is True
