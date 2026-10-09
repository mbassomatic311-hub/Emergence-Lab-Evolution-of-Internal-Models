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

## Source-pinned 47-participant audit — completed 9 October 2026

The [public 47-participant metadata audit](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models/actions/runs/37940166784) successfully ran and is archived as `event_structure/summary.json` and `event_structure/per_subject_event_counts.csv`. All **47/47** event streams contain **212** poem-onset codes (65282), versus **210** rated texts. Sequence and five-second event timing checks reported no detected errors. An extra leading rating-screen marker (65284) was present in **29/47** recordings and absent in **18/47**; the first eight recordings were not representative of that latter variation.

A separate [candidate seven-block pause audit](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models/actions/runs/37940643778) found longer gaps at positions compatible with two introductory presentations followed by seven sets of 30 texts (median candidate boundary gap **58.193 seconds**, median internal gap **25.597 seconds**). Its own summary explicitly reports `join_verified: false`: no code or source reliably identifies those first two trials as practice, excludes them, or maps the following EEG epochs to `PoemName`.

The [authors' published methods](https://doi.org/10.1038/s41597-025-06189-w) state that both the block order and within-block stimulus order were randomized **per participant**. Therefore generic block assignment spreadsheets and EEG timestamps cannot by themselves establish a per-subject poem-to-EEG join. The source has no event-level poem identity in `events.tsv`, and the behavioral file has no event timestamp/index. **Human EEG–vividness analysis remains STOPPED** pending authoritative presentation logs or author clarification and independent validation.

The paper lists Joydeep Bhattacharya (jbhattacharya@hkbu.edu.hk) as corresponding author. An inquiry has been drafted, **not sent**; author review is not yet underway.
