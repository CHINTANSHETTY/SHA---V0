# Architectural Decision Records (ADRs)

## ADR-001: Selection of HKDF-SHA256 for Sub-Key Expansion
- **Date**: 2026-08-01
- **Status**: Accepted
- **Context**: Needed domain-separated sub-keys for rule mutations ($K_r$), keystream cipher ($K_c$), and MAC ($K_a$).
- **Decision**: Adopt RFC 5869 compliant HKDF-SHA256 with explicit info tags (`kdr-ca-rule-v1`, `kdr-ca-cipher-v1`, `kdr-ca-mac-v1`).

## ADR-002: Encrypt-then-MAC Payload Format
- **Date**: 2026-08-02
- **Status**: Accepted
- **Decision**: Adopt Encrypt-then-MAC pattern over MAC-then-Encrypt to guarantee unforgeability under chosen-ciphertext attacks (INT-CTXT).
