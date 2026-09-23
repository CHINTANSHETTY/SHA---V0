# Practical Laboratory Exercises

These laboratory exercises provide students with hands-on assignments to experiment with **KDR-CA-AEAD**, analyze avalanche ratios, test MAC tag tampering, and compare performance metrics against standard ciphers.

---

## Lab Exercise 1: Encrypt-then-MAC Authentication Tampering

### Objective
Observe how constant-time HMAC-SHA256 authentication prevents ciphertext tampering.

### Tasks
1. Encrypt a payload using `encrypt.py` to create `package.json`.
2. Open `package.json` in a text editor and change a single hexadecimal digit in the `"ciphertext"` field.
3. Attempt to decrypt the modified file using `decrypt.py`.

### Reflection Questions
- What exception was thrown upon decryption?
- At what stage in the decryption process did authentication fail?
- Why is it critical to verify the MAC tag *before* executing stream decryption?

---

## Lab Exercise 2: Strict Avalanche Criterion (SAC) Measurement

### Objective
Calculate the bit flip probability of KDR-CA-AEAD plaintext avalanche.

### Tasks
1. Modify `crypto/benchmarking/benchmark_report.py` to flip 1 bit in a 512-bit plaintext payload.
2. Measure the number of bit changes in the resulting ciphertext over 1,000 random iterations.
3. Compute the average avalanche ratio:
   $$\text{SAC} = \frac{\text{Number of Flipped Ciphertext Bits}}{\text{Total Ciphertext Bits}}$$

### Expected Outcome
The resulting average ratio should lie within $[0.495, 0.505]$ (close to ideal $50.0\%$).

---

## Lab Exercise 3: Parameter Variation & Performance Scaling

### Objective
Analyze throughput scaling across message payload sizes.

### Tasks
1. Benchmark KDR-CA-AEAD execution time across payload sizes: $64\text{ B}$, $1\text{ KB}$, $64\text{ KB}$, $1\text{ MB}$, $10\text{ MB}$.
2. Plot execution time (ms) versus payload size (bytes) using `matplotlib`.
3. Determine whether the time complexity scales linearly $\mathcal{O}(N)$ with payload length.

---

## Lab Exercise 4: Comparative Benchmarking vs. AES-128-GCM

### Objective
Compare pure Python execution speed of KDR-CA-AEAD with standard library primitives.

### Tasks
1. Run the comparative benchmark script in `benchmarks/`.
2. Record the MB/s throughput for KDR-CA-AEAD and AES-128-GCM.
3. Discuss the architectural trade-offs between software bitwise CA evaluation and hardware AES-NI instructions.
