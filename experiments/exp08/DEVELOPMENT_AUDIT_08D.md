# Experiment 08D — Does motor-remapping learning need recurrence, more training data, or an action–effect inductive bias?

**Status: DEVELOPMENT-ONLY, post hoc exploratory computational methods investigation. Not preregistered, peer reviewed, or independently replicated. This does not measure consciousness.**

## Research aim and context
Experiments 08A–08C found that evolving generic recurrent networks performed poorly compared with hand-coded action–outcome estimators in a stochastic 2D world. Small neural networks also struggled to infer hidden actuator rotation even when trained on ground-truth rotation labels. Our next diagnostic asks which portion of that failure is explained by (a) extra training experience, (b) experiencing reversals during training, or (c) explicit structure mapping previous actions to sensory displacement.

This study deliberately supplies **privileged actuator labels in offline supervised training** (both for generic networks and the structured learner). This is a capacity/inductive-bias diagnostic, **not an evolved controller** and not a comparison with matched evolutionary data or training compute.

## Simulator and target semantics
Original 13×13 world from `world2d.py`: four unknown actuator rotations, slip, gusts, obstacles, noisy target bearings, collisions, energy, food and possible observation dropout. All deployments see only the ordinary 14-component observation, their action history and internally retained state. At step 24, a world configured for reversal rotates the motor mapping **inside** `World.step`, after `observe` has returned. Accordingly the hidden label in this 08D audit is **the actual rotation before this step**, not the next, initially unknowable motor rotation. Earlier 08C training code labeled the reversal boundary using the *upcoming* rotated state; this audit corrects that target-timing ambiguity and cannot be interpreted as a direct apples-to-apples score comparison with 08C.

All seeds are exploratory development seeds from the **14M–20M** namespaces; they do not overlap the prospective confirmatory pool (which has not been defined or opened). Each simulated world contributes a single trajectory, which is zero padded after death and ignored for accuracy computation. Episode-level results are not independent observations of biology. No test-set feedback is used to choose a controller for confirmatory inference; this is an openly exploratory pilot where code choices were informed by earlier results.

## Matched supervised-training conditions
Training totals are **episodes**, all using labels of the hidden rotation (privileged during training):

- **Stable-only (192)**: 192 stable-rotation worlds.
- **Stable matched-size (384)**: 384 independent stable-rotation worlds.
- **Mixed (384)**: 192 stable plus 192 worlds with an unannounced halfway actuator reversal and 12% bearing dropout.

For the two 384-episode conditions, the model classes, initial parameter seeds, number of optimization epochs (36), minibatch size (24), hidden units and evaluation data are held constant. Training uses Adam with clipped gradients. The 192-episode baseline has **half as much training data** and correspondingly fewer minibatch updates; do not attribute every observed difference to reversal exposure.

Generic models follow 08C: memoryless MLP (232 parameters); two-frame history MLP (235); tanh recurrent network (220). Three initializations per architecture/condition. The models predict the four possible hidden motor states from visible observations, not subjective awareness.

**Structured learner:** During training, fit a 4-state-by-4-command table of observed two-dimensional displacements using privileged rotation labels. Do not provide any exact geometric prototype prior (`regularize=0`). During deployment, infer the likely hidden actuator rotation by likelihood comparison of previous commanded movement versus observed target-bearing change, maintaining a four-state probabilistic belief across steps. The discrete state assumption, loss function, action/displacement feature, Bayesian update and memory are all deliberately designed, so this **does not constitute spontaneous discovery of an internal model**. Unlike the neural models, the structured learner is not parameter- or computation-matched. It is a mechanistic positive control.

## Development-only numerical results
Held-out **development shift+dropout** condition, 72 independent simulated world instances and 2,394 valid decision steps. Chance under uniform motor rotations is nominally 25%; empirical majority-state baseline is **29.57%** because trajectory survival and states are not balanced across valid decision steps.

| Method | 192 stable training episodes | 384 stable episodes | 192 stable + 192 shifted episodes |
|---|---:|---:|---:|
| Memoryless MLP, mean across 3 initializations | 40.41% | 45.43% | 46.67% |
| Two-frame history MLP, mean across 3 initializations | 38.32% | 41.73% | 44.61% |
| Recurrent tanh network, mean across 3 initializations | 34.85% | 40.11% | 46.95% |
| Structured action-effect observer | **87.22%** | **87.05%** | **87.01%** |

