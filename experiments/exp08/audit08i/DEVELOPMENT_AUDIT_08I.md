# Experiment 08I — Nonlinear sensory feedback and transfer to untried commands

**Status: EXPLORATORY DEVELOPMENT ONLY. Not preregistered, independently implemented by an outside investigator, peer reviewed, or evidence of consciousness.**

## Question

Can a label-free online predictor of the *sensory consequences of its actions* generalize after unannounced changes in a simulated 2D system whose observations are nonlinear landmark distances? Does explicitly engineered nonlinear regression outperform simpler memory-based prediction? Do repeated actions impede predicting outcomes of untried actions?

Prior work (08G/08H) used mostly linear displacement observations and hand-provided causal decomposition. This 08I simulator instead exposes **four noisy distances to landmarks**; the predictor receives no true position, landmark coordinates, physical motion equations, motor rotation, intervention time, change type, or cause labels. Predictions are logged **before** the action's consequence is observed. A noisy inertial channel reports the last executed physical displacement **only after the action**, but the primary endpoint is **range-only squared prediction error**. In this implementation, range and inertial outputs are fit by independent linear heads, so the inertial channel does not actually help the range predictions; a missing-inertial-channel experiment is *not* an effective multimodal ablation. This is an important design limitation.

**This is a fresh, nonlinear software task written by the same investigator, not an externally authored and independently audited environment.** The models are prewritten algorithms with investigator-chosen features; there is no evolutionary search or self-model invention in 08I.

## World and observations

- Two-dimensional hidden position and a randomized initial rotation of five possible commands: right, left, up, down, or no action.
- State-dependent motor gain and weak background nonlinearity; noisy landmark distance observations derived from square-root geometry (four fixed beacons whose coordinates are visible only to the simulator).
- An unknown change occurs at a randomly selected step 70–79 in changed worlds. Six types are evaluated: none, motor rotation, external drift, visual-range bias, motor+external, and an unmodeled nonlinear command-dependent fault. These types are **evaluator labels only**, not candidate categories offered to models.
- 150 commanded steps per episode; before-change error scored at steps 30–64, first aftermath at 80–98, late aftermath at 115–149. A single five-action counterfactual probe is performed at step 120 *in cloned copies of the world*, without changing the actual policy or updating the model from hypothetical outcomes.
- At each real step, an experimenter-specified random action policy chooses the next command. The model sees the command and its last observable ranges, then predicts the **next sensory change**. The real outcome becomes a training example only *after* the prediction is scored. No active probing policy is learned in this study.

### Label-free predictor classes

1. **Zero:** predict no sensory movement (intentionally weak).
2. **Linear action RLS:** recursive least squares with intercept and two command components.
3. **Nonlinear action RLS:** recursive least squares with 15 hand-built features that interact current observed landmark ranges with command components.
4. **Action-blind RLS:** 15 features derived from range observations, no access to motor command within its predictor features (diagnostic rather than fully equivalent baseline).
5. **Adaptive nonlinear RLS:** identical nonlinear features plus hand-selected error-dependent forgetting. Its detector threshold is chosen by the investigator, not learned.
6. **kNN all-history:** nonparametric matching of previous examples with the same action and nearest observed range states (seven-nearest weighting).
7. **kNN recent-history:** same, restricted to the previous 40 experienced actions, with no explicit physical dynamics.

All receive the same observed range stream and training outcomes and are scored on **identical physical trajectories** within each seed/cause/policy trial. But these are **not computation-, memory-, parameter-, or tuning-effort matched** comparisons: kNN stores past observations; RLS uses compact parameter matrices. The environment's motor and landmark nonlinearities and model vocabularies were designed by the same researcher.

## Development-only design and statistical unit

- Main random-action development evaluation: 48 seeded simulation worlds × six scenarios, with matched prechange noise and physics across the six scenarios for a given seed. These **48 base seeds** are the independent clusters; neither timesteps nor six within-seed scenarios should be treated as independent replicates.
- Restricted-action stress: 24 of the same seed IDs, action always `right`.
- High-noise stress: 24 of the same seed IDs, range/inertial noise standard deviation changed from 0.025 to 0.13.
- The first six and twelve main seed worlds were used in *development pilots*, and models were amended by adding stronger kNN controls before the 48-seed run. Thus **none of these estimates is confirmatory or held-out**, regardless of bootstrap intervals.
- Descriptive 95% percentile bootstrap intervals resample **base seeds**, average the five changed-world causes within each seed, and use 4,000 replicates. Hyperparameters and many earlier experiments were investigator-chosen; these intervals do not account for model selection or task design.

## Main development results

Late-phase mean squared error on **landmark-range changes** (lower is better):

