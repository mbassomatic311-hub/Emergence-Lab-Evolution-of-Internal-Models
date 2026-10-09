# Experiment 08G — When is the cause of unexpected action feedback identifiable?

**Research status: EXPLORATORY DEVELOPMENT. Not preregistered, independently peer reviewed, an evolved architecture, or evidence of subjective consciousness.**

## Research question

Could a controller that observes only its own commands and noisy sensory effects distinguish three possible causes of an unexpected motion: a changed actuator, an external persistent drift, or a visual-sensor-only drift? If not, what interventions make cause identifiable?

This audit tests **structural identifiability and active observation** in a simplified, independently implemented 2D linear displacement task. It does **not** extend the previous navigation study into a fully independent naturalistic ecosystem, and the classifier has a hand-specified causal hypothesis vocabulary.

## Three counterfactual mechanisms

Let `u` be a 2D motor command, `R` a hidden 90-degree rotation and `u0` a particular cardinal command. Set `b = (R-I)u0`. The primary visual-flow sensor's observed motion increment `y` has Gaussian noise `epsilon`:

1. **Actuator cause:** `y = R u + epsilon`, reference sensor `z = R u + eta`.
2. **External drift:** `y = u + b + epsilon`, reference sensor `z = u + b + eta`.
3. **Visual drift:** `y = u + b + epsilon`, reference sensor `z = u + eta`.

The simulated **no-change** option `y = u + epsilon`, `z = u + eta` is included as a fourth *candidate hypothesis*, not a fourth cause within the balanced three-class primary evaluation. Noise arrays are shared across counterfactual worlds with the same seed. In all cases the model's inputs are only chosen commands and available sensor increments, never the true cause, world seed, true actuator orientation, wind, or known generative parameter. The controller does, however, receive a common cue that an attribution window has begun. Detecting change autonomously is **not tested**.

### Deliberately unidentifiable condition

If the controller issues `u = u0` repeatedly and has only the first sensor, all three mechanisms yield **exactly the same** `y = R u0 + epsilon`. Their conditional observation distributions are identical. An arbitrarily powerful learner cannot identify which cause generated such a record on that evidence alone. The exact counterfactual equality is verified in software tests, not merely inferred from aggregate accuracy.

With two sensors but no varied actions, actuator and external-drift causes remain observationally identical, although visual drift becomes distinguishable. With varied actions but one sensor, motor change becomes identifiable, but external and visual drift remain identical. **Varied actions plus an independent reference sensor** supply enough information to distinguish all three idealized alternatives under these assumptions.

## Observer and decision rule

The observer computes a Gaussian least-squares fit for a **handwritten candidate family**: two possible actuator rotations, eight possible wind vectors, eight possible visual offsets, and no-change. For each cause class, it takes the best-fitting candidate; it normalizes the four resulting class likelihood scores; and it returns a diagnosis only if its highest *relative-fit support* reaches 0.80, otherwise `undetermined`. This procedure does **not** provide a calibrated Bayesian posterior: optimizing nuisance parameters rather than integrating them distorts probabilities. A high relative-fit support is not proof that any candidate hypothesis is physically correct.

The active intervention follows a **pre-programmed**, cause-independent 12-step sequence that deliberately includes orthogonal/reversed movements and voluntary zero-command pauses. The passive condition repeats one identical command for 12 steps. The agent did not autonomously invent its probe schedule.

## Development observations

192 paired base seeds, three balanced causal classes, 12 measurements per class/condition, additive independent Gaussian noise `sigma = 0.18`. There are **576 case-trials** per sensor/action condition; the statistical unit is a base seed, not an individual measurement or one of its correlated cause-trials.

