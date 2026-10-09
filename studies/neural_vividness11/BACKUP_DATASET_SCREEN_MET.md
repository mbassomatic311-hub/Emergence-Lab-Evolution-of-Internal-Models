# Study 11 fallback dataset screen — MET music-induced emotion EEG (ds008701)

**Date:** 9 October 2026. **Status: source-metadata feasibility audit only; no EEG signal samples were downloaded, joined to ratings, analyzed, or claimed to predict experience. This is NOT a completed empirical study.**

## Why screen another dataset
The poetry dataset ds006648 has 212 text onset markers and 210 ratings in every one of 47 participants, with no EEG event-level stimulus identity. The article reports participant-specific randomized block/trial order, and authoritative event↔poem mapping is still needed. See [Issue 13](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models/issues/13).

An alternative should have an **explicit record identifier shared by both recording and subjective report**, not a guessed trial order.

## Candidate: MET (Music-Induced EEG Dataset)
- Source: [OpenNeuro ds008701](https://openneuro.org/datasets/ds008701), publicly accessible GitHub [OpenNeuroDatasets/ds008701](https://github.com/OpenNeuroDatasets/ds008701), checked at commit `ca831e5bbc08e79a90733f08acd69c3dd70b0895` (2026-09-29).
- Published README says each `ses-tNN` is one song `tNN`, that subjective ratings follow the song and that music playback lasts 120 seconds (with pre/post buffers).
- The actual root `ratings.tsv` has **400** unique (`participant_id`, `song_id`) pairs from **20** participants and columns Valence, Arousal, Likeability, Familiarity and Song Category.
- Actual GitHub tree has **399** `*_eeg.set` recording files, with corresponding (`sub-XX`, `ses-tNN`) paths. **399 of the 400 rating keys match a recording path.** The missing EEG recording is **`sub-17/ses-t17`**; the corresponding behavioral rating must NOT be included in any paired analysis. No recording path lacked a rating.
- The README's BrainVision `.eeg/.vhdr/.vmrk` file list does not match the observed `.set` files; format and actual annex content must be checked rather than assuming the README sample code works.
- Example `_events.tsv` has event segments marked `bad`, not a stimulus timestamp or explicit rating timestamp. A *whole-session* recorded-song pairing may be viable without event-level matching, but **EEG validity, actual playback interval and artifacts require independent verification**.

## Narrow potential exploratory study
Could a low-dimensional representation learned **within training participants only** from their pre-rating music-listening EEG predict session-level **self-reported emotional valence/arousal** in held-out participants, beyond a song-ID and song-category-only baseline, and better than full-dimension feature models at a matched training budget?

This asks about neural correlates of **reported emotional responses**, **not** multidimensional subjective consciousness, integration of separate senses, or extra dimensions of spacetime. It is a different endpoint from poetry imagery vividness, so it must not be silently substituted for the original Study 11 question.

## Gates before running any human EEG inference
1. Verify 399 matched `*.set` files are accessible as actual bytes and the timing of music vs pre/post response, with a small pilot subject sample, without publishing individual EEG or ratings.
2. Confirm the missing sub-17/t17 recording and all other mismatched/invalid sessions, and predeclare exclusions and artifacts.
3. Cross-check the author-specified `ses-tNN` ↔ `song_id` mapping in a second independent source, or inspect a source task log; identifier agreement is encouraging but not full epoch alignment.
4. Predefine absolute power / spectral-connectivity summaries from EEG computed without using test labels, frequency bands and epoch durations, guarding against high dimensionality and motion artifacts.
5. Fit every scaler/PCA/regressor on training subjects only. Use grouped leave-subject-out validation. Compare subject-level model errors and disclose different numbers of valid sessions per subject.
6. Use an appropriate song-specific control: same song IDs repeat across subjects. Report whether EEG adds predictive value beyond song identity; also control for session order and missingness.
7. Refrain from inferential claims about consciousness. Confirmatory analysis would require advance timestamped protocol and independent methodological review.

**Current assessment:** Potentially feasible alternative with a better explicit key, but **not yet a validated EEG–rating study**. The poetry alignment blocker remains unsolved and must not be bypassed by guesswork.
