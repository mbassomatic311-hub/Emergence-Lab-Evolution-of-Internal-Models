# Study 09 — From Exploratory Simulations to a Testable Research Program

**Not an experiment or finding.** This directory is a **prospective methods and scientific-integrity package**, developed after inspecting Exploratory Experiments 01–08J. No new sensorimotor experiments or confirmatory runs are reported here.

- [`PROTOCOL_DRAFT.md`](PROTOCOL_DRAFT.md): narrow hypothesis, independent domains, structural assumptions, strong benchmarks, non-identifiability controls, three evidence pillars, explicitly defined failure conditions, and registration gates.
- [`PRIOR_ART_AND_NOVELTY.md`](PRIOR_ART_AND_NOVELTY.md): sources showing why action-conditioned self-modeling and identifiability are not discoveries new to this project.
- [`EXTERNAL_REVIEW_PACKET.md`](EXTERNAL_REVIEW_PACKET.md): concrete outside-review request with questions and an **unsent** outreach template.
- [`study_plan.json`](study_plan.json): machine-readable list of mandatory baselines, ablations, and presently unresolved research gates. No confirmatory seeds exist in this plan.
- [`preflight.py`](preflight.py), [`test_preflight.py`](test_preflight.py): standard-library research-governance tests to catch obvious protocol/information-leakage/pseudoreplication mistakes before beginning.

## How to check

```bash
python -m unittest -v test_preflight.py
python preflight.py --draft-check
python preflight.py --confirmatory-check   # expected EXIT 2: blocked
```

The final command **must not pass** until legitimate scientific review and independent preregistration occur; even then the research owner must authorize any confirmatory dataset generation. The script is a simple procedural guardrail, not a substitute for human method review or any external registration system.

## Current stage

The methods draft and software checks are complete. An independently implemented environment, budget-matched baselines, sample-size pilot/power study, outside reviewer sign-off, frozen analysis code and externally timestamped preregistration are **not complete**. The proper next step is independent methodological feedback, not another internally tuned result or a claim of consciousness.