| Experiment condition | Correct diagnosis incl. abstentions | Fraction with confident diagnosis | What it identifies |
|---|---:|---:|---|
| Repeated action, primary sensor only | 0 / 576 = **0.0%** | 0.0% | No causes; all cases indistinguishable |
| Repeated action, two sensors | 192 / 576 = **33.3%** | 33.3% | Visual drift only |
| Active probe, primary sensor only | 192 / 576 = **33.3%** | 33.3% | Motor remapping only |
| Active probe, two sensors | 576 / 576 = **100%** | 100% | All three designed causes |

*Accuracy with abstention* is not forced-choice accuracy. Forced argmax accuracy under passive/one-sensor, passive/two-sensor, active/one-sensor, active/two-sensor equals 33.3%, 66.7%, 66.7%, 100%, respectively, but argmax picks arbitrary classes when the likelihoods tie. The meaningful result is the inferential **ambiguity** rather than the guaranteed high accuracy once the simulator gives the classifier the exact correct candidate mechanisms.

### Robustness audit (completed after the first developmental results)

Under *active probing with two sensors* (576 balanced trials per setting), when noise standard deviation rises to 1.0:

| Diagnostic samples | Confident correct attribution |
|---|---:|
| 4 | **68.4%** |
| 6 | **88.5%** |
| 12 | **99.0%** |

At noise sigma 0.5, 4 samples gave **99.5%**, and 6 or 12 gave 100%. At sigma 0.18, all these studied sample lengths yielded 100%. These are **in-model, post-hoc development tests**—the classifier is supplied the correct class families and evaluation noise level.

### Strong failure when assumptions are wrong

We introduced three additional diagnostic cases absent from the original three-class model: simultaneous actuator change **plus** external drift; external drift **plus** visual drift; and no change. Because we included an explicit no-change candidate, the unchanged case was identified in all 192 seeds.

In **both simultaneous-cause settings**, the classifier nevertheless made a confident single-cause assignment in **all 192 seeds per setting** despite the absence of the true combined hypothesis. A secondary, *post-hoc* absolute residual-MSE check (`MSE > 0.2`) flagged every such simulated combined-cause case; the threshold has **not** been validated or calibrated over realistic noise variation, and it must not be treated as a proven safe rejection mechanism. That rule would also reject much normal data when sensor noise is higher. The model can be confidently wrong if our hypothesis vocabulary is incomplete.

## What this does and does not infer

The exact observational equivalence is a property of the designed physics, not an empirical discovery about biological organisms. The high active/two-sensor attribution score is expected because the observer knows the exact causal families used to generate test observations. **No architecture, investigative action policy, or self-representation arose spontaneously; there is no evolutionary selection in this experiment.**

The useful conceptual result is a disciplined research constraint: **any claim that an agent identified an internal versus external cause must demonstrate that its observations *could* distinguish those causes, and show the relevant information interventions.** Prediction error or surprise alone is insufficient. There is no evidence here about phenomenal consciousness, self-awareness, or whether physical information-processing is sufficient for experience.

## Reproduction

From `experiments/exp08/` with NumPy and Python 3.11+:

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest -q test_audit08g_causal_attribution.py test_audit08g_stress.py
OPENBLAS_NUM_THREADS=1 python audit08g_causal_attribution.py --worlds 192 --out /tmp/causal08g
OPENBLAS_NUM_THREADS=1 python audit08g_stress.py --worlds 192 --out /tmp/causal08g
sha256sum /tmp/causal08g/{per_world.csv,summary.json,noise_sweep.csv,outside_model.csv,stress_summary.json}
```

Compare regenerated files byte-for-byte with the 5 datasets in `development_causal08g/`. Source/tests and data are preserved; no confirmatory samples have been generated.

## Most important next gate

Run a future independent task in which cause timing is **not cued**, the agent chooses experiments adaptively, combined causes can occur, model families must be learned rather than enumerated, and the 2D observations are generated from nontrivial sensor geometry rather than direct flow increments. Compare matched-compute and matched-sensor model-based baselines, hold out interventions, and preregister the final plan externally *before* generating confirmatory seeds. Scientific novelty and limitations require independent expert assessment.
