# Experiment 11 protocol (exploratory)

## Primary hypothesis
Residual-guided active sampling has lower held-out predictive MSE than passive sampling when the generating function is outside Exp10's candidate grammar.

## Design
- Inputs: uniform in [-1, 1]^2.
- Target: 0.3*x1 - 0.2*x2 + A*g(x1,x2), with A uniform on [0.65, 1.35].
- Held-out g: one of five expressions listed in README and absent from Exp10's CANDIDATES.
- Default noise SD: 0.08; stress condition: 0.20.
- Default budget: 36 observations, including 10 initial points.
- Test MSE: noiseless targets on 2,048 uniformly sampled points.
- Arms: fixed baseline, passive random-query discovery, active disagreement-guided discovery.
- World seed: base seed + 1009*i; the same world seed is used across arms.

## Outcomes
Primary: paired active-minus-passive test MSE and percentile bootstrap 95% interval.
Secondary: fixed-vs-discovery contrasts, median MSE, per-family error, and exact-recovery rate (reported only to make clear that out-of-grammar exact recovery is not expected).

## Safeguards
The held-out expressions must remain absent from the candidate grammar. Run default and stress noise as separate conditions. This benchmark is synthetic and finite; no claim of unrestricted representation invention or real-world superiority is justified. A later study must add a regularized regression baseline, broader target distributions, and more worlds.
