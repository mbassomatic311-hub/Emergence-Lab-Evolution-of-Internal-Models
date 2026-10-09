# Experiment 08H — Uncued change, action selection and causal identifiability

**Research status:** EXPLORATORY DEVELOPMENT ONLY, run after inspecting earlier Experiments 08G/08F. Not preregistered, externally replicated, peer reviewed, or a discovery about consciousness.

## Scientific question

Can a computational observer, without a change cue or a hidden cause label, learn the action-dependent and action-independent components of its sensory consequences, and select informative probing commands? When does the evidence **fail to identify a cause**? This is an experiment about **structural identifiability in a hand-specified linear sensorimotor world**, not an experiment showing de-novo evolution of a self-model.

### Structural model (designed by researchers)

An agent issues one of five discrete commands: +x, -x, +y, -y, or 0. A separate physical displacement and two independent sensory measurements are generated:

`reference z_t = M_t u_t + d_t + eps_ref`, `primary y_t = M_t u_t + d_t + s_t + eps_primary`.

- `M_t`: unknown 2×2 motor mapping. It may change by a 90-degree rotation without a warning.
- `d_t`: external physical drift, independent of commanded action.
- `s_t`: drift in the primary sensory motion reading only; the reference sensor does not share this drift.
- `eps`: independent per-step zero-mean Gaussian noise with sigma 0.13 in the main developmental sample.
- A nonlinear movement anomaly can occur, deliberately outside the learner's additive-linear model family.

Each development world has a 22-step initial calibration period followed by 38 steps of actions; an uncued change, when applicable, occurs at a randomly chosen step 27–34. **The experiment does NOT model absolute positions, walls, biology, subjective experience, or an evolved network.** Its change setting is not exposed to the observer. Calibration and the fixed action vocabulary are generous engineered assumptions.

### Learning and intervention policies

The learner estimates a linear action–displacement mapping by least squares on calibration history. From then on it tests deviations between predicted and observed sensory consequences, accumulates recent surprises, and triggers an alarm when two of three recent errors exceed a fixed threshold. **No true cause label or oracle change timestamp is supplied.** After an alarm it fits an action-dependent matrix and independent constant offsets from recent observation history, but the *factorization* (action effect vs constant physical drift vs sensor disagreement) is human-designed. Attribution requires full-rank experimental data and a tolerable fit residual; otherwise it abstains. A model with zero prior change alarm answers 'no change', which can be wrong.

Four intervention policies were studied under the same world seeds and matched 60-step episode horizon:

- **Repeat**: continue the same command; deliberately observation-deficient control.
- **Random**: draw a random command uniformly each step.
- **Cycle**: use a predetermined balanced five-command cycle, an **important strong comparator**.
- **Adaptive**: repeat the default command until its own surprise detector alarms; then choose commands maximizing leverage under the observed regression-design matrix (a simple D-optimal experimental-design heuristic).

The adaptive policy is a **hand-designed algorithm**. 'Probe cost' counts commands not equal to the default command and is a **proxy action-diversion cost**, not actual energy or task reward. Thus the adaptive advantage on this metric partly follows by construction.

### Outcomes: main developmental run

96 paired base seeds × 7 cause scenarios × 4 action policies = **2,688 simulated case evaluations** (not 2,688 independent experiments). Five in-model changes are used for conditional attribution accuracy: motor change, external drift, primary sensor drift, motor+external, and external+sensor. An unchanged environment tests false alarms; a nonlinear perturbation tests model misspecification.

| Action policy | Exact five-cause attribution | Mean counterfactual displacement squared error | Mean nondefault commands (out of 38) | Unknown nonlinear correctly rejected |
|---|---:|---:|---:|---:|
| repeat | 0.0% | 0.9410 | 0.00 | 0.0% |
| random | 100.0% | 0.0041 | 30.46 | 93.8% |
| cycle | 100.0% | 0.0039 | 30.00 | 100.0% |
| adaptive | 100.0% | 0.0032 | 17.97 | 100.0% |

**Prespecified only locally for the developmental code**, not publicly: The adaptive policy had **no exact-attribution advantage** over random or cycle (all 100% in-model accuracy with both sensors at low noise). In this toy setting it used **17.97** nondefault commands against cycle's **30.00**. Seed-level mean difference adaptive minus cycle was **-12.03**, with an *exploratory*, paired seed-bootstrap 95% interval **[-12.36, -11.70]**. This difference is not an independent scientific discovery, and its cost definition favors 'wait until surprised' by construction. Every simulated cause is chosen from a small artificial menu.

