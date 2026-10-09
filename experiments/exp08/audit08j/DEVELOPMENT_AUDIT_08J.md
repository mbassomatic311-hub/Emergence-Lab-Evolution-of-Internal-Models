# Experiment 08J — Equal-budget uncertainty-based action selection, developmental audit

**Status:** EXPLORATORY DEVELOPMENT ONLY. Not preregistered, no external review, no evidence or assessment of consciousness, subjective awareness, or independently evolved cognitive structures. Pilot (6 seeds) was examined before the completed 24-seed runs. All intervals below are descriptive and post-hoc. Experiment 08J does not show that agents choose **when** to probe; it fixes probe times and allows them to choose **which** motor action to take.

## Question and falsifier

Can a controller whose model has no ground-truth motor or cause labels use its own parameter uncertainty to pick actions that improve later prediction of action effects? A meaningful finding would require it to beat a strong, equal-action-budget cyclic exploration policy, not just no-probe or random action controls. The possible falsifier is that a simple deterministic cycle generalizes as well or better. This also tests whether the effect persists for a different predictor family (nearest-neighbor memory).

## Methods and provenance

- Physical world: **exact existing Experiment 08I implementation**, not newly independent; hidden initial motor rotation, nonlinear displacement and four noisy landmark ranges, optional reference sensor, potential motor, external, sensor, combined, and unfamiliar nonlinear changes. Six investigator-chosen 908I scenarios: `none`, `motor`, `external`, `sensor`, `motor_external`, `unknown_nonlinear`.
- 150 action-observation steps per world. Each policy has **30 prescribed probing opportunities** (steps 0,5,...145) with a nonzero motor action in four directions, except no-probe. All other steps execute action zero. No intervention explicitly triggers at a change; world changes occur unannounced at a hidden random timestep ~70–79.
- Policy `uncertainty` selects action maximizing the nonlinear recursive-least-squares (RLS) model's **feature covariance** score `f(u)^T P f(u)` (ties randomized). This is a conventional designed approximate information-gain criterion, **not** a learned or evolved causal discovery algorithm. It uses only its current observed landmark distances and the model covariance. No true world state or cause labels are available.
- Fair same-budget alternatives: random action, fixed cycle of all four directions, least-used action, and repeat-one-command. A no-probe policy is an unequal-cost diagnostic. Ties and random action choices are repeatably seeded.
- All agents train the **same** nonlinear RLS predictor from observed range increments and inertial sensor increments. We additionally evaluate the KNN-recent predictor trained on each policy's exact same action trajectory to assess whether a policy effect survives a different modeling assumption.
- **Primary:** after training, score each model on five counterfactual commands at three **common evaluator-generated reference states** (times 110,125,140), using independent rollouts copied from a *single predefined* policy-independent 08I world trajectory for each seed/cause. Every policy gets exactly the same reference states and resulting outcomes. Those outcomes are never used to train policies. Training trajectories naturally differ among agents. Counterfactual average range MSE is lower-is-better.
- Note a limitation: the reference trajectory uses the same seed and physics parameters as the agent's world, but a different action history; it is a held-out **trajectory**, not a new independent physics world. The same fixed states are reused in the noise stress control.
- 24 independent development seed clusters, repeated across six causal settings and six policies (the unit for paired descriptive bootstrap contrasts is seed, not each step/trial). This is an opportunistic small study; development adjustments and repeated inspection preclude confirmatory statistical inference.

## Main low-noise results (observation noise sigma = .025)

24 world seeds × 6 physical conditions, fixed 30-probe budget. Both predictive models are **unlabeled** online learners, but the form of the four action channels and feature representation is pre-coded.

| Probe policy | RLS counterfactual range MSE | KNN counterfactual range MSE | Nonzero action probes |
|---|---:|---:|---:|
| uncertainty | 0.00777 | 0.00921 | 30 |
| random | 0.01443 | 0.01675 | 30 |
| cycle | 0.00770 | 0.00804 | 30 |
| least_seen | 0.00772 | 0.00800 | 30 |
| single_action | 0.05646 | 0.04525 | 30 |
| no_probes | 0.04753 | 0.04653 | 0 |

Active uncertainty minus deterministic cycle (RLS MSE): **+0.000073**, exploratory seed-bootstrap 95% interval [-0.000578, +0.000886], with active better in **12** / 24 and worse in **12** / 24 independent seed clusters. **No clear improvement over the simple cyclic control.**

Active minus random: -0.006655, exploratory interval [-0.010616,-0.003517]. The advantage is a weaker result than beating an informative systematic control. The alternative KNN learner favors the cyclic policy over uncertainty-based probing by +0.001174 MSE.

**Crucial measurement warning:** in-trajectory prequential errors for no-probe / repeat-one-command are deceptively small because they rarely leave familiar actions. The shared five-action counterfactual benchmark exposes this over-specialization. Therefore no-policy comparisons should be judged from in-trajectory prediction error alone.

## High-noise stress test (sigma = .13; 24 paired development seeds)

| Probe policy | RLS counterfactual range MSE | KNN counterfactual range MSE | Nonzero action probes |
|---|---:|---:|---:|
| uncertainty | 0.04899 | 0.04777 | 30 |
| random | 0.06565 | 0.05414 | 30 |
| cycle | 0.05217 | 0.04519 | 30 |
| least_seen | 0.05095 | 0.04730 | 30 |
| single_action | 0.18494 | 0.07469 | 30 |
| no_probes | 0.11794 | 0.07582 | 0 |

Active minus cycle on RLS: -0.003185; exploratory 95% seed-bootstrap interval [-0.009108,+0.001879]. Again, the interval contains zero. The alternative KNN predictor still scores better under cyclic exploration.

## Interpretation

Information-rich action sequences improve model identification versus collecting the same action repeatedly, *within this engineered environment*. In the observed simulations, maximizing the model's approximate uncertainty did not meaningfully outperform much simpler balanced or cyclic probing at the same probe cost. Indeed, the other predictor family benefits more from a fixed cycle. This is a substantive **negative** qualification to the hypothesis that more elaborate autonomous inference is inevitably better.

The agent does **not** autonomously discover the meaning of self, invent its feature representation, select probe timing, explicitly identify causes, evolve the policy, or demonstrate conscious experience. The strongest scientific conclusion is about properties of exploration schedules **under the provided dynamics and representation**; related ideas are established within active learning, system identification and dual control.

## Reproduction and further scientific gates

Run from `experiments/exp08/audit08j/` with NumPy 2.3.5 and sibling 08I implementation:

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest -v test_experiment08j.py
OPENBLAS_NUM_THREADS=1 python experiment08j.py --seeds 24 --noise .025 --out /tmp/exp08j-low
OPENBLAS_NUM_THREADS=1 python experiment08j.py --seeds 24 --noise .13 --out /tmp/exp08j-noise
python check_reproduction.py --reference development_main --candidate /tmp/exp08j-low
python check_reproduction.py --reference development_high_noise --candidate /tmp/exp08j-noise
```

Next scientifically worthwhile milestone: let policies decide **when** to probe under explicit intervention cost, learn features rather than receive them, include a genuinely independent nonlinear simulator, and preregister a final protocol before seeing confirmatory outcomes. Continue to compare simple analytical/planner baselines. Get external scientific review. Neither GitHub CI nor a DOI is external replication/peer review.
