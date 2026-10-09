# Study 11 — EEG event alignment audit (exploratory metadata only)

**No EEG recordings or behavioral ratings were joined or analyzed. No neuroscience or consciousness outcome has been measured.**

## Published trigger semantics
The ds006648 `task-readpoetry_events.json` dictionary specifies `65281` as fixation, `65282` as text presentation, `65283` as contemplation, `65284` as rating screen, and `65285`–`65288` as resting-state delimiters. In the published protocol the reading and contemplation periods are each about five seconds. This supports **a candidate pre-rating EEG epoch**, not a subjectively measured outcome.

## Why we stopped the join
Initial independent public-file inspection of participants 001–008 revealed **212** text presentation markers and one leading rating marker, despite **210 rated texts** per behavioral file. The real P101 behavioral schema has columns `PoemName, PoemType, Block, AA, Imagery, Moved, Originality, Creativity`, but no presentation timestamp or trial index. The event markers do not identify a particular poem. We must not assume the two additional event sequences are practice trials, nor shift rows to force an apparent match. The full 47-participant public event-structure audit is generated into `event_structure/summary.json` by GitHub Actions.

## Read-only procedure
Run `python -m unittest -v test_audit_event_counts.py` and `python audit_event_counts.py --out event_structure`. The audit reads the 47 public event files and `participants.tsv` from immutable OpenNeuroDatasets/ds006648 commit `b7e80bf9d225e8a5be06ee8358b7484972464edd`. It counts marker codes, identifies unexpected ordering and reading/contemplation timing errors, and reports participant-level event counts. It never downloads raw EEG or individual behavioral responses.

## Remaining requirement (STOP)
Before running `evaluate.py`, obtain an authoritative participant-level key identifying the extra event sequences, determining behavioral row presentation order, and matching each `PoemName` and block to an actual 65282 event. Cross-check at least the first, last, and block-boundary trials in multiple participants. An independent EEG/BIDS reviewer must verify extraction and pre-report window selection.

Do not generate the evaluator's required `events_to_stimuli_alignment_verified: true` or `rating_to_stimuli_alignment_verified: true` without this evidence. The 47-participant event audit **cannot** establish it.

This research is about predicting reports of imagery vividness, **not a direct measure of conscious experience**, and remains unregistered development work.