**Identifiability counterexample:** With only one primary sensor, a physical drift and an equal shift in its sensory reading generate exactly the same observations for any command sequence. This equality is checked *sample-by-sample* in `test_exp08h.py`. A single-sensor learner has no legitimate way to know which one occurred. With two sensors but only one repeatedly chosen command, the linear response matrix is rank deficient; the model abstains rather than asserting a complete causal diagnosis.

### Post-pilot robustness (a separate exploratory sensitivity analysis)

48 additional development base seeds, three noise levels, reference available/unavailable, two probe policies, and original fixed vs a new **noise-calibrated** alarm rule. The latter estimates observation noise from calibration data, not from hidden simulator parameters. These sweeps were designed **after** the low-noise main results and are post-hoc exploratory.

| Condition | Exact in-model attribution (adaptive) | False alarms in unchanged worlds | Recognized novel nonlinear worlds |
|---|---:|---:|---:|
| 0.13/two_sensors/adaptive/fixed | 100.0% | 2.1% | 100.0% |
| 0.35/two_sensors/adaptive/fixed | 66.7% | 100.0% | 100.0% |
| 0.35/two_sensors/adaptive/calibrated | 47.1% | 0.0% | 6.2% |
| 0.65/two_sensors/adaptive/calibrated | 5.8% | 0.0% | 0.0% |
| 0.13/one_sensor/adaptive/fixed | 20.0% | 0.0% | 100.0% |

Increased noise sharply degrades reliability. The fixed threshold becomes **nearly universally false-alarming** in null worlds at high noise. Adjusting the threshold from an estimated sensor noise level avoids most false alarms in these sampled worlds, but fails to detect many real subtle changes. The apparent clean low-noise attribution does **not generalize**. More aggressive rejection is not equivalent to correct causal explanation, and an 'unknown' label does not explain a novel physical mechanism.

### Key limits and publication decision

1. **No evolution, no self-awareness, no consciousness outcome.** This is an explicitly designed observer using linear regression, engineered sensor factorization, and a D-optimal design heuristic.
2. **No learned causal ontology.** Parameters are learned without cause labels; the *types of mechanism* (action-dependent, action-independent, sensor-specific) were programmed. The nonlinear anomaly's detection uses a fixed residual threshold.
3. **Strong comparator ties.** Adaptive probing fails to outperform a simple deterministic cyclic experiment on attribution, so there is no demonstrated general advantage for the adaptive strategy.
4. **No external validation.** All studies use one linear-simulator family built by the same researcher. Initial calibration and independent high-quality reference stream are generous assumptions. Simulator causal truth may be read **only by the evaluation code**.
5. **Nonstationary noise and variable probes untested.** Noise stress demonstrates the fixed detector is fragile; we did not study arbitrary noise distribution shifts or adversarial sensor errors.
6. **Seed is the experimental unit.** Cases from the same seed and different causal conditions are correlated. Report the exact seeds and avoid treating every time step as an independent replication.
7. **Scientific novelty limited.** Active experiment design, dual control, system identification and interventional causal identification are longstanding research fields. A publishable advancement would need a *new*, externally audited methodology and comparison to literature-established algorithms on independent tasks.

## Reproduce

`pip install numpy` then run from this folder:

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest -v test_exp08h.py
OPENBLAS_NUM_THREADS=1 python exp08h.py --seeds 96 --out /tmp/exp08h-main
OPENBLAS_NUM_THREADS=1 python stress.py --seeds 48 --out /tmp/exp08h-stress
```

Compare against checked-in `development/{summary.json,per_world.csv}` and `development_stress/{summary.json,per_world.csv}`. Both source and outputs are part of the same exploratory release; CI reproduces them from scratch on GitHub before accepting an import. Rerun the commands on new hardware/NumPy versions to assess numeric portability.

### Prior art

- Hauser & Bühlmann (2014), **Two optimal strategies for active learning of causal models from interventional data**. DOI: https://doi.org/10.1016/j.ijar.2013.11.007
- Mesbah (2018), **Stochastic model predictive control with active uncertainty learning: A survey on dual control**. DOI: https://doi.org/10.1016/j.arcontrol.2017.11.001
- Zhang et al. (2023), **Active learning for optimal intervention design in causal models**. DOI: https://doi.org/10.1038/s42256-023-00719-0

**Next research gate:** Have an external researcher design an independent nonlinear dynamical world and review identifiability. Compare active interventions against calibrated information-gain or Bayesian controllers with matched sensor/compute/action budgets. Work toward any confirmatory preregistration only after this design is audited. The current simulations cannot test or establish subjective experience.
