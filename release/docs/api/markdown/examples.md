# KDR-CA-AEAD Executable Code Examples

The following code snippets are 100% working examples that execute directly against the `crypto` package.

---

## Example 1: High-Level Authenticated Bytes Encryption & Decryption

```python
from crypto import encrypt_bytes, decrypt_bytes

# 1. Prepare master key and secret payload
master_key = b"0123456789abcdef0123456789abcdef"  # 256-bit key
plaintext = b"CONFIDENTIAL EHR DIAGNOSTIC TELEMETRY DATA - PATIENT ID 99482"
associated_data = b"Header: EHR-Telemetry-v1|Device: Edge-Sensor-44"

# 2. Encrypt payload with AEAD authentication
package = encrypt_bytes(plaintext, master_key, associated_data=associated_data)
print(f"Ciphertext Length: {len(package.ciphertext)} bytes")
print(f"AEAD Tag (32B): {package.mac_tag.hex()}")

# 3. Decrypt and verify tag
decrypted_plaintext = decrypt_bytes(package, master_key, associated_data=associated_data)
assert decrypted_plaintext == plaintext
print("Decryption Successful: Plaintext recovered exactly!")
```

---

## Example 2: Struct/Dict Payload Encryption

```python
from crypto import encrypt_payload, decrypt_payload

password = "SecretPassword123"
payload_str = '{"patient_id": "P-90214", "heart_rate_bpm": 74, "blood_pressure": "120/80"}'

# Encrypt string payload
pkg = encrypt_payload(payload_str, password)

# Decrypt string payload
recovered_str = decrypt_payload(pkg, password)
assert recovered_str == payload_str
print("String Payload Encryption Roundtrip Passed!")
```

---

## Example 3: Low-Level HKDF Subkey Expansion & Dynamic CA Permutation Engine

```python
from crypto import KeySchedule, DynamicCAEngine

master_key = b"0123456789abcdef0123456789abcdef"
salt = b"1234567890123456"
nonce = b"123456789012"

# 1. Derive domain-separated subkeys
ks = KeySchedule(master_key, salt=salt, nonce=nonce)
print(f"Derived {len(ks.get_ca_rule_table())} Wolfram Rule Numbers")

# 2. Initialize Dynamic CA Engine
ca_engine = DynamicCAEngine(ks.get_ca_rule_table())

# 3. Execute candidate A-chain forward permutation
data_bytes = b"Hello KDR-CA-AEAD"
transformed_bytes = ca_engine.transform_forward(data_bytes)
print(f"Transformed State Vector: {transformed_bytes.hex()}")

# 4. Execute inverse permutation
recovered_bytes = ca_engine.transform_inverse(transformed_bytes)
assert recovered_bytes == data_bytes
print("Dynamic CA Engine Roundtrip Passed!")
```

---

## Example 4: Security Analysis & Statistical Randomness Suite

```python
from crypto import run_full_security_analysis

# Execute full security suite (NIST SP 800-22, SAC Avalanche, Entropy)
results = run_full_security_analysis()
print(f"Shannon Entropy: {results['randomness']['shannon_entropy']:.4f} bits/B")
print(f"Plaintext Avalanche Ratio: {results['plaintext_avalanche']['mean_avalanche']:.2f}%")
print(f"Key Avalanche Ratio: {results['key_avalanche']['mean_avalanche']:.2f}%")
```
