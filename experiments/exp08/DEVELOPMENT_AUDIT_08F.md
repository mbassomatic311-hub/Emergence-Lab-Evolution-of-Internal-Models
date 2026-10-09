# Experiment 08F — Adaptive forgetting under unexpected action–outcome change

**Research classification: iterative EXPLORATORY DEVELOPMENT ONLY. NOT publicly preregistered; not peer-reviewed; no evidence of phenomenal consciousness, self-awareness, or autonomous invention of an architecture.**

## Question

Can an explicitly engineered online learner use **unexpected discrepancies between its motor commands and sensory consequences** to decide when its stored action-outcome predictions have become unreliable? Does resetting or rapidly revising memory improve subsequent sensory prediction or navigation when motor dynamics change abruptly, relative to fixed-memory and memoryless controls?

This question is distinct from whether something *experiences* the discrepancy. No subjective-experience instrument exists here.

## Design

The existing Experiment 08 13×13 grid world contains obstacles, motor slips, occasional exogenous gusts, targets, resource collection, and noisy, partially visible target-relative bearing. The world selects one of four unobserved motor command rotations. In **changed** worlds the mapping reverses at world step 24; **unchanged** worlds have stable mapping. Both include **12% observation dropout**. The agent sees the bearing, its own prior actions, and observable flags for food respawns/collisions/visibility; it does **not** see actual displacement, hidden rotation, objective map coordinates, a change indicator, or the change schedule.

All learning controllers start with **four zero-valued 2D action-effect vectors**. After a valid action→observation transition, they compare their prediction (issued *before* the observed consequence) with the observed difference in the same target-relative bearing. Scored transitions exclude observable target respawns, collisions, and invisible target bearings. The action-outcome representation and transition filter are **hand-engineered**. The model's own time counter is used only to log possible alarms, not to trigger them.

In *open-loop* tests, a separately seeded uniformly random action generator drives each physical world identically across the five models. Therefore the action history and sensory consequences match between predictor arms; any prediction difference arises from the model. The world—not each dependent step—is the sampling unit. The trial remains synthetic and task-specific.

### Five predictive models

1. **Slow constant gain:** each action estimate updated with exponential moving average learning rate 0.25.
2. **Fast constant gain:** otherwise identical, rate 0.75.
3. **Adaptive gain:** rate 0.85 when a familiar action has squared prediction error above 2.25, otherwise 0.25.
4. **Surprise-triggered reset:** rate 0.25 except reset all estimates when two *consecutive valid* experienced prediction errors exceed 2.25 after at least eight previous valid updates and one previous sample of the relevant action. Reset is based on surprise, not the true change flag.
5. **Memoryless:** predicts zero movement effect for every command and never accumulates memory (a deliberately weak diagnostic).

The learning rates, squared-error threshold, two-consecutive alarm rule, sensory representation, and exploration policy were investigator-chosen *after* prior 08E observations. They are not learned or evolved, and should not be sold as new algorithms.

### Protocol and seeds

Six fresh **development-only** namespaces (31–36 million), 24 seeds each = **144 distinct simulated worlds**. Each world is separately evaluated in changed and unchanged settings across all five models. A separate closed-loop test uses seeds offset by +10,000,003 for each corresponding world, evaluating food and survival for all five plus hand-designed Bayesian, geometric-comparator, and greedy controllers. Episodes last up to 48 steps, shorter if energy runs out. World generation and action RNG are explicitly seeded. The exploratory pilot first examined 3 seeds per namespace, then all 24; thus no confirmatory/preregistered inference is claimed.

### Outcomes (descriptive; no claims beyond this simulator)

**Open-loop squared sensory prediction error, averaged first within each world and then over worlds. Lower is better.**

| Controller | Before reversal | First 8 steps after reversal | Later after reversal |
|---|---:|---:|---:|
| Slow constant gain | 0.723 | 2.114 | 1.162 |
| Fast constant gain | **0.672** | 2.363 | **0.881** |
| Adaptive gain | 0.737 | **1.860** | **0.872** |
| Surprise-triggered reset | 0.724 | 1.892 | 0.934 |
| Memoryless | 1.123 | **1.138** | 1.152 |

