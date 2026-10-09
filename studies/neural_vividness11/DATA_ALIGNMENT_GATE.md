# Dataset alignment audit — mandatory prior to examining human outcomes

Dataset: [Poetry Assessment EEG Dataset 1, ds006648 v1.0.0](https://doi.org/10.18112/openneuro.ds006648.v1.0.0), 47 subjects, 210 stimuli per participant, 64-channel EEG and 1–7 subjective ratings for vivid imagery plus other responses. Copyright/license: CC0 on NEMAR. Authors Soma Chaudhuri and Joydeep Bhattacharya. Source review: https://www.nemar.org/dataset/on006648 and the dataset's paper https://pmc.ncbi.nlm.nih.gov/articles/PMC12675506/.

**Verified from public repository metadata:** `participants.tsv` maps anonymized IDs to original participant codes. `sub-001/eeg/sub-001_task-readpoetry_events.tsv` contains columns `onset,duration,sample,value`, NOT literal stimulus identity, vividness or response column. `derivatives/Behavioural_Ratings/P101.csv` in the public GitHub clone is a **git-annex pointer** (200 bytes), not the behavioral data itself. Most EEG files likewise require fetching annex content. DO NOT fabricate results from these pointers.

**STOP: before constructing an analysis table, verify all of these independently:**

1. Download a minimal subset of actual `.set` EEG and the corresponding real `P101.csv` file through OpenNeuro/Datalad or the NEMAR manifest. Record versions, checksums and origin URLs. Do not upload human-level recordings or respondent-level ratings to public GitHub; only aggregate metrics and analysis code.
2. Inspect real behavioral file **columns** and the study's event/trigger coding documents. Confirm mapping of anonymized participants to original P codes and stimulus ids, the order of trials, aborted repeats and missing trials. NEVER assume row order is enough to align.
3. Verify the selected EEG epoch window (e.g. stimulus-onset to end-of-reading) **precedes** the button response or rating and contains no response-related time samples. Identify which trigger code genuinely denotes stimulus onset from the dataset documentation; do not guess 65281 or 65282.
4. Check filtering and artifact-removal methods. Fit normalization, dimensionality reduction, regression and any feature selection **only inside training folds**. If preprocessing uses cross-participant statistical estimates, refit inside folds. Independent per-recording artifact correction without using ratings is acceptable if disclosed.
5. Ensure each joined CSV row has unique `(subject_id,trial_id)`, one `stimulus_id`, one numeric `vividness_rating` in [1,7], and EEG features with `eeg_` prefix. No missing values without a published exclusion table. Keep all other subjective ratings and diagnosis fields out of input predictors.
6. Produce a JSON audit manifest with truthful keys `source_doi`, `events_to_stimuli_alignment_verified`, `rating_to_stimuli_alignment_verified`, `eeg_precedes_rating_response`, `preprocessing_train_test_safe`, and `auditor_note`. Never assert verified flags unless checked from actual data by a human or independent process.
7. Extract **only** descriptive features from pre-report EEG. The machine-learning script compares participant-held-out stimulus-only, full EEG plus stimulus, PCA-4/8 compressed EEG plus stimulus, random-4 projection, and shuffled-brain control using the same ridge hyperparameter. It never infers trial correspondence.

## Analysis limitations

- This is **not an audiovisual integration task**. Language is visually presented; subjects rate vivid imagery evoked by poetry. It tests a narrower proposition: whether low-dimensional EEG activity relates to reported *vividness of imagery*. It cannot directly test whether conscious experience is compressed or unified, and certainly not physics' extra dimensions.
- Each test subject has many correlated trials, and multiple subjects see the same stimuli. Participant (not trial) is the inferential unit. Evaluate raw and stimulus-matched models; the stimulus-only baseline is essential for avoiding attribution of text-driven rating differences to neural activity.
- This pilot is exploratory, since the dataset and hypotheses were selected after Study 10 synthetic results. Independent preregistration and untouched external data are prerequisites for a confirmatory effect.
- A negative, null or contradictory result should be reported; results cannot prove presence or absence of consciousness.

## Local execution after **real** data alignment

```bash
pip install -r requirements.txt
python -m unittest -v test_evaluate.py
python evaluate.py --input /path/to/verified_join.csv --manifest /path/to/audit.json --out /tmp/study11_actual
```

Never commit the real `verified_join.csv` or participant-level predictions to a public repository.
