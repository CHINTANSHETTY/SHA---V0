# Step-by-Step Hands-On Educational Tutorial

Welcome to the **KDR-CA-AEAD** hands-on tutorial. In this guide, you will learn how to set up the framework, perform encryption and decryption via Python scripts and CLI commands, run performance benchmarks, and generate visual evaluation reports.

---

## 1. System Setup & Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
python -m venv venv
```

Activate the environment:
- **Windows**: `.\venv\Scripts\Activate.ps1`
- **Linux/macOS**: `source venv/bin/activate`

Install packages:
```bash
python -m pip install -r requirements.txt
```

---

## 2. Running Basic Encryption and Decryption

### Using Python API
Create a script named `quick_demo.py`:

```python
from crypto import encrypt_bytes, decrypt_bytes

# Define master key (32 bytes)
key = b"01234567890123456789012345678901"
message = b"Educational Cryptography Payload"
ad = b"Session-ID=1001"

# 1. Encrypt
package = encrypt_bytes(message, key, associated_data=ad)
print(f"Salt (hex): {package['salt']}")
print(f"Nonce (hex): {package['nonce']}")
print(f"Ciphertext (hex): {package['ciphertext']}")
print(f"HMAC Tag (hex): {package['tag']}")

# 2. Decrypt
decrypted_payload = decrypt_bytes(package, key, associated_data=ad)
print(f"Decrypted: {decrypted_payload.decode('utf-8')}")
assert decrypted_payload == message
```

Run the script:
```bash
python quick_demo.py
```

---

## 3. Using Standalone Command Line Utilities

### Encrypt a string to a JSON package file:
```bash
python encrypt.py --input "Top Secret Lecture Notes" --key "My_32_Byte_Secret_Key_For_KDR" --output package.json
```

### Decrypt the JSON package file:
```bash
python decrypt.py --input package.json --key "My_32_Byte_Secret_Key_For_KDR"
```

---

## 4. Benchmark Execution & Visual Report Generation

Run the empirical benchmark engine:

```bash
python crypto/benchmarking/benchmark_report.py
```

This will run throughput, latency, and Strict Avalanche Criterion (SAC) tests, saving output reports to `reports/`.

---

## 5. Web GUI Demonstration

Launch the interactive web server:

```bash
python app.py
```
Open `http://127.0.0.1:5000` in your web browser. You can input plaintexts, master keys, and associated data, view the generated ciphertext and HMAC tags in real-time, and test authentication failure behavior by tampering with payload bytes.
