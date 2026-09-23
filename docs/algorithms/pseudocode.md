# KDR-CA-AEAD Publication Algorithm Specifications & Pseudocode

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**IEEE Mapping:** Section IV & Appendix A  

---

## Algorithm 1: HKDF Sub-Key Derivation & Expansion

```text
================================================================================
Algorithm 1: HKDF Sub-Key Derivation
================================================================================
Input  : Master Key K (Bytes), Salt S (16 Bytes), Nonce N (12 Bytes)
Output : KeyMaterial (K_r, K_c, K_a, RuleTable R)

1: PRK ← HKDF-Extract(Salt=S, IKM=K)
2: K_r ← HKDF-Expand(PRK, Info="KDR-CA-AEAD-v1-ca-rules|" || N, L=32)
3: K_c ← HKDF-Expand(PRK, Info="KDR-CA-AEAD-v1-cipher-key|" || N, L=32)
4: K_a ← HKDF-Expand(PRK, Info="KDR-CA-AEAD-v1-mac-key|" || N, L=32)
5: R   ← Tuple of 32 uint8 values extracted from K_r
6: return KeyMaterial(rule_seed=K_r, cipher_key=K_c, mac_key=K_a, rule_table=R)
================================================================================
```

---

## Algorithm 2: Candidate A-Chain Forward Dynamic CA Permutation

```text
================================================================================
Algorithm 2: Candidate A-Chain Forward Dynamic CA Permutation
================================================================================
Input  : Plaintext Bytes P = (p_0, p_1, ..., p_{N-1}), Rule Table R = (r_0, ..., r_31)
Output : Transformed Bytes T = (t_0, t_1, ..., t_{N-1})

1: prev_state ← 0xC5                           ▷ Initial feedback IV
2: delta ← 13                                  ▷ Dual-rule offset index
3: for i ← 0 to N-1 do
4:     R1 ← R[i mod 32]
5:     R2 ← R[(i + delta) mod 32]
6:     ca_byte ← Evaluate_ECA_Byte(position=i, rule1=R1, rule2=R2)
7:     shift_amt ← (R1 mod 7) + 1
8:     mixed_byte ← p_i ⊕ prev_state
9:     y1 ← (mixed_byte + ca_byte) mod 256
10:    y2 ← ROTR_8(y1, shift_amt)              ▷ Keyed circular right shift
11:    t_i ← y2 ⊕ R2
12:    prev_state ← t_i                        ▷ Update inter-byte chaining IV
13: end for
14: return T = (t_0, t_1, ..., t_{N-1})
================================================================================
```

---

## Algorithm 3: Candidate A-Chain Inverse Dynamic CA Permutation

```text
================================================================================
Algorithm 3: Candidate A-Chain Inverse Dynamic CA Permutation
================================================================================
Input  : Transformed Bytes T = (t_0, t_1, ..., t_{N-1}), Rule Table R = (r_0, ..., r_31)
Output : Plaintext Bytes P = (p_0, p_1, ..., p_{N-1})

1: prev_state ← 0xC5
2: delta ← 13
3: for i ← 0 to N-1 do
4:     R1 ← R[i mod 32]
5:     R2 ← R[(i + delta) mod 32]
6:     ca_byte ← Evaluate_ECA_Byte(position=i, rule1=R1, rule2=R2)
7:     shift_amt ← (R1 mod 7) + 1
8:     y2 ← t_i ⊕ R2
9:     y1 ← ROTL_8(y2, shift_amt)              ▷ Keyed circular left shift
10:    mixed_byte ← (y1 - ca_byte) mod 256
11:    p_i ← mixed_byte ⊕ prev_state
12:    prev_state ← t_i
13: end for
14: return P = (p_0, p_1, ..., p_{N-1})
================================================================================
```

---

## Algorithm 4: KDR-CA-AEAD Authenticated Encryption Pipeline

```text
================================================================================
Algorithm 4: KDR-CA-AEAD Authenticated Encryption Pipeline
================================================================================
Input  : Data P, Master Key K, Optional AD, Salt S, Nonce N
Output : EncryptedPackage(Version, S, N, CT, Tag)

1: If S is NULL then S ← CSPRNG_Generate_Bytes(16)
2: If N is NULL then N ← CSPRNG_Generate_Bytes(12)
3: KeyMat ← HKDF_SubKey_Derivation(K, S, N)
4: T ← Dynamic_CA_Forward_Permutation(P, KeyMat.rule_table)
5: KS ← HMAC_SHA256_CTR_Keystream(KeyMat.cipher_key, N, Length(T))
6: CT ← T ⊕ KS                                 ▷ Stream XOR Encryption
7: Tag ← HMAC_SHA256(KeyMat.mac_key, N || S || AD || CT)
8: return EncryptedPackage(version="KDR-CA-AEAD-v1", salt=S, nonce=N, ciphertext=CT, tag=Tag)
================================================================================
```

---

## Algorithm 5: KDR-CA-AEAD Authenticated Decryption Pipeline

```text
================================================================================
Algorithm 5: KDR-CA-AEAD Authenticated Decryption Pipeline
================================================================================
Input  : EncryptedPackage(S, N, CT, Tag), Master Key K, Optional AD
Output : Original Plaintext P (or AuthenticationError)

1: KeyMat ← HKDF_SubKey_Derivation(K, S, N)
2: ExpectedTag ← HMAC_SHA256(KeyMat.mac_key, N || S || AD || CT)
3: If ConstantTimeCompare(Tag, ExpectedTag) is FALSE then
4:     Raise AuthenticationError("AEAD Tag Mismatch! Ciphertext or AD Tampered.")
5: end if
6: KS ← HMAC_SHA256_CTR_Keystream(KeyMat.cipher_key, N, Length(CT))
7: T ← CT ⊕ KS                                 ▷ Stream XOR Decryption
8: P ← Dynamic_CA_Inverse_Permutation(T, KeyMat.rule_table)
9: return P
================================================================================
```