| Cause | Linear RLS | Nonlinear RLS | kNN recent | Adaptive nonlinear | Action-blind |
|---|---:|---:|---:|---:|---:|
| No change | 0.00685 | **0.00250** | 0.00300 | 0.00250 | 0.04926 |
| Motor remapping | 0.02710 | 0.01080 | **0.00331** | 0.00845 | 0.05332 |
| External drift | 0.02772 | 0.01096 | **0.00928** | 0.01080 | 0.03257 |
| Sensor shift | 0.00688 | **0.00256** | 0.00300 | 0.00255 | 0.04915 |
| Motor + external | 0.02839 | 0.01304 | **0.00967** | 0.01208 | 0.03033 |
| Unknown nonlinear fault | 0.01436 | 0.00770 | **0.00562** | 0.00771 | 0.05014 |

The comparison averaged over the five **changed** conditions:

- Nonlinear minus linear late MSE: **−0.011878**, seed-bootstrap interval **[−0.012886, −0.010891]**, 48/48 seed averages favor nonlinear.
- Nonlinear minus **kNN recent** late MSE: **+0.002838**, seed-bootstrap interval **[+0.002247, +0.003516]**, 48/48 favor kNN recent. This is a **negative** result for the claim that our proposed engineered nonlinear regressor is generally best.
- Adaptive nonlinear minus fixed nonlinear: **−0.000695**, interval **[−0.001096, −0.000391]**, but it uses a designed threshold and no calibrated change attribution.
- The evaluator-only counterfactual transfer (five possible actions, at time 120) favored kNN recent over nonlinear by **0.002818** MSE units on average, interval **[0.001982, 0.003681]** when reporting nonlinear minus kNN.

## Stress tests and limitations

**High noise (24 overlapping seeds, noise SD 0.13):** the ranking reverses. Nonlinear minus kNN recent late MSE is **−0.001902**, seed-bootstrap interval **[−0.003214, −0.000475]**. The engineered nonlinear model now does better, showing that the model comparison depends on noise. Adaptive nonlinear minus fixed nonlinear is **−0.000391** with interval **[−0.001382, +0.000450]**; the apparent adaptive gain is uncertain even within this development simulator. Surprise alarms are frequent under higher noise, including the unchanged worlds. The detector is not validated for causal attribution.

**Repeated-action exposure (24 overlapping seeds):** when every training action is identical, counterfactual prediction error after motor remapping is about **0.049** for nonlinear regression and kNN, versus **0.003** for the kNN predictor trained with varied random actions in the main sample. This stresses a lack of identification under a restricted command policy. The repeated-action model is evaluated on five commands, most of which it has *never tried*. These task-specific numbers are not evidence of general self-discovery.

**No calibrated causal classification:** model scoring measures **predicting future sensory consequences**, not a discovered partition into “self,” “external,” and “sensor.” A model can forecast well without knowing why. Even intervention/counterfactual transfer in this artificial world does not imply phenomenology or true causal understanding.

**Additional caution:** a model can use recorded motor commands without exercising meaningful autonomous control. A nonlinear mapping of sensory changes is not necessarily an internal self-model. No biological/real-robot validation, outside replication, independent audit, computation matching, or preregistration has occurred.

## Reproduction

Requires Python 3.11+ and `numpy==2.3.5`. Run from the 08I folder (use `OPENBLAS_NUM_THREADS=1` for stable performance):

```bash
python -m unittest -v test_experiment08i.py
python experiment08i.py --seeds 48 --out /tmp/exp08i-main
python experiment08i.py --seeds 24 --policy repeat --out /tmp/exp08i-repeat
python experiment08i.py --seeds 24 --noise .13 --out /tmp/exp08i-noise
python export_per_world.py --directory /tmp/exp08i-main
python export_per_world.py --directory /tmp/exp08i-repeat
python export_per_world.py --directory /tmp/exp08i-noise
python check_reproduction.py --reference . --candidate-main /tmp/exp08i-main --candidate-repeat /tmp/exp08i-repeat --candidate-noise /tmp/exp08i-noise
```

Version-controlled seed-level outcomes are in `development/`, `restricted_actions/` and `high_noise/`, with summary JSON, per-world mean prediction errors, and alarm counts. The full downloadable research ZIP additionally preserves every individual scored prediction; regenerating those event logs from source is the canonical way to analyze different outcomes. A SHA-256 manifest covers all research-file versions.

## Required next step (not yet done)

An **external researcher** should first audit identifiability and task design. Then evaluate a **compute- and memory-matched** online learned representation versus a strong Bayesian nonlinear dynamics filter and model-based controllers, possibly with out-of-distribution interventions chosen *before* final protocol freezing. An agent would have to autonomously choose interventions and improve outcomes, not just passively predict the next sensory effect. An independent timestamped preregistration and untouched confirmatory seeds are required before claiming a confirmatory result. No new theory of consciousness has been established.
