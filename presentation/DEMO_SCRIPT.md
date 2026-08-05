# Live Demonstration Script

This script provides step-by-step instructions for conducting a live 5-minute software demonstration of **KDR-CA-AEAD** at conference presentation booths or workshop sessions.

---

## 1. Preparation Checklist
- [x] Laptop running Python 3.10+ with repository cloned.
- [x] Terminal open in root repository directory (`SHA---V0`).
- [x] Flask Web Application server ready to start (`python app.py`).
- [x] Web browser open at `http://127.0.0.1:5000`.

---

## 2. Live Demo Sequence (5 Minutes)

### Minute 0:00 – 1:00: Overview & CLI Encryption
**Presenter**: *"Welcome! Today we demonstrate KDR-CA-AEAD, a lightweight authenticated encryption scheme powered by dynamic cellular automata."*

**Action**: Run command-line encryption in terminal:
```bash
python encrypt.py --input "Confidential Telemetry Payload" --key "Research_Master_Key_32Bytes_Long!" --output package.json
```
**Presenter**: *"Notice how `encrypt.py` outputs a structured JSON package containing salt, nonce, ciphertext, and HMAC-SHA256 authentication tag."*

---

### Minute 1:00 – 2:30: CLI Decryption & Authentication Tampering
**Presenter**: *"Now let's verify decryption and demonstrate Encrypt-then-MAC authentication security."*

**Action 1**: Execute normal decryption:
```bash
python decrypt.py --input package.json --key "Research_Master_Key_32Bytes_Long!"
```
*Output: `Confidential Telemetry Payload`*

**Action 2**: Tamper with `package.json` ciphertext:
```bash
# Modify 1 character in package.json ciphertext
python decrypt.py --input package.json --key "Research_Master_Key_32Bytes_Long!"
```
*Output: `InvalidTag Exception: Authentication tag verification failed!`*

**Presenter**: *"Notice that tampering with even a single bit immediately aborts decryption before processing stream bytes, preventing unauthenticated access."*

---

### Minute 2:30 – 4:00: Interactive Web GUI Walkthrough
**Presenter**: *"For visual inspection, we provide a Web GUI application."*

**Action**:
1. Run `python app.py`.
2. Open `http://127.0.0.1:5000`.
3. Input plaintext: `Medical Sensor Telemetry Data`.
4. Input master key and associated data.
5. Click **Encrypt Payload** to view real-time hex encoding of salt, nonce, ciphertext, and tag.
6. Click **Decrypt Payload** to confirm exact roundtrip recovery.

---

### Minute 4:00 – 5:00: Benchmark & Reproducibility Verification
**Presenter**: *"Finally, let's run the master reproducibility suite."*

**Action**: Run in terminal:
```bash
python crypto/benchmarking/benchmark_report.py
```
**Presenter**: *"The benchmark engine computes Strict Avalanche Criterion (SAC) ratios (50.12%) and writes comparative performance charts directly to the `reports/` folder."*
