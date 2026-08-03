"""End-to-End Integration Tests & Property Invariant Verification for Phase 2.2 Key Subsystem.

Validates end-to-end interactions between:
- KeyEvolutionEngine
- AdaptiveKeyScheduler
- ForwardKeyChain
- SessionKeyManager
- HKDF Primitives
"""

import pytest
from crypto.key.adaptive_schedule import AdaptiveKeyScheduler, ForwardKeyChain
from crypto.key.evolution import (
    AUTH_KEY_LABEL,
    ENC_KEY_LABEL,
    ROUND_KEY_LABEL,
    SESSION_KEY_LABEL,
    KeyEvolutionEngine,
)
from crypto.key.session_keys import SessionKeyManager
from crypto.primitives.hkdf import hkdf, hkdf_expand, hkdf_extract


class TestPhase2KeyIntegration:
    """Integration test suite connecting all Phase 2.2 key evolution components."""

    def test_full_key_evolution_pipeline(self):
        """Verify full key derivation and scheduling pipeline."""
        engine = KeyEvolutionEngine(default_key_length=32)
        master_key = b"initial_master_key_bytes_1234567"

        # 1. Forward-secure ratcheting chain
        chain = ForwardKeyChain(initial_key=master_key, chain_length=50)
        current_master = chain.current_key()
        next_master = chain.next_key()

        assert next_master != current_master

        # 2. Session management
        session_mgr = SessionKeyManager(key_engine=engine)
        session_meta = session_mgr.create_session("sess_prod_01", master_key=next_master)
        assert session_mgr.validate_session("sess_prod_01") is True

        # 3. Derived session key
        session_key = engine.derive_session_key(next_master, session_id="sess_prod_01")
        assert len(session_key) == 32

        # 4. Adaptive key scheduler
        scheduler = AdaptiveKeyScheduler(
            mode=AdaptiveKeyScheduler.MODE_CYCLIC,
            round_sequence=[1, 2, 3],
        )

        rk1 = scheduler.next_key(engine, next_master)
        rk2 = scheduler.next_key(engine, next_master)

        assert rk1 == engine.derive_round_key(next_master, round_num=1)
        assert rk2 == engine.derive_round_key(next_master, round_num=2)

    def test_domain_separation_invariants(self):
        """Property Invariant: Different domain labels never produce identical keys for same master key."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_property_test_123"

        round_k = engine.derive_round_key(master, round_num=1)
        sess_k = engine.derive_session_key(master, session_id="1")
        epoch_k = engine.derive_epoch_key(master, epoch_num=1)
        ctx_k = engine.derive_context_key(master, context=b"1")
        ca_k = engine.derive_ca_key(master, ca_id=1)
        auth_k = engine.derive_auth_key(master)
        enc_k = engine.derive_encryption_key(master)

        all_keys = [round_k, sess_k, epoch_k, ctx_k, ca_k, auth_k, enc_k]
        assert len(set(all_keys)) == len(all_keys), "Domain separation collision invariant violated!"

    def test_context_sensitivity_invariants(self):
        """Property Invariant: Changing context or master key changes derived key."""
        engine = KeyEvolutionEngine()
        m1 = b"master_key_bytes_variant_11111111"
        m2 = b"master_key_bytes_variant_22222222"

        k_m1 = engine.derive_auth_key(m1)
        k_m2 = engine.derive_auth_key(m2)
        assert k_m1 != k_m2

        k_ctx1 = engine.derive_context_key(m1, context=b"ctx_A")
        k_ctx2 = engine.derive_context_key(m1, context=b"ctx_B")
        assert k_ctx1 != k_ctx2

    def test_hkdf_direct_interoperability(self):
        """Verify KeyEvolutionEngine outputs match direct RFC 5869 HKDF calculation."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_interop_test_12"

        derived_auth = engine.derive_auth_key(master, key_length=32)

        # Re-derive directly using HKDF extract and expand from crypto.primitives.hkdf
        prk = hkdf_extract(salt=AUTH_KEY_LABEL, ikm=master)
        expected_auth = hkdf_expand(prk=prk, info=AUTH_KEY_LABEL, length=32)

        assert derived_auth == expected_auth
