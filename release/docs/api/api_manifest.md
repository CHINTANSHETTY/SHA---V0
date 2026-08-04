# API Manifest — KDR-CA-AEAD Public Module Inventory

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)
**Task:** Ashwitha – Phase 3.2.4 (API Documentation & Developer Reference)
**Doc Coverage:** 100% Public Symbols Documented

| Module Path | Public Classes | Public Functions | Documentation Status |
| :--- | :--- | :--- | :--- |
| `crypto` | None | None | ✅ Complete (100%) |
| `crypto.ca.engine` | None | evolve, evolve_step, validate_boundary, validate_generations, validate_state | ✅ Complete (100%) |
| `crypto.ca.mapping` | None | build_rule_lookup, compare_rule_sequences, cycle_rule, deserialize_rule_sequence, export_rule_configuration, generate_rule_sequence, get_rule, invert_rule_mapping, load_rule_configuration, map_rules, merge_rule_sequences, rotate_rule_sequence, rule_exists, rule_index, serialize_rule_sequence, unique_rules, validate_rule_sequence | ✅ Complete (100%) |
| `crypto.ca.rules` | None | get_neighborhood_output, parse_rule, rule_to_binary, validate_rule | ✅ Complete (100%) |
| `crypto.ca.utils` | None | chunk_state, compare_states, copy_state, flatten_states, hamming_distance, int_to_state, invert_state, matrix_to_states, one_state, pad_state, population_count, random_state, state_from_string, state_to_int, state_to_string, states_to_matrix, trim_state, validate_bit, validate_state_length, validate_width, xor_states, zero_state | ✅ Complete (100%) |
| `crypto.engine.encrypt` | None | encrypt_bytes, encrypt_payload | ✅ Complete (100%) |
| `crypto.engine.decrypt` | None | decrypt_bytes, decrypt_payload | ✅ Complete (100%) |
| `crypto.engine.dynamic_ca` | DynamicCAEngine | apply_keyed_ca_forward, apply_keyed_ca_inverse | ✅ Complete (100%) |
| `crypto.engine.key_schedule` | KeyMaterial, KeySchedule | None | ✅ Complete (100%) |
| `crypto.primitives.hkdf` | None | hkdf, hkdf_expand, hkdf_extract | ✅ Complete (100%) |
| `crypto.primitives.hmac` | None | generate_hmac, verify_hmac | ✅ Complete (100%) |
| `crypto.primitives.random` | None | generate_nonce, generate_salt | ✅ Complete (100%) |
| `crypto.models.package` | EncryptedPackage | None | ✅ Complete (100%) |
| `crypto.models.exceptions` | AuthenticationError, CorruptedPayloadError, CryptoError, KeyDerivationError | None | ✅ Complete (100%) |
| `crypto.analysis.security_analysis` | None | generate_security_report_markdown, run_full_security_analysis | ✅ Complete (100%) |
| `crypto.analysis.benchmark_runner` | None | generate_benchmark_report_markdown, run_benchmark_pipeline, run_full_benchmark_suite | ✅ Complete (100%) |
| `crypto.analysis.final_validation` | None | generate_consolidated_tables, generate_experiment_configuration, generate_final_evaluation_report, generate_publication_figures, generate_reproducibility_markdown, run_final_validation_pipeline, verify_end_to_end_pipeline | ✅ Complete (100%) |
