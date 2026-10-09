# Emergence Lab — Experiment 07: Evolution of action-effect adaptation under unknown actuator polarity

**Protocol status:** Locally frozen *before the 32-seed primary run* on 2026-10-08 (Pacific). This is **not a public preregistration**. An exploratory two-seed implementation pilot (`seed-start 4100`) was run before freezing; those observations are **not** included in primary results. Protocol and engine hashes are recorded in `FROZEN_SHA256.txt`.

## Research question and scope
Can finite-lifetime selection on actual simulated outcomes evolve controllers that use an action-conditioned, internally maintained state to adapt to an unknown motor mapping, and does that behavior transfer to a surprising mid-life reversal? The project tests computational mechanisms of adaptation, not consciousness or phenomenal selfhood. Literature on efference copy and self-modeling predates this project. The sensorimotor feature and memory architecture are deliberately provided in the design; **neither emerged without design**.

## Data generating mechanism
64 candidate genetic controllers per population; 90 generations; 3 randomly simulated 40-step lifetimes per candidate per generation. Agent chooses left or right each step in an unbounded one-dimensional world. A food target is placed 3–6 units to left or right. The agent sees a noisy bearing to the target (relative position divided by 6); its motor command causes motion with an *unseen* sign, +1 or -1, randomly selected per lifetime. Each action costs 1 energy; acquiring food replenishes 12 energy; death occurs at energy <= 0. Scores are accumulated simulated food and survival, not analytically computed expected payoffs. Target relocates after consumption. Training lifetimes have fixed unseen polarity. Unexpected reversal test swaps polarity at step 20, which never occurs during training. Sensor noise standard deviation 0.04. Genotypes are eight continuous parameters with inherited variation, parameter mixing, and mutation. Evolution begins with random weights but **includes an engineered action–sensor difference input and a memory unit from the outset**.

## Conditions
- `full`: evolves all controller weights, including memory that updates with a normalized action-conditioned sensory difference.
- `reactive`: evolves the same eight-number genotypes and uses exactly the same environment, but memory is silenced during both training and tests.
- `random_selection`: same controller and inherited mutation as full, but parent choice is uniform regardless of reproductive performance.
- `no_inheritance`: fully new genomes sampled each generation; a valid random-sampling negative control but not perfectly effort-matched to inherited mutational search.
- `scrambled` (within full, **test-only**): after selection, substitute a random previous-command sign in the sensory-update feature. No training under this intervention.

## Fixed sampling and outcomes
Primary sample: 32 independently seeded evolutionary worlds `870000 + 71*i` for i=0,...,31. Pop=64, gens=90, train episodes=3, steps=40. At final generation, select six candidate genomes only using **fresh development trials in the stable environment** (16 episodes each), never the test results. Each selected controller is assessed over 128 fresh test episodes in two held-out conditions: stable actuator and untrained reversal at step 20. Common PRNG seed offsets are used across conditions. Seed is the independent statistical unit; agent test episodes are repeated-measure simulations, not independent replicate research studies.

**Primary outcome:** mean food rewards per 40-step *held-out reversal* test, averaged across the six selected controllers and 128 test episodes.

**Primary contrast H1:** full minus reactive > 0 in held-out reversal. 

**Secondary prespecified contrasts:** full minus random-selection > 0 and full minus test-time scrambled-copy > 0; full minus no-inheritance reported as context without passing/failing criterion. Secondary outcomes: held-out stable food and both survival fractions. No controller is selected based on held-out results. Report all 32 seeds, including failures.

## Analysis plan
Report means for all arms. Use seed-paired differences for comparisons. Compute percentile 95% bootstrap confidence intervals for the *mean paired difference*, using 10,000 resamples of 32 seeds with replacement, fixed bootstrap seed 50607. Pass H1 support threshold only if mean difference is positive AND bootstrap 95% lower bound > 0. Secondary contrasts are exploratory/uncorrected; their intervals do not justify discovery claims. Do not exclude any valid seeds. Reports shall include negative findings and simulator source for full replication.

## Pilot/design deviations
Two-seed exploratory pilot was run with a different seed set (4100, 4171); results were reviewed before this freeze. No tuning has been undertaken after the freeze. Any subsequent model edits must be versioned and the original run kept; any later analyses explicitly marked post hoc.

## Interpretive boundaries
The environment, actuator ambiguity, mutation operator, sensor access, energy mechanics, target reward, model architecture, and action-conditioned input are human-designed. The toy task is unusually favorable to memory and does not reproduce the full ecology of nervous-system evolution. Computation is not a consciousness measure; nothing here establishes first-person experience. If favorable, this is evidence of *task-specific adaptation by artificial evolution* and an illustrative model useful for teaching and further pre-registered work, not a novel theory of consciousness or automatic grounds for journal publication.
