# Experiment 08 — Development report (exploratory, negative pilot)

## Question and status

Can artificial evolution find effective policy architectures using action history in a noisy 2D environment with hidden motor rotation and unseen intervention? This exploratory pilot does **not** ask or answer whether artificial agents are conscious. This was NOT preregistered, independently audited, or peer reviewed.

### Method

The 2D world is a 13 × 13 bounded grid with randomly situated static obstacles, an initially unknown actuator rotation (0/90/180/270 degrees), action slips, environmental gusts, and relocatable food targets. Each episode lasts at most 48 steps and agents lose energy when moving or colliding, restoring energy on reaching food. Inputs are noisy relative food bearing, neighboring blockers, energy, prior-action flags, prior food/collision events and sensor-availability flag. No privileged motor rotation is provided to controllers. Transfer evaluations rotate the hidden actuator mapping by 180 degrees halfway through an episode, and optionally remove the bearing signal on 12% of observations. The reversal is absent in training.

The evolving-network genotype contains weights plus an initially empty mask of recurrent edges between five predefined hidden nodes. Heritable mutations vary weights and add/remove mask edges. Populations of 18 were evaluated for 14 generations under fitness-weighted parent selection, or uniform parent selection (random-selection control). The feedforward control disables recurrence. Agent survival and food collection, not reported subjective experience, are measured. Three development seeds (1103, 1205, 1411); 12 evaluations per controller per seed per environment. Training uses an engineering fitness proxy of food + 0.3 × episode survival; a separate **post-hoc development-only** diagnostic added 0.25 × reduction in goal distance in simulator state. Hyperparameters were not tuned systematically.

## Results: sparse-reward development pilot

Mean **food rewards per 48-step episode**, averaged across three independently seeded evolution populations with 12 evaluation episodes/population (or 36 seeded baseline episodes). **Descriptive means only; no inferential significance claim.**

| Controller | Stable | Reversal + 12% dropout |
|---|---:|---:|
| Evolved recurrent | 0.0278 | 0.0000 |
| Evolved feedforward | 0.0000 | 0.0556 |
| Random-selection network | 0.1111 | 0.1111 |
| Random motor command | 0.1111 | 0.1111 |
| Greedy, no motor-model | 1.0833 | 0.6389 |
| One-step hand-coded estimator | 4.1667 | 3.0556 |
| Bayesian four-rotation filter (added post hoc) | 3.5833 | 3.4167 |

The original unmodified pilot is preserved. The later `development_with_bayes/` repeat gave identical outcomes for the originally assessed controllers, with the Bayesian baseline added after inspecting the first pilot.

### Shaped-selection development diagnostic

We tried a second pilot with a fitness signal measuring net goal-distance improvement, which is unavailable to the agent and biologically unrealistic as a selection criterion. It still did not produce successful evolved policies. Recurrent controller mean was 0.0556 food in both stable and shift+dropout development tests; comparator remained at 4.1667 and 3.0556 respectively. The signal, architecture, budget and test conditions were investigated post-hoc, so this is troubleshooting, not a confirmatory null result.

### Sensor reliability diagnostic

Under severe sensor corruption (35% bearing dropout, elevated observation noise, stronger gusts and slips), one-step and Bayesian hand-coded estimators each declined from roughly 3.06/3.42 to 0.61 food per episode. These are **post-hoc descriptive development tests**, not proof of causal identification, generalization, or consciousness. See `development_diagnostics/sensor_stress_pilot.csv`.

## What we can and cannot conclude

- **Supported within this development pilot:** engineered model-based estimators outperform the random-initialized evolved networks on these tasks. The neural structure and evolutionary search need redesign or better training feedback; no evidence of successful self-model emergence was obtained.
- **Unsupported:** that recurrent architectures intrinsically fail, that this outcome generalizes to other environments or compute budgets, or that a particular circuit produces conscious subjective experience.
- **Prior design bias:** actuator rotations, sensor access, energy costs, representations, mutations, and target placements were specified. The Bayesian and one-step controllers encode strong domain knowledge. Comparison is not compute-matched.
- **Confounding:** the recurrent control and feedforward model are not strictly parameter-count matched because the dormant recurrent parameters still exist in the genome. Mutation budget, prior initialization, and fitness precision might explain failure.
- **Replicability:** deterministic tests pass locally, but separate scientist reproduction, multi-version numerical checks, and peer review remain necessary.
- **Statistical limitation:** 3 evolutionary seeds; episodes nested within population. No credible confidence interval about an underlying population of evolving environments is warranted.
- **Procedural integrity:** All initial pilot data preserved, subsequent tuning labeled exploratory, and no designated confirmatory seeds examined.

## Gate before a registered confirmatory Experiment 08

1. Make a separate implementation by another person, or have an expert independently audit the world dynamics and leakage risk.
2. Design two materially different environments (1D and 2D is not enough unless transfer claims and comparisons are appropriate); validate reset mechanics and sensor distributions.
3. Tune topological evolution and controller learning on explicitly declared development seeds only; use matched compute, sensor access, and information budgets for Bayesian, one-step, history-rich nonrecurrent, and recurrent methods.
4. Investigate fitness sparsity through a documented parametric study before any frozen protocol; do not redesign the primary hypothesis after viewing confirmatory data.
5. Freeze all environments, parameters, seed-generation methods, the primary contrast, minimum effect of interest, statistical unit, power/sample-size rationale, stopping rule, exclusion rule and multiplicity policy.
6. Publish an independently timestamped registration before generating or evaluating confirmatory episodes; retain raw failed runs and all software versions.
7. Invite external critical review. Rejection of the proposed hypothesis must remain an acceptable research outcome.

**This is authentic exploratory computational work and a negative development result. It is not yet a scientific discovery.**
