# Study 11 — First empirical neural-data test (preflight, development only)

**Status:** code and dataset metadata preflight; **no human EEG or human vividness response data have yet been downloaded or analyzed**. Unit tests are synthetic fixtures only. **No claim about subjective consciousness.**

## Dataset selected

[OpenNeuro ds006648 v1.0.0](https://doi.org/10.18112/openneuro.ds006648.v1.0.0): 47 humans read 210 short texts and gave 1–7 ratings including vivid imagery. The dataset shares 64-channel EEG and trial-level ratings. It is not an audiovisual fusion task, and only tests a limited proxy for richness of subjective imagery (not consciousness, information integration or extra dimensions). Reference: Chaudhuri & Bhattacharya, *An EEG Dataset on Aesthetic and Creative Judgments of Brief Structured Poetry*, Scientific Data (2025), https://pmc.ncbi.nlm.nih.gov/articles/PMC12675506/.

## Hypothesis (prospective for dataset, exploratory because selected post Study 10)

A compact EEG representation (PCA-4 or PCA-8 fit on training participants only) could predict **reported vividness** on held-out participants with less error than full EEG, **conditional on the stimulus identity**. Hypothesis fails if full EEG or stimulus-only predictions are just as good or better. This would be a result about predictive signals correlated with reported imagery—not a consciousness scale.

## Design

- **Input:** externally constructed, manually verified table with `subject_id,trial_id,stimulus_id,vividness_rating,eeg_*`, plus independently completed JSON alignment audit. No speculative BIDS trigger interpretation in our code.
- **Validation:** 5-fold `GroupKFold` leaving all trials for any test participant out of training. Stimulus one-hot baselines are fit on training participants. All normalization, PCA, random projection and ridge regression are fit on training participants only.
- **Models:** stimulus-only, stimulus+full EEG, stimulus+PCA-4, stimulus+PCA-8, stimulus+random 4D projection, stimulus+PCA-4 trained with shuffled EEG within stimulus. All use same Ridge alpha 30; alpha remains an explicit exploratory engineering choice. Stronger future work needs nested group-wise tuning.
- **Evaluation:** descriptive per-subject MSE and MAE; paired subject bootstrap for model differences. No trial-level p-values. No claim of statistical significance due to post-hoc dataset/model selection.
- **Safeguards:** The code refuses unverified event-to-stimulus or rating-to-stimulus joins. EEG epoch must precede report/ratings. No real EEG/behavioral records may be publicly pushed; reports should be aggregated without identifiable records.

See [DATA_ALIGNMENT_GATE.md](DATA_ALIGNMENT_GATE.md) for compulsory steps before real data analysis. Unit tests are a software check only, not a scientific result.

## Run tests

```bash
pip install -r requirements.txt
python -m unittest -v test_evaluate.py
```

Run the evaluation **only after verifying data alignment and EEG epochs**:

```bash
python evaluate.py --input path/to/verified_join.csv --manifest path/to/audit.json --out results_private
```

## Data access

The raw EEG corpus is about 45 GB. Use partial NEMAR downloads or DataLad; do not download all 47 participants just to validate the schema. The public GitHub mirror contains annex **pointers** for some files, not data bytes. Source access guide: https://www.nemar.org/dataset/on006648. The official file catalog is https://data.nemar.org/on006648/v1.0.0/manifest.json; use it to resolve the actual versioned data bytes.

## Reviewer needs

An EEG/BIDS specialist must first check behavioral stimulus-epoch correspondence, EEG window selection and any participant-specific exclusions. A neuroscientist should review whether the hypothesis meaningfully tests perception as opposed to aesthetic responses or linguistic difficulty. If the trial-alignment key cannot be verified, **do not run Study 11**; move to a dataset with documented event-wise reports instead.
