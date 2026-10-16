"""Experiment 08: active discovery of inadequate representations.
Synthetic benchmark only. No claim of scientific novelty or general intelligence.
Requires numpy.
"""
from __future__ import annotations
import argparse, json
from dataclasses import dataclass
from pathlib import Path
import numpy as np

MODEL_NAMES = ("linear", "interaction", "quadratic", "difference")

def features(x: np.ndarray, name: str) -> np.ndarray:
    a, b = x[..., 0], x[..., 1]
    cols = [np.ones_like(a), a, b]
    if name == "interaction": cols.append(a*b)
    elif name == "quadratic": cols.extend([a*a, b*b])
    elif name == "difference": cols.append(np.abs(a-b))
    elif name != "linear": raise ValueError(name)
    return np.stack(cols, axis=-1)

@dataclass
class World:
    name: str
    coeff: np.ndarray
    noise: float
    def observe(self, x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        return features(x, self.name) @ self.coeff + rng.normal(0, self.noise, size=len(x))

def make_world(rng: np.random.Generator, noise: float = 0.05) -> World:
    name = MODEL_NAMES[int(rng.integers(len(MODEL_NAMES)))]
    p = features(np.zeros((1, 2)), name).shape[-1]
    coeff = rng.normal(0, 0.8, size=p)
    if name != "linear":
        coeff[-1] = rng.choice([-1.0, 1.0]) * rng.uniform(0.45, 1.25)
    return World(name, coeff, noise)

def fit_model(x: np.ndarray, y: np.ndarray, name: str):
    X = features(x, name)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    rss = float(np.sum(resid**2))
    n, k = X.shape
    score = n * np.log(max(rss / max(n, 1), 1e-12)) + k * np.log(max(n, 2))
    return beta, score

def fit_all(x: np.ndarray, y: np.ndarray):
    return {name: fit_model(x, y, name) for name in MODEL_NAMES}

def predict(x: np.ndarray, fitted, name: str) -> np.ndarray:
    return features(x, name) @ fitted[name][0]

def select_model(fitted):
    return min(MODEL_NAMES, key=lambda name: fitted[name][1])

def choose_active_query(fitted, rng: np.random.Generator, grid_size: int = 401):
    """Choose a query by weighted disagreement among candidate models."""
    grid = rng.uniform(-1, 1, size=(grid_size, 2))
    scores = np.array([fitted[n][1] for n in MODEL_NAMES])
    weights = np.exp(-0.5 * np.clip(scores - scores.min(), 0, 100))
    weights /= weights.sum()
    preds = np.stack([predict(grid, fitted, n) for n in MODEL_NAMES], axis=1)
    mean = (preds * weights[None, :]).sum(axis=1)
    disagreement = (weights[None, :] * (preds - mean[:, None])**2).sum(axis=1)
    idx = int(np.argmax(disagreement + rng.uniform(0, 1e-12, size=grid_size)))
    return grid[idx:idx+1]

def run_arm(world: World, seed: int, arm: str, budget: int = 32, initial: int = 8, test_n: int = 512):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, size=(initial, 2))
    y = world.observe(x, rng)
    for _ in range(budget - initial):
        fitted = fit_all(x, y)
        if arm == "active":
            q = choose_active_query(fitted, rng)
        elif arm in ("passive", "fixed_linear"):
            q = rng.uniform(-1, 1, size=(1, 2))
        else:
            raise ValueError(arm)
        yq = world.observe(q, rng)
        x = np.concatenate([x, q], axis=0)
        y = np.concatenate([y, yq])
    fitted = fit_all(x, y)
    chosen = "linear" if arm == "fixed_linear" else select_model(fitted)
    test_rng = np.random.default_rng(seed + 99173)
    test_x = test_rng.uniform(-1, 1, size=(test_n, 2))
    target = features(test_x, world.name) @ world.coeff
    pred = predict(test_x, fitted, chosen)
    return {"arm": arm, "true_model": world.name, "selected_model": chosen,
            "correct_model": bool(chosen == world.name), "test_mse": float(np.mean((target-pred)**2)),
            "observations": int(len(x))}

def run_benchmark(n_worlds=100, budget=32, initial=8, base_seed=20261015):
    rows=[]
    for i in range(n_worlds):
        world_seed = base_seed + i * 1009
        world = make_world(np.random.default_rng(world_seed))
        for arm in ("fixed_linear", "passive", "active"):
            rows.append({"seed": world_seed, **run_arm(world, world_seed, arm, budget, initial)})
    summary={}
    for arm in ("fixed_linear", "passive", "active"):
        subset=[r for r in rows if r["arm"]==arm]
        summary[arm]={"mean_test_mse":float(np.mean([r["test_mse"] for r in subset])),
                      "median_test_mse":float(np.median([r["test_mse"] for r in subset])),
                      "model_accuracy":float(np.mean([r["correct_model"] for r in subset])),
                      "n_worlds":len(subset)}
    by_seed={}
    for row in rows:
        by_seed.setdefault(row["seed"], {})[row["arm"]]=row
    rng=np.random.default_rng(71823)
    contrasts={}
    for left,right in (("passive","active"),("fixed_linear","passive"),("fixed_linear","active")):
        diffs=np.array([v[left]["test_mse"]-v[right]["test_mse"] for v in by_seed.values()])
        boot=np.array([np.mean(rng.choice(diffs,size=len(diffs),replace=True)) for _ in range(10000)])
        contrasts[f"{left}_minus_{right}_mse"]={"mean_difference":float(np.mean(diffs)),
            "bootstrap_95_ci":[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
            "worlds_right_better":int(np.sum(diffs>0)),"worlds_left_better":int(np.sum(diffs<0)),
            "ties":int(np.sum(diffs==0))}
    return {"config":{"n_worlds":n_worlds,"budget":budget,"initial":initial,"base_seed":base_seed},
            "summary":summary,"contrasts":contrasts,"rows":rows}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--worlds",type=int,default=100)
    p.add_argument("--budget",type=int,default=32)
    p.add_argument("--initial",type=int,default=8)
    p.add_argument("--seed",type=int,default=20261015)
    p.add_argument("--out",default="results.json")
    a=p.parse_args()
    result=run_benchmark(a.worlds,a.budget,a.initial,a.seed)
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"summary":result["summary"],"contrasts":result["contrasts"]},indent=2))
    print(f"Wrote {a.out}")

if __name__=="__main__":
    main()