The repeated bolding denotes *descriptively relatively low* error in different periods; it does not denote a preregistered winner. Note the nonintuitive result: no memory remains much less affected immediately after reversal, while rapid learning of new outcomes helps later. Some worlds have no valid observations in a phase due to dropout/collisions and are omitted for that phase; sample sizes are published per phase in `development_change08f/summary.json`.

**Surprise-triggered detection:** in the changed setting 83/144 worlds triggered at least once; 82 of those had a post-reversal alarm (one also or only alarmed earlier). There were 82 total post-change alarms and 1 pre-change alarm. Median time of a post-change alarm was **3 observation steps after the reversal**, among worlds where an alarm occurred. In unchanged worlds, 3/144 raised an alarm. Descriptive detection sensitivity for a post-change alarm is **82/144 (56.9%)**, and the observed stable-world false-alarm rate is **3/144 (2.1%)**. Thus this particular threshold detector *misses many actual reversals*, even though its false-alarm rate is low. Some trials may lack enough valid sensory observations to detect a change. Detection refers only to behavioral prediction-error patterns in this modeled task.

**Closed-loop food rewards per world (changed condition, 144 worlds):**

| Controller | Mean rewards |
|---|---:|
| Slow constant gain | 0.743 |
| Fast constant gain | 0.743 |
| Adaptive gain | 0.806 |
| Surprise-triggered reset | **0.944** |
| Memoryless | 0.181 |
| Greedy | 0.535 |
| Geometric comparator | 2.653 |
| Bayesian four-state estimator | **2.986** |

The difference between surprise-reset and slow EMA navigation is +0.201 foods per world, exploratory world-paired 95% percentile bootstrap interval [+0.111, +0.306]. Note **127/144 paired worlds were ties**, 17 favored reset, and none favored slow EMA; this is a small effect from a sparse outcome, not evidence of general optimality. Surprise-reset remains **2.042 food rewards behind** the Bayesian estimator on average, bootstrap interval [−2.389, −1.701]. Multiple comparisons, development tuning, and task specificity preclude inferential or publication claims.

## Why this matters and why it does *not* establish consciousness

The results provide a computational example of a feedback mechanism that can register surprising action consequences and sometimes revise an outdated internal mapping. It is **not an agent identifying its own conscious self**, and it does not reliably distinguish *internal actuator changes* from *external gusts, slips, environmental movement, or bad sensor data*. A gust can produce the same action–observation mismatch as a changed motor system. Differentiating internal versus external causes would require additional identifiable cues or independently varying interventions; the present evidence is insufficient.

The strong Bayesian benchmark was explicitly supplied with the **four-rotation physical hypothesis**, whereas the learned action vectors are initialized blank; these controllers are not compute-, structure-, or prior-matched. Their navigation actions necessarily alter subsequent trajectories, so only the open-loop prediction arms are physically trajectory-matched. All confidence intervals describe Monte Carlo variation under this constructed model; they are not estimates of consciousness, real-world evolutionary uncertainty, or independent external replication.

**Research result:** simple error-triggered forgetting can offer a modest within-task benefit when an online predictor encounters an abrupt regime shift, but frequent misses and large benchmark gaps demonstrate that this mechanism is limited.

## Reproduction

Python 3.11+, NumPy. From `experiments/exp08`:

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest -q test_audit08f_change.py
OPENBLAS_NUM_THREADS=1 python audit08f_change.py --per-group 24 --out /tmp/exp08f-reproduction
OPENBLAS_NUM_THREADS=1 python audit08f_analyze.py --data-dir /tmp/exp08f-reproduction
```

Compare `summary.json`, `alarm_per_world.csv`, `navigation_per_world.csv`, `prediction_events.csv`, and `exploratory_intervals.json` to published development outputs; raw event CSV has one row per *valid* observable action–consequence pair. The local full ZIP contains the entire event-level dataset; source plus seeded simulator regenerates it exactly. Do not overwrite any prior experiment.

## Next research gate

**Before confirmatory work:** add a genuinely independent environment where target-relative bearing is NOT an almost-direct displacement sensor, vary change types (sudden shift vs one-time gust vs moving landmark vs sensor corruption), compare observation-equivalent Bayesian change-point detectors and matched-cost trainable models, and obtain independent critique of identifiability. Externally preregister only *after* designs and development hyperparameters are frozen. Our work remains exploratory research, not a discovery about consciousness.
