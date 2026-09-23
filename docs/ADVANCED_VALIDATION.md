# KDR-CA-AEAD Advanced Validation & Error Handling Specification (Phase 4.1 Task 7)

**Author:** Nagamrutha (Security Analysis & Cryptographic Validation Lead)  
**Algorithm:** KDR-CA-AEAD  
**Date:** August 2026  
**Status:** Completed & Documented  

---

## Executive Summary

This document specifies the **Advanced Validation Framework** for the **KDR-CA-AEAD** cryptographic research engine. The framework ensures strict input validation, boundary condition enforcement, exception standardization, and automated reporting across all cryptographic components prior to execution.

---

## 1. Validation Workflow Architecture

```
                                  [API Call Input]
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
                 [encrypt_bytes]                  [decrypt_bytes]
                         │                               │
             ┌───────────┴───────────┐       ┌───────────┴───────────┐
             ▼                       ▼       ▼                       ▼
    [validate_master_key]  [validate_payload]  [validate_package] [validate_master_key]
             │                       │               │                       │
             └───────────┬───────────┘               └───────────┬───────────┘
                         ▼                                       ▼
             [KeySchedule / HKDF-SHA256]            [AEAD Tag Verification (hmac)]
                         │                                       │
            (Sub-keys: Kc, Km, Kr)                         (Pass or Abort)
                         │                                       │
             [Dynamic CA + CTR-PRNG]                [XOR Stream + Inverse K-DCA]
```

---

## 2. Component Validation Rules

### 1. Master Key & Password Validation (`validate_master_key`)
- **Rules:** Must not be `None`; must be `bytes`, `bytearray`, or `str`; length must be $\ge 1$ byte. Whitespace-only strings are rejected.
- **Exception:** `CryptoError`.

### 2. Salt Validation (`validate_salt`)
- **Rules:** Must not be `None`; must be `bytes` or `bytearray`; exact length must be 16 bytes (128 bits).
- **Exception:** `CryptoError`.

### 3. Nonce Validation (`validate_nonce`)
- **Rules:** Must not be `None`; must be `bytes` or `bytearray`; exact length must be 12 bytes (96 bits).
- **Exception:** `CryptoError`.

### 4. Payload Data Validation (`validate_payload_data`)
- **Rules:** Must not be `None`; must be `bytes`, `bytearray`, or `str`; length must be $> 0$ bytes and $\le 100 \text{ MB}$.
- **Exception:** `CryptoError`.

### 5. Encrypted Package Validation (`validate_encrypted_package`)
- **Rules:** Must be an instance of `EncryptedPackage`; protocol version string non-empty; 16-byte salt; 12-byte nonce; non-empty ciphertext; 32-byte HMAC tag.
- **Exception:** `CorruptedPayloadError`.

### 6. CA Rule Table Validation (`validate_ca_rule_table`)
- **Rules:** Must be a sequence of 256 integers; each integer in range $[0, 255]$.
- **Exception:** `CryptoError`.

### 7. HMAC Tag Validation (`validate_hmac_tag`)
- **Rules:** Must be `bytes` or `bytearray`; exact length must be 32 bytes (256 bits).
- **Exception:** `CorruptedPayloadError`.

### 8. HKDF Parameters Validation (`validate_hkdf_parameters`)
- **Rules:** Input Keying Material (IKM) non-empty; requested length $1 \le L \le 8160$ bytes (RFC 5869 255 * 32 limit).
- **Exception:** `KeyDerivationError`.

---

## 3. Exception Hierarchy & Error Codes

All cryptographic exceptions inherit from `CryptoError` (`crypto/models/exceptions.py`):

```
Base Exception: CryptoError
 ├── AuthenticationError      (Raised on AEAD tag verification failure or wrong key)
 ├── KeyDerivationError       (Raised on invalid HKDF/PBKDF parameters)
 └── CorruptedPayloadError    (Raised on malformed JSON/hex payload or tag corruption)
```

| Exception Type | Trigger Condition | HTTP / API Status Code |
| :--- | :--- | :--- |
| `CryptoError` | Invalid key, null argument, or improper type | 400 Bad Request |
| `AuthenticationError` | AEAD tag verification failure or tampered payload | 401 Unauthorized |
| `KeyDerivationError` | HKDF parameters exceed RFC limits | 400 Bad Request |
| `CorruptedPayloadError` | Hex decoding failure or missing schema key | 422 Unprocessable Entity |

---

## 4. Validation Report JSON Schema (`reports/validation_summary.json`)

The validation report exporter generates JSON structured as follows:

```json
{
  "title": "KDR-CA-AEAD Cryptographic System Validation Report",
  "timestamp_epoch": 1785838800.0,
  "total_checks": 12,
  "passed": 12,
  "failed": 0,
  "warnings": 0,
  "status": "PASS",
  "execution_duration_ms": 1.25,
  "checks": [
    {
      "check_id": "VAL-01",
      "component": "MasterKey",
      "description": "Validate master key non-null and non-empty byte buffer",
      "passed": true,
      "warning": false,
      "message": "Validation successful."
    }
  ]
}
```
