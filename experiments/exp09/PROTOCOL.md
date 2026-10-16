# Experiment 09 Protocol — Bounded Representation Invention

**Status:** exploratory protocol, written with implementation. Results from this implementation are exploratory until the code, seed range, and analysis are frozen before an untouched run.

## Hypothesis

When the true rule is outside the original feature family but expressible using a broader documented grammar, adding a feature-discovery mechanism improves held-out prediction over the original fixed representation. Active disagreement sampling may or may not improve on passive sampling; that is a separate comparison.

## Synthetic world

Inputs are two real-valued variables sampled in [-1, 1]. The output includes a shared linear background plus one nonlinear term selected from six functions: `sin(pi*x1*x2)`, `x1^3`, `tanh(2*x1*x2)`, `sin(pi*(x1+x2))`, `x1^2*x2`, or `cos(pi*x1)`, with additive Gaussian observation noise (SD 0.08).

## Arms and budget

- 10 initial random observations, 30 further observations by default.
- Fixed original representation.
- Passive sampling + final BIC-like selection from the original model and one-term expansions.
- Active sampling by weighted disagreement among those same candidates + identical final selection.
- Held-out prediction uses fresh random inputs and the noise-free underlying target.
- Primary unit: generated world; contrasts are paired by world seed.
- Bootstrap interval: resampling worlds with fixed seed, 5,000 replicates.

## Threats to validity

The true function is in the larger grammar by construction; the benchmark is deliberately bounded and may favor the algorithm. Model score calibration, feature collinearity, small sample size, and active query distribution can affect outcomes. A feature-discovery rate is not a proof of understanding. The active strategy may lose to passive sampling.

## Confirmatory separation

Do not treat development runs as confirmatory. Before a formal run, freeze the code and seeds, preregister sample size and one primary contrast, and add a held-out generator family not used to design the discovery grammar. Report null and negative results.
