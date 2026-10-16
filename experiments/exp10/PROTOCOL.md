# Experiment 10 protocol (exploratory)

## Hypothesis
Residual-screened composition improves held-out prediction and recovers the generating composition more often than the fixed baseline. Disagreement-guided queries may help compared with passive random queries, but this is a secondary hypothesis.

## Data generation
- Inputs: independent uniform samples in [-1, 1]^2.
- Target: 0.3*x1 - 0.2*x2 + A*g(x1,x2), where A is uniform on [0.65, 1.35].
- Noise: independent Gaussian noise, standard deviation 0.08.
- Truth g: one of eight predeclared compositional expressions in engine10.py.
- Observation budget: 48 total points; 12 initial points.
- Held-out score: mean squared error on 2,048 noiseless test inputs per world.

## Comparisons
- fixed: baseline features only.
- passive: random queries; same candidate grammar and final model-selection rule.
- active: disagreement-guided queries; same candidate grammar and final model-selection rule.

## Reporting
Report mean and median held-out MSE, composition recovery rate, paired mean MSE differences, percentile bootstrap 95% intervals, and counts of worlds each arm wins. Use identical world seeds across arms. Preserve full per-world rows.

## Limitations / safeguards
This is exploratory because the target family and candidate grammar are known to the experiment author and informed implementation. Do not use these same target expressions as a confirmatory test set. Candidate screening and BIC are heuristic; compare with regularization and oracle baselines before making strong claims. A poor result is informative and must not be silently discarded.
