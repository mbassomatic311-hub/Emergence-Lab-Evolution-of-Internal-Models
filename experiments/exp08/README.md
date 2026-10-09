# Experiment 08 — 2D sensorimotor transfer (development-only)

**Status: exploratory engineering and development pilots. No confirmatory experiment has been run or preregistered. No evidence of consciousness.**

## Research question

Can evolutionary search produce action-conditioned internal state mechanisms that transfer to unseen motor-mapping reversals and partial sensor loss **better than elementary hand-coded model-based controllers**?

This is a deliberately harder continuation of earlier experiments. Prior Experiment 07 used a one-dimensional reversible actuator. A post-hoc simple estimator surpassed the evolved network. Here the actuator has four possible motor rotations, obstacles, stochastic slips and environmental gusts. Food location is noisy and occasionally unavailable. After the midpoint of a held-out *development* episode, the motor mapping rotates by 180 degrees; under the combined shift test, the food bearing is sometimes absent.

**Important:** The same investigator wrote both implementations; they are NOT independently reviewed implementations, even though the 2D world was written separately from the 1D engine.

## Agents and mechanism

The simulated agent observes noisy relative target bearing, local blockers in four environmental directions, energy, previous action (one-hot), previous reward/collision and current sensor availability. Agents do **not** observe their exact coordinates, hidden actuator mapping, or reversal schedule. The initial recurrent graph has zero active edges; structural mutations can add or remove recurrent edges between five pre-designed neural units. Dense feedforward input/output connectivity, action space, selection algorithm, reward mechanics and the possibility of recurrence are still designed by the programmer. This is **not de novo emergence of a mind**.

Compare against random movement, uncalibrated greedy movement, a hand-coded one-step motor estimator, a four-hypothesis Bayesian motor estimator, feedforward evolved networks, and random-fitness selection. Bayesian parameters were introduced after inspecting the initial dev pilot; report all runs as exploratory.

## How to reproduce

Install `numpy` (tested on Python 3.11+). Run from `experiments/exp08/`:

```bash
python -m unittest -v test_exp08.py
python engine.py --seeds 3 --generations 14 --population 18 --eval-n 12 --selection-signal sparse --out reproduction_sparse
python engine.py --seeds 3 --generations 14 --population 18 --eval-n 12 --selection-signal shaped --out reproduction_shaped
python diagnostics.py
```

The raw initial pilot is archived in `development_initial_immutable/` and the initial progress-shaped pilot in `development_shaped_initial_immutable/`. A later repeat with a Bayesian benchmark is in `development_with_bayes/`; the Bayesian controller was not assessed in the first pilot.

## Scientific caution

This deliberately modest developmental search budget (3 seeded populations per condition; 14 generations; 18 agents; 12 evaluation episodes per seed) is too small for confirmatory effect estimates. The evolving networks did not become competitive. Environmental and architecture choices strongly influence outcomes, and we have not established external validity or methodological novelty. The progress-shaped selection pilot uses a **privileged simulator distance statistic** in evolutionary fitness; it is an engineering diagnostic, not a plausible model of natural selection.

The file `DEVELOPMENT_REPORT.md` gives unrounded values, an honest methods audit, and a path toward external preregistration. **No held-out confirmatory seeds have been generated or evaluated.**
