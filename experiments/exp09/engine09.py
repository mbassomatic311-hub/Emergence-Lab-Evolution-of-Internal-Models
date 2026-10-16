"""Experiment 09: representation invention outside Experiment 08's model family.

The algorithm may add one discovered feature from a documented symbolic grammar.
This is a bounded proof-of-concept, not unrestricted invention or a novelty claim.
Requires Python 3.10+ and NumPy.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

BASE_NAMES = ("1", "x1", "x2", "x1*x2", "x1^2", "x2^2", "abs(x1-x2)")
DISCOVERY_NAMES = (
    "x1^3", "x2^3", "x1^2*x2", "x1*x2^2",
    "sin(pi*x1)", "cos(pi*x1)", "sin(pi*x2)", "cos(pi*x2)",
    "sin(pi*x1*x2)", "cos(pi*x1*x2)", "tanh(2*x1*x2)",
    "abs(x1+x2)", "sin(pi*(x1+x2))", "x1^2-x2^2",
)

def feature_values(x: np.ndarray) -> dict[str, np.ndarray]:
    a, b = x[:, 0], x[:, 1]
    return {
        "1": np.ones(len(x)), "x1": a, "x2": b, "x1*x2": a*b,
        "x1^2": a*a, "x2^2": b*b, "abs(x1-x2)": np.abs(a-b),
        "x1^3": a**3, "x2^3": b**3, "x1^2*x2": a*a*b, "x1*x2^2": a*b*b,
        "sin(pi*x1)": np.sin(np.pi*a), "cos(pi*x1)": np.cos(np.pi*a),
        "sin(pi*x2)": np.sin(np.pi*b), "cos(pi*x2)": np.cos(np.pi*b),
        "sin(pi*x1*x2)": np.sin(np.pi*a*b), "cos(pi*x1*x2)": np.cos(np.pi*a*b),
        "tanh(2*x1*x2)": np.tanh(2*a*b), "abs(x1+x2)": np.abs(a+b),
        "sin(pi*(x1+x2))": np.sin(np.pi*(a+b)), "x1^2-x2^2": a*a-b*b,
    }

def matrix(x: np.ndarray, names: tuple[str, ...] | list[str]) -> np.ndarray:
    f = feature_values(x)
    return np.column_stack([f[n] for n in names])

def make_world(rng: np.random.Generator, noise_sd: float = 0.08):
    # The true function is drawn from outside Experiment 08's original model family.
    choices = ("sin(pi*x1*x2)", "x1^3", "tanh(2*x1*x2)", "sin(pi*(x1+x2))",
               "x1^2*x2", "cos(pi*x1)")
    truth = choices[int(rng.integers(len(choices)))]
    f = feature_values(np.zeros((1, 2)))
    coeffs = rng.normal(0, 0.7, size=3)
    amp = float(rng.uniform(0.65, 1.35))
    def target(x):
        z = feature_values(x)
        # Shared background makes identifying the new term a genuine regression task.
        return 0.35*z["x1"] - 0.25*z["x2"] + amp*z[truth]
    return {"truth": truth, "amp": amp, "noise_sd": noise_sd, "target": target}

def fit_score(x, y, names):
    X = matrix(x, names)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y-X@beta
    n, k = X.shape
    rss = float(resid@resid)
    bic = n*np.log(max(rss/n, 1e-12)) + k*np.log(max(n, 2))
    return beta, bic

def candidate_fits(x, y):
    models = [BASE_NAMES]
    models.extend(tuple(BASE_NAMES)+(name,) for name in DISCOVERY_NAMES)
    return [(names, *fit_score(x, y, names)) for names in models]

def choose_active_query(x, y, rng, grid_size=1001):
    fitted = candidate_fits(x, y)
    scores = np.array([item[2] for item in fitted])
    # Approximate Bayesian model weights, stabilized against score outliers.
    delta = np.clip(scores-scores.min(), 0, 80)
    weights = np.exp(-0.5*delta)
    weights /= weights.sum()
    grid = rng.uniform(-1, 1, size=(grid_size, 2))
    predictions = np.column_stack([
        matrix(grid, item[0]) @ item[1] for item in fitted
    ])
    mean = predictions @ weights
    disagreement = np.sum(weights[None, :]*(predictions-mean[:, None])**2, axis=1)
    return grid[[int(np.argmax(disagreement))]]

def run_arm(world, seed, arm, budget=40, initial=10, test_n=2048):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, size=(initial, 2))
    y = world["target"](x) + rng.normal(0, world["noise_sd"], size=initial)
    for _ in range(budget-initial):
        if arm == "active_expand":
            q = choose_active_query(x, y, rng)
        elif arm in ("passive_expand", "fixed_original"):
            q = rng.uniform(-1, 1, size=(1, 2))
        else:
            raise ValueError(arm)
        yq = world["target"](q) + rng.normal(0, world["noise_sd"], size=1)
        x = np.concatenate((x, q))
        y = np.concatenate((y, yq))
    if arm == "fixed_original":
        names = BASE_NAMES
        beta, _ = fit_score(x, y, names)
    else:
        fitted = candidate_fits(x, y)
        names, beta, _ = min(fitted, key=lambda z: z[2])
    test_rng = np.random.default_rng(seed+99173)
    tx = test_rng.uniform(-1, 1, size=(test_n, 2))
    truth = world["target"](tx)
    pred = matrix(tx, names)@beta
    discovered = world["truth"] in names
    return {"arm": arm, "true_new_feature": world["truth"],
            "selected_features": list(names), "discovered_true_feature": bool(discovered),
            "test_mse": float(np.mean((truth-pred)**2)), "observations": int(len(x))}

def run_benchmark(n_worlds=200, budget=40, initial=10, base_seed=20261016):
    rows=[]
    for i in range(n_worlds):
        seed=base_seed+i*1009
        world=make_world(np.random.default_rng(seed))
        for arm in ("fixed_original", "passive_expand", "active_expand"):
            rows.append({"seed":seed, **run_arm(world, seed, arm, budget, initial)})
    summary={}
    for arm in ("fixed_original", "passive_expand", "active_expand"):
        sub=[r for r in rows if r["arm"]==arm]
        summary[arm]={"mean_test_mse":float(np.mean([r["test_mse"] for r in sub])),
                      "median_test_mse":float(np.median([r["test_mse"] for r in sub])),
                      "feature_discovery_rate":float(np.mean([r["discovered_true_feature"] for r in sub])),
                      "n_worlds":len(sub)}
    paired={}
    for seed in sorted({r["seed"] for r in rows}):
        paired[seed]={r["arm"]:r for r in rows if r["seed"]==seed}
    rng=np.random.default_rng(80911)
    contrasts={}
    for left,right in (("passive_expand","active_expand"),
                       ("fixed_original","passive_expand"),
                       ("fixed_original","active_expand")):
        d=np.array([v[left]["test_mse"]-v[right]["test_mse"] for v in paired.values()])
        boot=np.array([np.mean(rng.choice(d,size=len(d),replace=True)) for _ in range(5000)])
        contrasts[f"{left}_minus_{right}"]={
            "mean_mse_difference":float(np.mean(d)),
            "bootstrap_95_ci":[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
            "left_lower_error_worlds":int(np.sum(d<0)),
            "right_lower_error_worlds":int(np.sum(d>0))}
    return {"config":{"n_worlds":n_worlds,"budget":budget,"initial":initial,
                      "base_seed":base_seed,"noise_sd":0.08},
            "summary":summary,"contrasts":contrasts,"rows":rows}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--worlds",type=int,default=200)
    p.add_argument("--budget",type=int,default=40)
    p.add_argument("--initial",type=int,default=10)
    p.add_argument("--seed",type=int,default=20261016)
    p.add_argument("--out",default="exp09_results.json")
    a=p.parse_args()
    result=run_benchmark(a.worlds,a.budget,a.initial,a.seed)
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"summary":result["summary"],"contrasts":result["contrasts"]},indent=2))
    print(f"Wrote {a.out}")
if __name__=="__main__":
    main()
