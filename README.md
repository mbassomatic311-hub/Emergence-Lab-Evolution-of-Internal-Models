# Emergence Lab — Evolution of Internal Models

**Exploratory computational research on how artificial evolution can produce adaptive memory, sensing, and action–outcome processing.**

> **Scope and limitations:** This repository contains toy evolutionary simulations. It does **not** demonstrate machine consciousness, first-person experience, the origins of biological consciousness, or a new law of physics. Previous studies of recurrent processing, corollary discharge, biological evolution, artificial life, and robot self-models substantially predate this work. Results are specific to the designed simulators; independent scrutiny is welcome.

## Research question

How can basic evolutionary operators (variation, differential reproduction, and inheritance) favor information-processing mechanisms that help agents respond to danger, remember observations, sample additional information, and adapt when action outcomes change?

## Experiments

| Experiment | Core test | Material |
|---|---|---|
| 01 | Survival, resource gathering and inherited behavior | `experiments/exp01/` |
| 02 | Evolving weights for provided predictive memory | `experiments/exp02/` |
| 03 | Mutation of pre-specified memory connections | `experiments/exp03/` |
| 04 | Simplified perception versus more detailed, costly sensing | `experiments/exp04/` |
| 05 | Selection for optional measurements that disambiguate environmental states | `experiments/exp05/` |
| 06 | Evolution of action–outcome comparator connections and ablation controls | `experiments/exp06/` |
| 07 | Sensorimotor adaptation to unseen actuator reversal | `experiments/exp07/` |

Experiments 01–05 are exploratory demonstrations with interactive HTML and supporting engine, analysis and output files. Experiments 06–07 include more detailed study reports, protocols and reproducibility data. **None is publicly preregistered.** Read each experiment's limitations and protocol before describing any outcome.

## Reproducing results

Python 3.11+ recommended. For Study 06, use `experiments/exp06/README.md`; for Study 07, use `experiments/exp07/README.md`.

```sh
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd experiments/exp07
python -m unittest -q test_engine07.py
# To regenerate the 32-seed primary dataset, see this experiment's README.
```

For early browser-based demonstrations, open the `experiment_*.html` file in the matching folder's `code/` subdirectory. Some experiment-generation scripts expect their original working directory; those files are preserved for provenance and might need path adjustments before regenerating early artifacts from the reorganized structure.

## Scientific status & publication ethics

- **Exploratory, not peer reviewed.** This repo does not itself constitute a scientific publication or DOI.
- The earlier protocol freezes were **local**, not external preregistration.
- Model assumptions and useful controller mechanisms were designed; the simulations do not establish spontaneous emergence of consciousness.
- Read `docs/RESEARCH_STATUS.md` for claims supported and unsupported, and `docs/REPLICATION_PLAN.md` for a stricter future confirmatory design.
- Don't treat simulation episodes as independent biological observations. Analyze independently seeded populations as experimental units.
- Do not selectively discard failed seeds or edit outcomes without keeping originals and describing changes.

## Releases and archiving

Create a GitHub release only after verifying reproducibility and documenting the version. If desired, connect the repository to [Zenodo](https://zenodo.org/) to archive tagged releases and obtain a DOI. A DOI is not peer review. A future preregistration must be independently timestamped **before** any relevant confirmatory results are examined.

## Authorship and permissions

Repository prepared for the connected GitHub account `mbassomatic311-hub`. Authorship, license, release date, and external collaborators should be chosen by the repository owner. **No open-source license is granted by this package.** Add a license deliberately before inviting unrestricted reuse.
