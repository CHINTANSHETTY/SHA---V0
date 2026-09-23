"""
Module:
    test_threat_model.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit & Integration Test Suite for Phase 3.2 Threat Modeling Subsystem.
    Verifies adversary taxonomy, capability boundaries, asset protection definitions,
    and automated threat mitigation evaluator.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import unittest

from crypto.security.threat_model import (
    get_threat_actor_taxonomy,
    get_attacker_capabilities,
    get_protected_assets,
    evaluate_threat_model,
)


class TestThreatModel(unittest.TestCase):
    """Test suite for Phase 3.2 Threat Modeling Subsystem."""

    def test_threat_actor_taxonomy(self):
        """Verify 5 threat actor profiles are defined with mitigations."""
        actors = get_threat_actor_taxonomy()
        self.assertEqual(len(actors), 5)
        actor_ids = [a.actor_id for a in actors]
        self.assertIn("ACTOR-01", actor_ids)
        self.assertIn("ACTOR-02", actor_ids)
        self.assertIn("ACTOR-03", actor_ids)
        self.assertIn("ACTOR-04", actor_ids)
        self.assertIn("ACTOR-05", actor_ids)

        for actor in actors:
            self.assertEqual(actor.mitigation_status, "MITIGATED")
            self.assertTrue(len(actor.capabilities) > 0)
            self.assertTrue(len(actor.non_capabilities) > 0)

    def test_attacker_capabilities(self):
        """Verify explicit listing of attacker capabilities vs non-capabilities."""
        caps = get_attacker_capabilities()
        self.assertIn("attacker_can_do", caps)
        self.assertIn("attacker_cannot_do", caps)
        self.assertTrue(len(caps["attacker_can_do"]) >= 5)
        self.assertTrue(len(caps["attacker_cannot_do"]) >= 5)

    def test_protected_assets(self):
        """Verify protected assets and trust boundaries."""
        assets = get_protected_assets()
        self.assertTrue(len(assets) >= 4)
        asset_names = [a.name for a in assets]
        self.assertIn("Master Secret Key Material", asset_names)
        self.assertIn("Plaintext Payload Data", asset_names)
        self.assertIn("Ciphertext & Associated Data Integrity", asset_names)
        self.assertIn("Session Nonce Uniqueness", asset_names)

    def test_evaluate_threat_model(self):
        """Verify automated threat model evaluation runner."""
        res = evaluate_threat_model()
        self.assertEqual(res["threat_actors_count"], 5)
        self.assertTrue(res["protected_assets_count"] >= 4)
        self.assertIn("SECURE", res["overall_threat_model_status"])


if __name__ == "__main__":
    unittest.main()
