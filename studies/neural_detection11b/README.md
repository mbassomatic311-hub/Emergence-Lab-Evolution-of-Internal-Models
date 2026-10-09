# Study 11B — Public tactile detection EEG data: feasibility and alignment audit

**Status: exploratory METHODS PREFLIGHT, not preregistered. No EEG signal processed and no new result concerning human conscious experience.** Study 11 (poetry EEG) remains blocked by an unverified 212-to-210 presentation/ratings mismatch; this is a separate backup, not a silent replacement for Study 11.

## Data, scope and verified advantages

- Pereira et al., *Evidence accumulation relates to perceptual consciousness and monitoring*, *Nature Communications* **12**, 3261 (2021). https://doi.org/10.1038/s41467-021-23540-y
- [OpenNeuro ds001785 v1.1.1](https://openneuro.org/datasets/ds001785), DOI **10.18112/openneuro.ds001785.v1.1.1**, original repository `OpenNeuroDatasets/ds001785`, metadata pinned to commit `53be0167e7068aba693d57923eb4c9c037878159`.
- The task presents near-threshold tactile pulses and interleaved catch trials. Participants report detection and confidence while EEG is recorded.
- Crucially, **each BIDS adaptive-task event row contains event timings AND detection-related `sdt` information and confidence**. Later rows in the same trial encode `hit`, `miss`, `cr`, `fa`, `conf` and `conf-resp`. No separate speculative stimulus-to-rating join is necessary.
- The public `participants.tsv` exposes **18 participants**, even though the accompanying published study describes a larger healthy volunteer sample. Do not assume all 20 original participants are represented or usable.
- The `.set`/`.fdt` EEG objects are git-annex links in the plain GitHub mirror; the real signal bytes must be obtained from OpenNeuro/NEMAR before claiming EEG analysis.
- [NEMAR mirror](https://nemar.org/dataset/on001785) allows subset downloads; the full collection is large. Download one subject only to verify signal/metadata/trigger synchronization before attempting a group-level model.

## What's already audited (metadata only)

The reproducible `audit_events.py` script fetches *public text event files only* at the pinned Git commit, groups events by `stim-adapt` start and checks whether there is exactly one first-order outcome event plus matching confidence markers. It refuses to guess missing outcomes or confidence. It counts candidate 500 ms stimulus-relative EEG windows as **nominal only**, not physical/electrical alignment.

Initial inspection of all 18 public event files found **8,690 adaptive-task starts**; **28** lacked a unique explicit detection outcome; **one** lacked valid confidence; two participants had fewer than 500 starts (440 and 250). These are exploratory *data-quality results* to be independently confirmed by GitHub CI. Some files have extra threshold-related events; a strict four-row assumption fails and is intentionally not used.

**Do not interpret confidence as a direct consciousness intensity scale.** It is the participant's subjective confidence that their detection decision was correct, potentially influenced by task difficulty, attention and response strategy.

## Proposed EEG analysis — NOT RUN

**Question:** Can early pre-report neural dynamics compressed into four or eight learned dimensions predict (A) whether the participant reports detecting a tactile pulse, and (B) their confidence, beyond stimulus presence, physical pulse intensity and baseline behavior? A positive result would indicate a **predictive association**, not a proof that neural compression generates conscious experience.

1. Validate actual EEGLAB `.set` plus `.fdt` from **one** participant; verify sampling rate, channel types, event alignment and timing of physical vibrotactile pulses. The `stim-adapt` event is a trial start, **not automatically stimulus onset**. A candidate stimulus event is `onset + stimon`; check this against the recorded audio actuator channel and EEG event samples. Catch trials have no delivered pulse, so this pseudo-onset requires independent audit.
2. Construct pre-report epochs only, e.g. −0.2 to +0.5 s relative to validated physical/pseudo onset, baseline-correct and reject artifacts using signal-based criteria determined before inspecting detection outcomes. **Stop** if epoch overlaps the participant's decision or motor response, or stimulus timing is ambiguous.
3. Use first-order report = `hit` or `fa` (yes), `miss` or `cr` (no). Physical stimulus presence is different: hit/miss mean stimulation; fa/cr mean catch. Treat labels as evaluation outcomes only. For confidence, use the separate 0–1 rating.
4. Primary baseline: physical presence/intensity, subject-independent trial/history covariates, and a calibrated intercept. Test whether pre-report EEG adds predictive information *above* this baseline.
5. Candidates: full-channel spectral/time-domain features, joint PCA-4 and PCA-8 features, random-4 projection, and train-only within-stimulus/performance-stratum shuffled EEG. Compare a fixed regularized classifier for detection and ridge regression for confidence; avoid matching model capacity unfairly.
6. Cross-validation **groups by participant**, with any normalization, PCA, feature selection, imputation, artifact model trained only on training subjects where relevant. Tune hyperparameters in nested grouped development folds. Participant, not trial, is the uncertainty-analysis unit; report participant-level losses with paired bootstrap/descriptive intervals.
7. Negative controls: label permutation only in training participants, post-report leakage check, stimulus-only baseline, behavior-history baseline, and performance on catch/near-threshold trials separately. Predeclare how missing reports, nonfinite signals, bad channels, and partially recorded participants are excluded.
8. Do not commit person-level predictions or raw EEG to the public GitHub repo. Report only aggregate quality-control and evaluation metrics with dataset provenance and environmental checksums.

## Hypothesis falsifiers and scientific context

- If full EEG features or stimulus/history baselines predict held-out detection and confidence as well as or better than compact representations, the narrow *compression advantage* is unsupported.
- A compact representation predictive of detection/confidence is NOT an additional spatial dimension, proof of perceptual unity, or a quantitative degree of consciousness.
- The original paper already connects EEG evidence accumulation with detection and confidence. Merely replicating its qualitative result is not a new discovery. We must demonstrate a new, controlled methodological angle and request outside statistical/neuroscience review before claiming novelty.
- This is a post-hoc dataset chosen after inspecting Study 10 simulations, so all current/preliminary analyses are **exploratory only**. Register an independent study prospectively before confirmatory evaluation.

## Reproduce metadata audit (small textual files only)

```bash
cd studies/neural_detection11b
python -m unittest -v test_audit_events.py
python audit_events.py --output event_audit_aggregate.json
```

The audit writes **only aggregate statistics**, not trial-level confidential data. No EEG or individual ratings are saved.

## First independently reproduced aggregate quality checks

The GitHub workflow has verified the pinned public event-data audit: **18** subject records, **8,690** task starts, **8,662** uniquely paired first-order outcomes, **8,689** confidence entries, and **8,662** trials with both outcome and valid confidence. There are **28** ambiguous or missing outcome labels and **one** missing confidence rating. The source also contains **61** nonstandard threshold-event markers. In the conservative prospective **0.5-second** stimulus-relative EEG-window feasibility check, only **7,211** trials pass, with **1,479** excluded from that hypothetical window (including invalid labels or windows too near a response marker).

**Important:** `7,211` is **not** the number of verified extractable EEG epochs. It is a metadata-only screening statistic based on a *provisional* stimulus timing formula. The real physical onset must be confirmed using the recorded vibrotactile actuator channel, and the report timing interpretation must be checked against original task code. The data source contains trial outcome markers separate from confidence markers, and the meaning/timing of non-task `stim-thr` markers must be clarified. No hypothesis about neural prediction or graded consciousness has been tested.

[Public aggregate audit](event_audit_aggregate.json) — contains no participant-level predictions or raw EEG.