**Structured stable-only learner ablations on identical recorded development traces:**
- Intact 4-state belief filter: **87.22%**.
- Retain only the immediately preceding action/observation evidence, reset the prior each step: **63.95%**.
- Scramble last-action one-hot signals between distinct trajectories at each timestep, leaving world observations fixed: **25.81%**.
- Accuracy in the first six timesteps after reversal (t=25…30): **80.88%**; later timesteps (t≥31): **91.27%**. Many test trajectories end before the end of the episode. The world rotates **during** the t=24 step and the immediate effect is not knowable in advance.

**Geometric prior sensitivity:** with no handcrafted movement prototype prior, accuracy was **87.22%**; weak regularization weight 4 yielded **87.18%**, and strong weight 100 yielded **87.09%**. However the four-state action-conditioned emission table and filtering algorithm remain engineered.

**Closed-loop navigation, 72 further development simulated worlds per condition, 48 action steps each, shifted/dropout condition:**
- Learned structured observer trained on stable-only data: **3.125** food/episode.
- Analytical Bayesian hand-coded controller: **3.403** food/episode.
- Analytical comparator: **2.736** food/episode.
All policies face the same **starting seed IDs**, but actions change subsequent world trajectories. Scores are descriptive development data, and no significance or novelty claim is made. The learned observer is not superior to the Bayesian baseline here.

## What can and cannot be inferred
The shift-trained recurrent classifier improves from 40.11% (equal-size stable training) to 46.95% with changed dynamics, but remains far inferior to a **hand-structured** inference architecture. Three random initializations and one world family are insufficient for general inferences about representation learning. Importantly, no recurrent architectural selection is involved in 08D, and the classifier uses a privileged label unavailable to evolutionary selection in the original model. The central demonstrated mechanism—remembering actions and comparing their predicted sensory consequences—is already well established in control theory, robotics and neuroscience (efference copy, corollary discharge, Bayesian filtering).

The study therefore supports a **diagnostic explanation**: the observation histories are informative, but small generic models under this training regimen do not efficiently recover the needed action-conditioned latent state. It does **not** show any emergence of consciousness, intrinsic neural limitations, a new sensorimotor theory, or anything that could warrant a priority claim in neuroscience.

## Limitations / audit checklist
1. The structured observer incorporates extensive human inductive bias and is privileged-label trained. Comparing its accuracy directly with the generic neural models is *not* a compute-, expressivity- or data-efficiency-matched algorithm comparison.
2. The 72 development episodes share one designed simulation family; this is not independent replication or out-of-family generalization. The steps within episodes are autocorrelated; **2,394 is not the number of independent trials**.
3. Reversal and dropout configurations, filter hazard and likelihood forms are known from the simulator design. No attempt was made to prove robustness over hyperparameters, sensor distortion, other tasks or transfer to nature.
4. The action-history-scrambled comparison is a retrospective data-level perturbation, not a causal intervention physically rerun in a fresh world. It shows sensitivity to the action copy, not a proof of self-awareness.
5. 08D training examples are chosen based on prior negative experiments. This is *explicitly post-hoc development*, not a preregistered test.
6. The baseline labels are supervised privileged latent states. Real biological evolution does not receive such labels; no inference about ecological evolution follows.
7. Reversal labels at the imminent step are not knowable from the current observation. This audit uses the pre-step rotation label, which is better grounded but must be distinguished from the actual **future** action-to-movement mapping at the instant of reversal.
8. Model-selection/architectural search and hyperparameter optimization are not exhaustively standardized; no new scientific novelty claim is justified.

## Reproduce
From `experiments/exp08/` with NumPy installed:

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest -v test_exp08.py test_audit_fitness_noise.py test_audit_world_controls.py test_audit08c_learning.py test_audit08d_learning.py
OPENBLAS_NUM_THREADS=1 python audit08d_learning.py --stable-train 192 --shift-train 192 --test 72 --val 48 --epochs 36 --policy 72 --out /tmp/exp08d-reproduction
```

Compare `/tmp/exp08d-reproduction/summary.json`, `model_comparisons.csv`, and `policy_episode_results.csv` to the versioned `development_learning08d/` outputs. The JSON stores all per-initialization outcomes, model parameters, world seed ranges, and individual food rewards. Note that the training/validation and test **trajectories** are deterministically generated from the published source and are not hand-edited. The tests check no lifetime stitching, world-state labeling, no future information use, prototype correctness, action-signal ablation, and robustness of the input/output shapes.

## Next step (not executed)
Seek **independent expertise** to build a genuinely new ecological environment, equate resources/observations across learned and analytic policies, and investigate latent-state estimation without privileged labels (e.g. self-supervised sensory prediction and error-driven online adaptation). Pre-register the final confirmatory study with a third-party timestamp **before** the first untouched confirmatory outcome is generated. This requires independent methodological review and should not be confused with releasing a GitHub archive.
