# Known Limitations & Performance Constraints

- **Pure Python Execution Speed**: Sustained throughput is ~13.37 MB/s in pure Python without native C bindings.
- **1D CA Rule Space**: Current implementation focuses on 1D Wolfram rule permutations; higher-dimensional CA spaces require separate evaluation.
- **Thread Safety**: High-level state machines are re-entrant, but concurrent mutations of identical state objects should use thread locks.
