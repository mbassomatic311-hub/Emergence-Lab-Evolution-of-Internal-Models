# Emergence Lab Experiment 07
## Evolving action-conditioned adaptation under uncertain motor effects: an exploratory computational study

**Status: exploratory independent computational simulation. NOT peer-reviewed, externally replicated, or publicly preregistered.**

### Abstract
We simulated populations of agents who chose discrete motor commands in a noisy, one-dimensional resource world. The relationship between motor commands and movement was initially hidden and randomized across individual lifetimes. Controllers were selected using finite stochastic lifetime outcomes over 90 generations. A locally frozen protocol specified 32 independent evolutionary seeds, four arms and a held-out evaluation in which actuator polarity reversed unexpectedly halfway through a lifetime. The primary comparison was evolved controllers with an engineered action-conditioned recurrent state against reactive controllers. Evolved recurrent controllers collected 5.072 food rewards per 40-step held-out reversal lifetime versus 2.034 for reactive controls. The paired seed mean difference was 3.038 (95% seed-bootstrap CI 2.200, 3.891); the prespecified positive-difference criterion was met. Test-time scrambling of the action-effect feedback yielded an observed mean difference of 3.741 (95% CI 2.743, 4.722); interpretation is limited by unequal downstream random draws in this ablation. These synthetic results address adaptability in evolutionary computation, NOT subjective experience or the emergence of consciousness.

### Research aim
Determine whether stochastic selection over actual simulated lifetimes can favor an action-conditioned feedback representation and produce transfer to an untrained actuator reversal, relative to appropriate controls. The study was motivated by questions about precursors to evolved self/world modeling, but measures only action choices, food rewards, and survival.

### Prior art
Body modeling and sensorimotor prediction in robotics have been studied for decades. Bongard, Zykov & Lipson (2006) demonstrated resilient robot adaptation using continuous self-modeling (doi:10.1126/science.1133687). Nguyen et al. (2020) surveyed sensorimotor representations of an active self (arXiv:2011.12860). Kahl et al. (2021) modeled sense of control in situated artificial agents (arXiv:2112.05577). Accordingly, we make NO priority, novelty, or phenomenal-consciousness claim.

### Protocol timeline and status
An exploratory two-seed implementation pilot (seeds 4100 and 4171) was viewed BEFORE freezing the primary protocol and source. The protocol and source were locally frozen and hashed before main analysis; hashes reside in FROZEN_SHA256.txt. The 32 primary seeds were disjoint from the pilot: 870000 + 71i for i = 0,...,31. **Local hashing is not OSF preregistration.** No later parameters were optimized based on main-study results.

### World and genetic controller
- Population: 64 eight-parameter genotypes. 90 generations, each with three stochastic 40-step lifetimes per genotype; selection based on actual food rewards and time alive, not an expected-fitness oracle.
- At each step each agent selects a left/right action. A hidden, episode-specific actuator polarity determines physical movement. Food appears 3–6 units to either side. Agents see a noisy relative bearing to food (not the hidden actuator setting). Actions consume energy, while collecting food restores energy.
- Agents can evolve weights for a fixed, provided memory unit using an engineered action-conditioned sensory-difference feature. They do NOT evolve their own sensors, a body morphology, or the connection architecture itself.
- A food relocation resets the previous-command signal so that new target creation is not mistaken for self-caused movement.
- Final candidate selection: six controllers chosen using 16 new *development* lifetimes in the training distribution. Held-out tests: 128 fresh episodes per selected controller. Test results are never used for selection.

### Arms and comparisons
1. Full: action-conditioned memory capable of integrating previous action effects.
2. Reactive: same overall genome representation, memory silenced.
3. Random selection: memory available but reproduction parent choice independent of fitness.
4. No inheritance: fresh genome population every generation (not compute-matched to inherited search).
5. Full with test-time scrambled action-copy: action feedback corrupted only during held-out evaluation. This is a test-time intervention, not a fifth independently evolved lineage.

