# Study 11B — real behavioral predictions and real EEG signal preflight (development report)

**Date:** 2026-10-09. **Status:** EXPLORATORY, non-preregistered, post-hoc model choices, not externally replicated, no theory of subjective consciousness established.

## Research question and provenance

Can previous *reported perceptual experiences* and confidence improve predictions of later subjective detection/confidence, beyond pulse presence/intensity? This is a study of serial dependence in **behavioral reports**, not measured awareness intensity. A separate technical preflight asks whether raw EEG files and their recorded actuator channel can be decoded and synchronized.

Source: Pereira et al., *Evidence accumulation relates to perceptual consciousness and monitoring*, Nature Communications 12:3261 (2021), DOI 10.1038/s41467-021-23540-y, [OpenNeuro ds001785 v1.1.1](https://openneuro.org/datasets/ds001785), pinned upstream Git commit `53be0167e7068aba693d57923eb4c9c037878159`. The original investigators already associated evidence accumulation with detection/confidence; our analysis does **not** establish scientific novelty.

## Independently reproduced aggregate trial counts

- 18 distinct participants in public `participants.tsv`; 8,690 adaptive trial starts.
- 8,662 complete eligible events (one hit/miss/correct-rejection/false-alarm marker, valid 0–1 confidence, and corresponding response markers).
- 5,630 training trials (first 65% of each subject's chronological starts) and 3,032 strictly later evaluation trials. Same splits for all models; training transformation fitted on training portion only. No trial-level outcomes or EEG bytes archived in this repository.
- Participants are independent reporting units, rather than treating 3,032 correlated test trials as independent people.

## Exploratory behavioral results

**Detection report**, mean across 18 participants, lower log loss is better:

| Predictor information | Held-out log loss |
|---|---:|
| Individual baseline yes rate | 0.66152 |
| Physical pulse presence + nominal amplitude | 0.62329 |
| Pulse + elapsed-trial progress | 0.67671 |
| Pulse + past reports / confidence / recent-yes rate | **0.59219** |
| Pulse + past reports AND elapsed-trial progress | 0.60727 |
| Pulse + *shuffled* past reports, time preserved | 0.67817 |
| Pulse + shuffled entire history/time | 0.61938 |

The exploratory participant-bootstrap paired difference for **pulse + past reports** minus **pulse only** was **−0.03110** log-loss units (95% descriptive interval **[−0.05917, −0.00533]**). Adding an elapsed-trial trend weakened this apparent gain; for the full history+time candidate vs pulse-only, difference **−0.01602**, interval **[−0.05999, +0.03406]**. Thus model choice changes the strength of this result. The more elaborate model is not automatically better.

**Confidence report**, mean squared error (lower is better):

| Predictor information | Held-out confidence MSE |
|---|---:|
| Individual training-set mean | 0.017940 |
| Pulse presence + nominal amplitude | 0.017303 |
| Pulse + time progress | 0.017434 |
| Pulse + past reports, prior confidence, and recent-yes rate | **0.016172** |
| Pulse + past reports AND elapsed-trial progress | 0.016038 |

The participant-bootstrap difference **pulse + past minus pulse only** was **−0.001131** MSE, descriptive interval **[−0.001849, −0.000481]**. This is suggestive of a useful serial statistical association but does not establish a causal influence of previous experience.

Across the 18 test populations, the mean within-participant **reported confidence was 0.823**, while the average objective response accuracy from hit/miss/correct-rejection/false-alarm codes was **0.547**. This discrepancy illustrates why **confidence cannot automatically be treated as a scalar of phenomenal consciousness**. It also requires caution because reported certainty and objective correctness can differ for response bias, challenging thresholds, and instrument-calibration reasons.

### Limitations and possible alternative explanations

1. The task used an **adaptive stimulus staircase**: earlier reports influence later pulse amplitudes. Lagged reports might predict the staircase's evolving difficulty rather than encode an intrinsic, evolving perceptual self-model. A causal "learning builds consciousness" interpretation is **not warranted**.
2. Models, parameters and dataset were selected after our simulated studies; the descriptive bootstrap intervals are **not preregistered statistical tests**, no multiple-model selection correction, and individual model coefficients weren't tuned in nested held-out folds.
3. These are within-participant time-forward tests, **not** transfer to never-seen people. Greater predictive accuracy does not imply more actual subjective experience.
4. The stimulus presence variable is derived from the dataset's original signal-detection outcome coding. This is an experimental condition, **not** a neural recording or current subjective report supplied to the model.
5. Reading reported confidence at time t never supplies the same-trial confidence to detection predictors; only prior reports enter history predictors. All calculations can be reproduced from pinned public metadata.

## Genuine EEG signal feasibility — important negative technical result

- GitHub's bounded public-source access verified `sub-01` **.set = 35,381,760 bytes** and `.fdt = 1,241,670,720 bytes**, with HTTP 206 range support.
- The actual .set header loaded: **71 channels**, 1024 Hz sampling, 4,372,080 samples. The independent BIDS `channels.tsv` identifies **BIP3 (channel index 64)** as the actuator **AUDIO** channel; EEG and BIDS channel names/order agree.
- A second bounded test sampled the real .fdt AUDIO channel in **12 physically delivered** and **12 catch** trials near the **nominal** `trial_start + stimon` prediction. Median baseline-corrected post/pre audio RMS ratios were **0.996** delivered versus **0.975** catch; 230 Hz relative spectral metrics were **1.074** versus **0.882**. These small and inconsistent differences did **not** validate the true pulse onset. A physiological EEG–perceptual report comparison has therefore **not** been performed.
- Actual audio signal bytes and individual reports were processed transiently in GitHub-hosted memory only, not stored or committed. A future investigator must inspect the original acquisition trigger/audio waveform alignment and artifact handling. Neither positive nor negative consciousness conclusions can follow from a failed time-alignment attempt.

## Reproduce and evaluate

```bash
cd studies/neural_detection11b
python -m pip install "numpy==2.2.6" "scikit-learn==1.6.1" "scipy==1.15.3"
python -m unittest -v test_behavioral_models.py test_inspect_signal.py
python behavioral_models.py
python inspect_signal.py
```

Independent GitHub runs: [behavioral aggregate and seven tests](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models/actions/runs/37945974088); [real EEG auxiliary recording and five reader tests](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models/actions/runs/37945301050). See `behavioral_aggregate.json` for full descriptive contrasts and `audit_events.py` for event inclusion decisions.

**Bottom line:** Prior behavioral information provides a limited, exploratory prediction advantage in this task, especially for subsequent confidence reports, but this may come from the adaptive task itself. We have real neural recording access, **not valid EEG timing or a compression finding**. Consciousness or extra dimensions are not measured.
