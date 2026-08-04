# KDR-CA-AEAD API Reference

Complete API specification for the `crypto` library, cellular automata permutation engines, key schedules, security analysis modules, and HTTP endpoints.

---

## 1. High-Level Cryptographic Engine (`crypto.engine`)

### `encrypt_bytes(data: bytes, key: bytes, associated_data: bytes = b"") -> EncryptedPackage`
Encrypts plaintext byte string `data` using 256-bit `key` with optional `associated_data`.

* **Parameters**:
  * `data` (`bytes`): Raw plaintext bytes to encrypt.
  * `key` (`bytes`): 32-byte (256-bit) secret master key.
  * `associated_data` (`bytes`, optional): Unencrypted metadata authenticated by HMAC-SHA256.
* **Returns**: `EncryptedPackage` containing salt, nonce, ciphertext, and MAC tag.
* **Raises**: `ValueError` if `key` is not 32 bytes long.

### `decrypt_bytes(package: EncryptedPackage, key: bytes, associated_data: bytes = b"") -> bytes`
Authenticates MAC tag and decrypts `package` using master `key`.

* **Parameters**:
  * `package` (`EncryptedPackage`): Valid encrypted package object.
  * `key` (`bytes`): 32-byte secret master key.
  * `associated_data` (`bytes`, optional): Must match associated data supplied during encryption.
* **Returns**: Decrypted plaintext `bytes`.
* **Raises**: `SecurityError` / `ValueError` if HMAC authentication tag verification fails (constant-time check).

### Class `EncryptedPackage`
Data model encapsulating authenticated encryption outputs.

* **Attributes**:
  * `salt` (`bytes`): 16-byte random salt used in HKDF key derivation.
  * `nonce` (`bytes`): 16-byte random initialization vector / nonce.
  * `ciphertext` (`bytes`): Encrypted byte sequence.
  * `mac` (`bytes`): 32-byte HMAC-SHA256 authentication tag.
* **Methods**:
  * `to_dict() -> dict`: Serializes package to dictionary.
  * `to_json() -> str`: Serializes package to JSON string.
  * `from_json(json_str: str) -> EncryptedPackage`: Deserializes JSON string to `EncryptedPackage`.

---

## 2. Key Schedule & Sub-Key Expansion (`crypto.key.derivation`)

### `derive_subkeys(master_key: bytes, salt: bytes, info: bytes = b"KDR-CA-AEAD-v1") -> SubKeys`
Expands master key into domain-separated sub-keys using HKDF-SHA256 (RFC 5869).

* **Output SubKeys**:
  * `rule_key` ($K_r$): 32 bytes for seeding CA Wolfram rule mutation sequence.
  * `cipher_key` ($K_c$): 32 bytes for cellular automata keystream generation.
  * `mac_key` ($K_a$): 32 bytes for HMAC-SHA256 Encrypt-then-MAC tag computation.

---

## 3. Cellular Automata Permutation Engine (`crypto.ca.engine`)

### Class `CellularAutomataEngine`
1D Wolfram Reversible Cellular Automata state engine.

* **Methods**:
  * `__init__(rule_seed: bytes)`: Initializes CA engine with HKDF rule key $K_r$.
  * `transform(data: bytes, cipher_key: bytes) -> bytes`: Applies reversible 1D CA rule transformations and keystream XOR diffusion.
  * `inverse_transform(data: bytes, cipher_key: bytes) -> bytes`: Applies exact inverse CA transformation for decryption.

---

## 4. Cryptanalysis & Benchmark Suite (`crypto.analysis`)

### Class `StrictAvalancheTester`
Performs bit-flip avalanche testing according to the Strict Avalanche Criterion (SAC).
* `evaluate_plaintext_avalanche(iterations: int = 1000) -> float`: Evaluates percentage of ciphertext bits inverted when 1 plaintext bit is flipped (Ideal: 50.0%).

### Class `EntropyAnalyzer`
* `shannon_entropy(data: bytes) -> float`: Calculates Shannon entropy of ciphertext bytes (Ideal: ~8.0 bits/byte).

---

## 5. Web REST API Endpoints (`app.py`)

### `POST /api/encrypt`
* **Request Body**: `{"key": "32-byte-hex-or-str", "payload": "text", "associated_data": "optional"}`
* **Response**: `{"status": "success", "package": {"salt": "...", "nonce": "...", "ciphertext": "...", "mac": "..."}}`

### `POST /api/decrypt`
* **Request Body**: `{"key": "...", "package": {...}, "associated_data": "..."}`
* **Response**: `{"status": "success", "plaintext": "..."}`
