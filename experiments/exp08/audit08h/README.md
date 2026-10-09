# Emergence Lab / Experiment 08H — Uncued changes and intervention identifiability

**Status:** post-08G EXPLORATORY DEVELOPMENT. Not preregistered. No model of phenomenal experience, no evolved architecture, and no independent peer review.

The toy agent calibrates a linear action/sensor mapping, detects anomalous feedback **without being told when the world changed**, and may request informative commands. It uses a **researcher-supplied factorization** into action-dependent displacement, action-independent physical drift, and sensor-only drift; it does **not invent causal concepts**. Action policies include repeating one command, random probing, a balanced fixed cycle, and an engineered D-optimal policy that probes after an alarm.

Main developmental evaluation: **96 paired base seeds, seven world types, four policies**, yielding 2,688 correlated synthetic episodes. Stress evaluation: **48 different base seeds**, three noise levels, one versus two sensors, cyclic versus adaptive policy, and fixed versus noise-calibrated surprise thresholds.

The low-noise two-sensor agent correctly attributes the five modeled change types, but a fixed cyclic policy ties it; the adaptive policy saves nondefault commands partly **by construction**. At increased noise, accuracy and false-alarm performance deteriorate badly. Without an independent reference sensor, an external physical drift and an equivalent bias in the primary sensor are **exactly observationally indistinguishable**, as asserted in the tests. All findings are limited to the artificial linear environment.

Read [DEVELOPMENT_AUDIT_08H.md](DEVELOPMENT_AUDIT_08H.md) before drawing scientific conclusions.

## Reproduce

Python 3.11+ and NumPy. From this directory:

```bash
python -m unittest -v test_exp08h.py
OPENBLAS_NUM_THREADS=1 python exp08h.py --seeds 96 --out /tmp/exp08h-main
OPENBLAS_NUM_THREADS=1 python stress.py --seeds 48 --out /tmp/exp08h-stress
```

Compare the generated summaries against `development/summary.json` and `development_stress/summary.json`. Correlated cases sharing a base seed are not independent research samples. Data and failed settings are retained. No confirmatory seed set exists for this study.

## External science / novelty

Active experiment design and dual control predate this work. See the citations and limitations in the methods report. The next major scientific requirement is an **independently authored nonlinear environment and external methodological review**, with matched-compute and matched-sensor baselines before any confirmatory study is preregistered. Do not claim we have created self-awareness or discovered the origin of consciousness.
