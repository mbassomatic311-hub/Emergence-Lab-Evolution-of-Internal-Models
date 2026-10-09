# Experiment 08 — Development audit 08B: Fitness noise, common initial worlds, and privileged reference

**Status: exploratory post-hoc methods audit; not preregistered, confirmatory, peer reviewed, independently audited, or evidence of consciousness.** Original negative results in `development_with_bayes/` and `development_shaped/` remain unchanged. All runs here reuse the 3 declared development population seeds `1103`, `1205`, `1411`. Do not use these as independent confirmation.

## Audit questions

1. **Training fairness.** `engine.py::train_population` scores genome *i* on a different world seed (`seed + g*2213 + i*13`). With noisy, sparsely rewarded episodes, initial-world luck affects which genomes reproduce. Can scores on shared initial world-seed schedules help?
2. **Fitness informativeness.** How well do scores from two initial development episodes rank the same 18 fresh random controllers when checked over 16 separate development episodes?
3. **Task solvability.** Can a fully informed controller reliably obtain food in this world, and does the observation channel directly reveal the hidden motor rotation or absolute position?

## Methods

- `audit_fitness_noise.py`: 18 independently initialized genotypes for each of 3 population seeds. Assess original candidate-specific and common initial seed schedules with **two** lifetime simulations per genome. Separately evaluate each genome with **16** new development lifetimes. Compute within-seed Spearman rank correlations and fraction of 2-episode scores with zero food (using the food+0.3*survival proxy; no food implies fitness ≤ 0.3).
- Rerun **recurrent-only** evolutionary search using the same population size (18), 14 generations and 2 fitness episodes per candidate as the original development pilot, but share initial training seeds *across candidate genomes* each generation and share fresh development selection seeds. Test champions on the same 12 development episodes per seed, in stable and shift+12%-sensor-dropout conditions. Caution: policies can cause diverging trajectories and RNG draw sequences; this is **not identical realized noise** across agents.
- `audit_world_controls.py`: privileged pathfinding reference uses hidden actual rotation, full obstacle grid, agent coordinates, exact target, and **advance knowledge of reversal timing**. It cannot serve as an information-matched model baseline or empirical upper bound. Its purpose is to indicate rough world solvability. Re-evaluate greedy, comparator, and Bayesian baselines on identical development world seed identifiers for reference.
- `test_audit_world_controls.py`: causal tests check hidden actuator rotation has no *direct* effect on the current observation, that two interior locations with identical local observations yield identical sensor values, that dropout removes bearing, that targets spawn in valid cells, and that the oracle is repeatable.

## Results: developmental diagnostics only

Across 54 sampled fresh genomes (3 seeds × 18):

| Population seed | Original short-score zero-food share | Spearman, original 2 vs independent 16 episodes | Spearman, common worlds 2 vs independent 16 episodes |
|---|---:|---:|---:|
| 1103 | 83.3% | 0.482 | 0.562 |
| 1205 | 83.3% | 0.747 | 0.548 |
| 1411 | 83.3% | 0.330 | 0.049 |

Average Spearman rank correlation across these three small groups: original 0.520; common-world 0.386. The common-world variant **did not** consistently improve rank correspondence with the longer evaluation. The two-episode scores remain noisy and contain many ties/near-ties. These are diagnostics, not robust population-level statistical estimates.

| Controller/training condition | Stable food | Shift + sensor dropout food |
|---|---:|---:|
| Original evolved recurrent (prior 3-seed pilot) | 0.0278 | 0.0000 |
| **Common-initial-world evolved recurrent (new audit)** | 0.1389 | 0.1111 |
| Ordinary hand-coded comparator (not evolved) | 4.1667 | 3.0556 |
| Ordinary hand-coded Bayesian estimator (not evolved) | 3.5833 | 3.4167 |
| **Privileged map-and-rotation pathfinder (diagnostic only)** | 7.4444 | 7.4444 |

These are descriptive means of 12 fresh episode evaluations from each of 3 development seed worlds. The small improved evolved means may reflect stochastic variation and the corrected training seed scheme; **no causal improvement or scientific novelty has been established**. The pathfinder's superiority is largely due to privileged access to simulator state and a specified search algorithm; it cannot be fairly ranked against sensor-limited agents.

## Methodological interpretation

A core flaw in the initial pilot is not simply that recurrent networks are poor: evolutionary selection often cannot reliably distinguish controllers after only two very sparsely rewarding episodes. Using common initial world seeds alone is inadequate; much stronger sampling, complexity-matched learning baselines, and independent algorithmic implementations are needed. A 5-node, untrained recurrent network with mostly random direct input-to-action weights may lack an optimization path to beneficial action-conditioned behavior under the tiny evolutionary budget. The present audit does **not** establish that the controller family could never succeed with sufficient compute or suitable training.

**Further limitation:** The experiment's observation contains an explicit previous-command one-hot vector, energy, last food/collision outcome, nearby obstacle flags, and noisy relative goal vector. The evolved agents were *provided* this input design. They did not discover perception, embodiment, a self-model architecture, or consciousness.

## Reproduction

With `numpy` installed, from `experiments/exp08/`:

```bash
python -m unittest -v test_audit_fitness_noise.py test_audit_world_controls.py
python audit_fitness_noise.py --out /tmp/exp08-audit-fitness --seeds 3 --population 18 --generations 14 --eval-n 12 --high-eval 16
python audit_world_controls.py --out /tmp/exp08-audit-world --eval-n 12
```

Compare the generated `summary.json` and `reference_summary.json` against version-controlled data in `development_fitness_audit/` and `development_world_audit/`. Retain the original `development_with_bayes/` pilot data unchanged. CI should check those summaries with strict numerical tolerances.

## Decision and next work

- Keep this audit exploratory; do not merge PR #2 or launch a confirmatory experiment as if these numbers were preregistered.
- Build and test a genuinely information-matched policy class with explicit history and training-budget accounting; compare against a trained recurrent controller as well as Bayesian and comparator baselines.
- Increase development sample sizes to estimate selection noise and statistical power, without reusing future frozen confirmatory seeds.
- Identify and correct any modeling artifacts under independent review, and consult the published literature before claiming new methods.
- Freeze and **externally** timestamp a complete prospective protocol *before* generating untouched confirmatory results. Ethical scientific interpretation remains focused on **sensorimotor computation**, not subjective consciousness.

## Relevant literature

- Tang, Jin, Yao & Zhou, *On the Effectiveness of Sampling for Evolutionary Optimization in Noisy Environments*, Evolutionary Computation (2018): DOI `10.1162/evco_a_00201`.
- Nelson, Barlow & Doitsidis, *Fitness functions in evolutionary robotics: A survey and analysis*, Robotics and Autonomous Systems (2009): DOI `10.1016/j.robot.2008.09.009`.
- Lehman & Stanley, *Abandoning Objectives: Evolution through the Search for Novelty Alone*, Evolutionary Computation (2011): DOI `10.1162/EVCO_a_00025`.
