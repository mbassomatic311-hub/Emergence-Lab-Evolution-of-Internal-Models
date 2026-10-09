# Experiment 08J — Equal-budget action selection for causal feedback learning

**Classification:** exploratory computational development, unregistered and not externally reviewed. No evidence or measure of phenomenal consciousness. This experiment reuses the author-designed 08I nonlinear world, not an independent third-party simulation.

## Question

Given exactly 30 opportunities for nonzero probing actions, can a label-free learner choose *which motor command* to test to improve next-step sensory prediction on standardized evaluation states, versus simple scripted exploration? **Probe times are preset**; the experiment does *not* demonstrate autonomous choice of when to conduct an experiment. We do not claim autonomous discovery of causes, selfhood or architecture.

## Research files

- [`experiment08j.py`](experiment08j.py): action choice, inherited 08I nonlinear world, predictive models, paired comparisons.
- [`test_experiment08j.py`](test_experiment08j.py): 12 software and protocol-invariant tests.
- [`check_reproduction.py`](check_reproduction.py): exact row/schema validation and numerical tolerance checks across machines.
- [`DEVELOPMENT_AUDIT_08J.md`](DEVELOPMENT_AUDIT_08J.md): methods, results, limitations.
- `development_main/`: 24 seeds x six changes x six controllers (low noise, 864 score rows).
- `development_high_noise/`: same seed namespace, higher sensor noise (864 score rows).
- `SHA256SUMS.txt`: checksums of all committed source, data and notes (excluding manifest itself).

## Run from the repository

This directory is `experiments/exp08/audit08j` and uses its sibling `../audit08i/experiment08i.py` as the *existing version-controlled* world definition. Requires Python 3.11+ and `numpy==2.3.5`.

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest -v test_experiment08j.py
OPENBLAS_NUM_THREADS=1 python experiment08j.py --seeds 24 --noise .025 --out /tmp/08j-low
OPENBLAS_NUM_THREADS=1 python experiment08j.py --seeds 24 --noise .13 --out /tmp/08j-high
python check_reproduction.py --reference development_main --candidate /tmp/08j-low
python check_reproduction.py --reference development_high_noise --candidate /tmp/08j-high
```

The downloadable complete ZIP also includes a copy of 08I source for standalone reconstruction. All 08J analyses are post-hoc/exploratory; no confirmatory seeds have been touched.
