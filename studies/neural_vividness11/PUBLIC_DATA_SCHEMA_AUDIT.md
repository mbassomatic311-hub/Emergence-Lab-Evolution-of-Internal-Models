# Study 11 public behavioral-data inspection — verified

**Status:** REAL PUBLIC BEHAVIORAL FILE INSPECTED; **NO human EEG downloaded or analyzed, no trial-to-EEG mapping verified, and no individual ratings stored in GitHub.** This file is a data-format validation, not a study finding.

## Provenance

Original: [OpenNeuro ds006648 v1.0.0](https://doi.org/10.18112/openneuro.ds006648.v1.0.0), NEMAR on006648 v1.0.0, freely reusable CC0.

Using the NEMAR published versioned manifest, we downloaded **one** real rating CSV privately inside an isolated GitHub runner and retained **only its schema**. On 2026-10-09, the automated inspection succeeded. [GitHub Actions run](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models/actions/runs/37938250078).

- File: `derivatives/Behavioural_Ratings/P101.csv`.
- Actual file size: **13,773 bytes** (unlike the GitHub git-annex *pointer* at the same path, which is not the CSV content).
- Encoding: **Windows-1252 (cp1252)**; the first schema-only inspection failed when mistakenly assuming UTF-8. The corrected check succeeded without changing any human ratings.
- Row count: **210**.
- Columns: `PoemName`, `PoemType`, `Block`, `AA`, `Imagery`, `Moved`, `Originality`, `Creativity`.
- Numeric ratings appear in `Imagery` and other rating columns; **actual rating values were not kept**.
- Full machine-readable, aggregate-only schema: [schema_check.json](schema_check.json).

## Mandatory next blocker

The EEG `sub-001_task-readpoetry_events.tsv` available via public metadata contains **`onset`, `duration`, `sample`, `value`**, without explicit `PoemName` or `Imagery`. Neither matching each CSV row to a specific EEG event nor interpreting the numeric trigger codes has yet been independently validated. We must:

1. Inspect experiment trigger-code documentation and the official order of poems within blocks.
2. Confirm the actual onset of poem processing versus response onset (exclude motor/report contamination).
3. Validate alignment on one participant; then test independently on others.
4. Retrieve a minimal real EEG subset through official NEMAR/OpenNeuro access, never a full 45GB clone just for the metadata check.
5. Consult an EEG/BIDS specialist before rating-level neural claims.

**STOP:** Do not assert a neural correlate of vivid imagery from this schema. The prediction benchmark in `evaluate.py` uses synthetic data in its tests and remains **unexecuted on human EEG**.
