# Experiment Replication Workflows

## Workflow 1: Re-Running SAC Avalanche Computation
```powershell
$env:PYTHONPATH="."
python crypto/analysis/avalanche.py
```
Expected Output: Plaintext Avalanche Ratio ~ 50.12%.

## Workflow 2: Re-Running Shannon Entropy Evaluation
```powershell
$env:PYTHONPATH="."
python crypto/analysis/entropy.py
```
Expected Output: Entropy ~ 7.998 bits/byte.

## Workflow 3: Re-Running Comparative Throughput Benchmarks
```powershell
$env:PYTHONPATH="."
python crypto/analysis/benchmark.py
```
Expected Output: Throughput ~ 13.37 MB/s.
