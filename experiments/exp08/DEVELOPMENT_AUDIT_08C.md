# Emergence Lab — Experiment 08C: Can a small network learn an observable motor model?

**Status: developmental exploratory computational audit, NOT a preregistered/confirmatory experiment. No implication of phenomenal consciousness, biological evolution, or autonomous discovery of a body model.** This audit uses **privileged hidden-state labels in offline supervised training**, deliberately unlike the natural-selection procedure in 08B. Do not compare its training efficiency against evolutionary search as if information or compute were matched.

## Scientific question and falsifiers

Earlier Experiment 08 pilots found topology-mutating recurrent controllers received sparse and noisy fitness signals and failed to become effective. Before attributing this solely to evolutionary search, we ask two separate questions:

1. **Identifiability:** Does the sensory/action history contain enough information to infer hidden actuator rotation on the 2D world, including unannounced reversal and sensory loss? A reference observer should fail when previous motor-command information is scrambled.
2. **Trainability of simple neural architectures:** Given labeled development trajectories, can matched-size (~220–235 parameter) memoryless, explicit two-frame history, and recurrent networks estimate hidden rotation and produce a useful policy? A positive result would establish the information is *learnable with supervised privileged training*, not that evolution discovers it.

The project **must report negative results** if the trained networks fail. A memory-dependent task does not by itself show general self-modeling or consciousness.

## Experimental design and data provenance

- Underlying world and observations are defined in `world2d.py` (13 × 13 grid, hidden four-way motor rotation, noise, collisions, wind, food/energy, unannounced reversal, 12% sensory dropout in shifted worlds). No changes to previously released environment or Experiment 08 main engine.
- All training labels are the true hidden actuator rotation for the action about to be executed; the supervised learner sees these **only during training and offline scoring**, never at rollout time. The invisible mid-episode reversal occurs inside `world.step`, and labeling correctly marks the changed actuator effect on that decision.
- Trace generation uses an exploration policy that is a 55% mixture of direct-target greedy moves and 45% uniformly random actions, neither knowing the true rotation. No network acts in the world during training. Training 192 development episodes (stable motor mapping), validation 48 different stable development episodes, and evaluation 72 additional stable plus 72 shifted-and-dropout development episodes.
- Earlier local implementation mistakenly restarted a dead agent as part of the same 48-step neural sequence. **This was detected and corrected before this version was finalized.** Sequences now terminate at simulated death, are zero-padded, and loss and metrics ignore padded steps. Do not reuse results from that flawed preliminary implementation.
- Three neural models receive the same 14 observation channels and supervised labels; the history feedforward model receives one previous observation explicitly, whereas the recurrent model must internally retain history. Model sizes: memoryless MLP 232 trainable scalars, two-frame MLP 235, recurrent tanh network 220. **Similar parameter counts do not guarantee equivalent inductive bias, information, effective capacity, or training quality.**
- Full-sequence cross-entropy training uses manually implemented backpropagation through time (for recurrent), Adam optimization, 36 epochs, batch size 24 episodes and learning rate 0.013. Training random seed 80808, additional independently initialized training seeds 80908 and 81008. Gradient calculations are covered by finite-difference unit tests.
- Policy-rollout diagnostic: classifier predicts rotation from sensors and its own memory only; a shared hand-coded greedy action rule then attempts food collection. These hybrid controllers are not purely learned or evolved policies. 36 development rollouts per world for primary single-initialization scores; the three-initialization sensitivity uses 24 rollouts per world per model/initialization. **Comparison with evolved controllers is neither training-budget nor supervision matched.**
- The additional Bayesian evidence reference was hand-designed using known action dynamics and the previous observation/command (not the hidden motor-state labels). It is evaluated on the exact same exploration traces. Scrambling the recorded previous-command one-hot vector while preserving the other features and true labels is an **offline information-ablation diagnostic**, not a physical intervention on the simulated world.
- All 08C world seeds are deterministic *development* offsets of the established 08A/08B development identifiers (1103,1205,1411). No confirmatory dataset is generated, opened, or analyzed.

## Results — observation identifiability

