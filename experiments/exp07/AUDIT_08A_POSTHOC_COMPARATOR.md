# Experiment 07 — Audit 08A: Simple comparator benchmark (post-hoc)

**Status: EXPLORATORY, POST-HOC. Not registered, peer reviewed, or independently replicated. No consciousness inference is possible.**

## Why run this?
Experiment 07 showed evolved recurrent controllers outperforming a reactive controller on a task with an initially hidden action-to-motion sign and an unexpected polarity reversal. But the recurrent architecture and action-history feature were designed into the system. The earlier comparison did not include an obvious hand-engineered alternative: estimate the sign of the action-to-motion relationship using the change in noisy target bearing after the previous motor command.

The benchmark code is [audit08a_independent_baseline.py](audit08a_independent_baseline.py), with [tests](test_audit08a_independent_baseline.py) and [all seed-level results](audit08a_benchmark_per_seed.csv). It uses the same stochastic world mechanics, population-independent evaluation size (768 episodes per seed), and 32 seeds as the original study, but implements the simulator independently.

## Algorithm
- Set initial estimated actuator sign to +1, an uninformed guess with 50% accuracy.
- After a movement, compute `effect = -6 * (bearing_now - bearing_previous) * previous_action`.
- If the effect magnitude exceeds 0.25, update the estimated sign to its sign.
- Move toward the currently observed target bearing, corrected by the estimated actuator sign.
- When food respawns at a new location, avoid treating the relocation as a consequence of the immediately previous motor command.

**This is a hand-designed one-step comparator. It was not evolved, trained, or discovered by artificial selection.** The choice of threshold and feedback architecture is a designed inductive bias. It has a favorable advantage in this simple task and is NOT a proof of general artificial intelligence.

## Results (32 seeded simulation worlds)
Mean food collected per 40-step held-out actuator reversal episode:

| Model | Mean rewards |
|---|---:|
| Hand-designed comparator, post-hoc | **7.854940** |
| Original evolved recurrent controllers | **5.072347** |
| Original evolved reactive controllers | 2.034017 |
| Hand-designed naive controller | 2.056112 |

- Seed-paired **evolved minus comparator**: **−2.782593** (95% percentile seed-bootstrap interval **[−3.658964, −1.939598]**).
- Comparator outperformed evolved recurrent controllers in **32 of 32 seeded comparisons**.
- Seed-paired **comparator minus naive**: **5.798828** (95% percentile seed-bootstrap interval **[5.776408, 5.820475]**).
- Comparator survived all 40 steps on average in the evaluated simulation, while the naive controller did not.
- These bootstrap intervals measure variability among seeds **within this designed simulator**, not real-world uncertainty.

### Independent dynamics check
We compared the naive controller implemented in the independent benchmark against the frozen Experiment 07 engine, using the exact same seed, number of trials, random generator sequence, and action rule. Food and survival mean values were **exactly equal for all 6 combinations** (three seeds × stable/reversal). The check is formalized in [test_audit08a_parity.py](test_audit08a_parity.py).

The comparator versus evolved network comparison is **not trajectory-paired**: the controllers' actions change subsequent target relocations, so trajectory-level common random events are no longer identical. Seed-paired intervals are descriptive, not an exact counterfactual on identical trajectories.

## Interpretation
A cheap, interpretable estimator outperforms a neural controller on a task deliberately favorable to action-conditioned inference. This **weakens** any proposed novelty claim for Experiment 07 and suggests that part of its apparent sophistication is actually a simple binary-state estimation problem. It does not refute the finding that selection optimized the provided recurrent parameters. It also does not establish a subjective self or any level of phenomenal experience.

## How to reproduce

From `experiments/exp07/` with the root repository's dependencies installed:

```bash
python -m unittest -v test_audit08a_independent_baseline.py test_audit08a_parity.py
python audit08a_independent_baseline.py --previous-csv primary/results_per_seed.csv --out .
```

This writes `benchmark_per_seed.csv` and `benchmark_summary.json`. Compare with version-controlled `audit08a_benchmark_per_seed.csv`. Do not overwrite the frozen original `primary/` data. The audit is explicitly post-hoc and should always be identified as such in presentations or submissions.

## Related foundations
- Imamizu (2010): https://doi.org/10.1111/j.1468-5884.2010.00428.x
- Shadmehr, Smith, and Krakauer (2010): https://doi.org/10.1146/annurev-neuro-060909-153135
- Bongard, Zykov, and Lipson (2006): https://doi.org/10.1126/science.1133687

**Publication assessment:** archive as a transparent negative/qualification finding, not as a discovery of consciousness or a new type of self-model.
