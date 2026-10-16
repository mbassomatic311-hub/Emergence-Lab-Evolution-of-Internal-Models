# Experiment 11 — Held-Out Target Generalization

**Status: exploratory falsification test.** Exp11 reuses the Exp10 learning procedure but evaluates it on five target families deliberately absent from Exp10's candidate feature grammar.

## Question

Does residual-guided compositional search improve prediction when the generating structure is outside the representation vocabulary it searches?

## Held-out targets

- `sin(2*pi*x1)*x2`
- `cos(pi*x1*x2)`
- `exp(-3*(x1-x2)^2)`
- `relu(x1*x2-0.15)`
- `sin(2*pi*x1)*sin(2*pi*x2)`

The targets include higher-frequency periodic structure, a nonlinear interaction, a localized smooth response, and a piecewise response. These are still synthetic functions, not real-world data.

## Run

From this directory:

```sh
python -m pip install numpy
python -m unittest -v
python engine11.py --worlds 30 --budget 36 --initial 10 --seed 20261018 --out exp11_results.json
```

Try noise stress separately with `--noise-sd 0.20`; keep the seed and budget fixed when comparing noise levels. Do not combine different noise regimes into one aggregate.

## Interpretation rules

- Compare fixed, passive, and active arms at identical budgets and matched world seeds.
- Predictive test MSE is primary. Exact symbolic recovery is not meaningful for targets absent from the grammar and is expected to be zero.
- Report all target families and paired uncertainty; do not treat a small smoke run as confirmatory evidence.
- Exp11 still does not include a strong regularized regression baseline or establish superiority to standard methods. Those are subsequent work.
- If the learned grammar performs poorly, report the failure. Do not add the held-out target terms to the candidate vocabulary and then call the same targets held out.