| Metric | Stable dev traces | Shift+dropout dev traces |
|---|---:|---:|
| Valid decisions, after masking death | 2,433 | 2,332 |
| Hand-designed four-state evidence observer accuracy | **91.90%** | **88.42%** |
| Same observer with previous-action flags permuted | 26.39% | 26.46% |
| Always choose majority label in these traces | 36.58% | 32.38% |

**Interpretation:** These observations do carry information about hidden motor dynamics, and a designed estimator can recover much of it. Destroying motor-command history degrades this estimator sharply. This is not proof the learned networks will discover the relationship or that the information is sufficient for any general form of self-awareness. Rotation labels can be imbalanced *conditional on survival* and exploration policy; the 25% uniform prior is not the right empirical reference after censoring.

## Results — three supervised training initializations

**Held-out developmental shift+dropout observation accuracy** (mean across three independently initialized training runs; reported range is across those three models, not a confidence interval):

| Neural class | Trainable weights | Mean accuracy | Across-start range | Mean food/48-step closed-loop episode | Food range |
|---|---:|---:|---:|---:|---:|
| No-history MLP | 232 | **35.81%** | 32.08–38.55% | 0.347 | 0.208–0.583 |
| Explicit one-frame history MLP | 235 | **36.91%** | 36.19–37.69% | 0.208 | 0.167–0.292 |
| Recurrent network | 220 | **34.06%** | 30.02–39.24% | 0.222 | 0.208–0.250 |

On the same 36 rollout seed worlds used for the primary single-initialization diagnostic, the **hand-designed comparator** collected 2.667 food after shift+dropout and the **hand-designed Bayesian** reference 2.889. These were not trained on hidden-state labels, so their advantage is particularly notable, but neither computational efficiency nor algorithmic complexity is matched to the neural variants.

**Accuracy is measured over valid decisions in the deterministic developmental sample, not over statistically independent individual decisions.** The sensitivity runs share data and worlds; their ranges reflect only three model initializations. No generalization or statistical-discovery claim is warranted.

## What the negative finding can and cannot mean

- **Supports:** Information about the actuator mapping is present in action-conditioned sensory history, as a clear deterministic proof of feasibility within this simulator.
- **Suggests:** The three small neural architectures and this limited supervised optimizer have poor generalization to a reversal that is absent from training; a hand-built state tracker has a strong inductive advantage here.
- **Does NOT support:** A proven inherent limitation of neural networks, of evolutionary algorithms broadly, or of the emergence of consciousness. The study has tiny, hand-designed model classes, sparse training, and no hyperparameter optimization.
- **Important confound:** The training data never include actuator reversals, whereas shifted-world evaluation includes them. Generalization failure is not surprising and should be tested systematically against training distributions with changes before drawing conclusions about representation learning.
- **Another confound:** Comparisons to 08B evolution, to hand-coded Bayesian observers, and to neural memory classes are not all compute-, training-information-, or hypothesis-class-matched. They answer different diagnostic questions.

## Reproduce

Python 3.11+ with NumPy 1.26+. From `experiments/exp08/`:

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest -v test_audit08c_learning.py
OPENBLAS_NUM_THREADS=1 python audit08c_learning.py --out /tmp/audit08c --train 192 --val 48 --test 72 --epochs 36 --rollout 36
OPENBLAS_NUM_THREADS=1 python audit08c_sensitivity.py --out /tmp/audit08c --epochs 36
```

Compare generated `summary.json` and `initialization_sensitivity.json` against the committed versions under `development_identifiability_08c/`. The trained primary weights are in the separately downloadable full 08C audit ZIP (`development_identifiability_08c/weights.json`); the lightweight GitHub import contains the deterministic training source, seeds, summary and sensitivity data, so these weights can be regenerated exactly. The weights have not been uploaded to GitHub. See GitHub Actions workflow for strict numeric reproduction checks. The original prior 08B reports and results remain intact.

## Decision gate

Do NOT label this as the prospective confirmatory experiment. Next steps: design a matched-information action-conditioned baseline training curriculum, a simpler sufficient-statistic network control, **at least two independent research groups** to examine the simulator and design, and a registered study with unused seed worlds. A scientific manuscript about *sensorimotor state estimation* would require both a meaningful novelty analysis against existing filter/state-space literature and robust independent replication; the data above alone do not clear that bar.
