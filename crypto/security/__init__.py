"""
Module:
    __init__.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Cryptographic Security Evaluation, Threat Modeling, Formal Verification, Security Compliance,
    and Programmatic Security Audit Subsystem (Phases 3.1, 3.2, 3.3, 4.1, and 4.2).

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

from crypto.security.evaluation import (
    analyze_key_space,
    evaluate_brute_force_resistance,
    evaluate_brute_force_security,
    evaluate_tag_forgery_probability,
    analyze_authentication_tag_forgery,
    run_security_evaluation,
    run_comprehensive_security_evaluation,
)
from crypto.security.attacks import (
    evaluate_known_plaintext_attack,
    evaluate_chosen_plaintext_attack,
    evaluate_chosen_ciphertext_attack,
    evaluate_replay_attack_resistance,
    evaluate_nonce_uniqueness,
    run_all_attack_evaluations,
)
from crypto.security.threat_model import (
    ThreatActorProfile,
    AssetDefinition,
    get_threat_actor_taxonomy,
    get_attacker_capabilities,
    get_protected_assets,
    evaluate_threat_model,
)
from crypto.security.verification import (
    verify_confidentiality_properties,
    verify_integrity_properties,
    verify_authenticity_properties,
    verify_replay_protection_properties,
    assess_forward_secrecy,
    run_formal_verification_suite,
)
from crypto.security.compliance import (
    verify_nist_compliance,
    verify_owasp_compliance,
    verify_rfc_aead_compliance,
    generate_vulnerability_assessment,
    generate_consolidated_compliance_matrix,
    run_full_compliance_suite,
)
from crypto.security.security_audit import (
    audit_static_code_security,
    audit_cryptographic_primitives,
    audit_threat_mitigations,
    audit_security_checklist,
    run_full_security_audit,
)
from crypto.security.audit_report import (
    SecurityFinding,
    get_default_audit_findings,
    generate_audit_report,
)

__all__ = [
    "analyze_key_space",
    "evaluate_brute_force_resistance",
    "evaluate_brute_force_security",
    "evaluate_tag_forgery_probability",
    "analyze_authentication_tag_forgery",
    "run_security_evaluation",
    "run_comprehensive_security_evaluation",
    "evaluate_known_plaintext_attack",
    "evaluate_chosen_plaintext_attack",
    "evaluate_chosen_ciphertext_attack",
    "evaluate_replay_attack_resistance",
    "evaluate_nonce_uniqueness",
    "run_all_attack_evaluations",
    "ThreatActorProfile",
    "AssetDefinition",
    "get_threat_actor_taxonomy",
    "get_attacker_capabilities",
    "get_protected_assets",
    "evaluate_threat_model",
    "verify_confidentiality_properties",
    "verify_integrity_properties",
    "verify_authenticity_properties",
    "verify_replay_protection_properties",
    "assess_forward_secrecy",
    "run_formal_verification_suite",
    "verify_nist_compliance",
    "verify_owasp_compliance",
    "verify_rfc_aead_compliance",
    "generate_vulnerability_assessment",
    "generate_consolidated_compliance_matrix",
    "run_full_compliance_suite",
    "audit_static_code_security",
    "audit_cryptographic_primitives",
    "audit_threat_mitigations",
    "audit_security_checklist",
    "run_full_security_audit",
    "SecurityFinding",
    "get_default_audit_findings",
    "generate_audit_report",
]