### Prespecified analyses
The primary outcome is food collected per 40-step episode following an untrained actuator reversal at step 20. Primary contrast: full minus reactive, 32 paired evolutionary seeds. Secondary contrasts: random-selection, no-inheritance, and scrambled feedback. Bootstrap: 10,000 resamples of seed-level paired differences, fixed bootstrap seed 50607, percentile 95% intervals. These are within-model seed intervals and do not quantify biological uncertainty. The primary directional support criterion required a positive estimated mean and a 95% interval lower bound greater than zero.

### Results (held-out)
| Condition | Mean reversal food | Mean stable food | Reversal survival fraction |
|---|---:|---:|---:|
| Evolved action history | 5.072 | 6.475 | 0.899 |
| Reactive only | 2.034 | 4.207 | 0.751 |
| Random selection | 1.938 | 3.175 | 0.757 |
| No inheritance | 2.038 | 3.499 | 0.768 |

Paired mean effects on reversal food rewards (full minus comparison):
- **reactive:** 3.038 (95% bootstrap CI [2.200, 3.891]); seed outcomes: 25 positive, 7 negative, 0 ties.
- **random-selection:** 3.134 (95% bootstrap CI [2.243, 3.993]); seed outcomes: 28 positive, 4 negative, 0 ties.
- **no-inheritance:** 3.034 (95% bootstrap CI [2.152, 3.880]); seed outcomes: 30 positive, 2 negative, 0 ties.
- **scrambled feedback:** 3.741 (95% bootstrap CI [2.743, 4.722]); seed outcomes: 30 positive, 2 negative, 0 ties.

### Sensitivity checks and limitations
1. This is a task intentionally designed to reward learning an unknown actuator mapping; transfer is tested within the same synthetic world family. We did not compare independently authored simulators, ecological tasks, controller families, or mutation-rate regimes.
2. The critical sensorimotor term and recurrent memory unit were included by design. Favorable outcomes cannot be described as a system inventing selfhood, a new network architecture, or basic awareness.
3. The reactive control is inherently less expressive, and the random/no-inheritance controls have different search dynamics. A complexity-matched nonrecurrent network, alternative policies (e.g. hand-coded Bayes) and reparameterizations should be added in follow-up work.
4. Unexpected actuator polarity inversion is a simplified distribution shift; it does not establish general world-model learning. Other transfer tests (sensor dropout, actuator latency, target dynamics, 2D worlds) are needed.
5. Within-agent scramble draws extra random numbers from the same generator, so full-vs-scrambled outcomes are not matched on exactly the same downstream environmental randomness; treat that secondary ablation as suggestive only.
6. Seed-bootstrap intervals represent outcomes under one invented world and fixed hyperparameters. They are not probability statements about consciousness or natural evolution.
7. Development-pilot observations preceded the local protocol freeze; there is no independent preregistration or third-party code audit.
8. Multiple comparisons were not adjusted, and secondary differences are descriptive.

### Interpretation and publication decision
This study is reproducible exploratory work in artificial evolution. If replicated with independent code and new environmental families, the result could support a narrow educational or methods-focused technical note about action-conditioned adaptation. It does NOT demonstrate an origin of consciousness, subjective experience, or a breakthrough in evolutionary neuroscience. For an externally credible research submission, publicly preregister an independently reimplemented Experiment 08 before any new data collection, compare architectural and reward alternatives, and invite an experienced evolutionary-robotics researcher to audit the design.

### Sources and provenance
- Bongard, Zykov, Lipson (2006), *Resilient Machines Through Continuous Self-Modeling*, Science. https://pubmed.ncbi.nlm.nih.gov/17110570/
- Nguyen et al. (2020), *Sensorimotor representation learning for an active self in robots: A model survey*. https://arxiv.org/abs/2011.12860
- Kahl et al. (2021), *Towards autonomous artificial agents with an active self*. https://arxiv.org/abs/2112.05577
- OSF preregistration documentation, including simulation-specific templates: https://help.osf.io/article/330-welcome-to-registrations
- Reproduce: `python -m unittest -q test_engine07.py && python engine07.py --seeds 32 --seed-start 870000 --out primary`
