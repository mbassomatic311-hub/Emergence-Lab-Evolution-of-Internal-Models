"""Experiment 11: held-out target-family stress test for Exp10.

Targets are intentionally outside Exp10's documented candidate grammar. This
tests out-of-grammar predictive generalization, not symbolic recovery or novelty.
Requires NumPy and experiments/exp10/engine10.py.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "exp10"))
from engine10 import run_arm

HELD_OUT = (
    "sin(2*pi*x1)*x2",
    "cos(pi*x1*x2)",
    "exp(-3*(x1-x2)^2)",
    "relu(x1*x2-0.15)",
    "sin(2*pi*x1)*sin(2*pi*x2)",
)

def make_heldout_world(rng: np.random.Generator, noise_sd: float = 0.08):
    truth = HELD_OUT[int(rng.integers(len(HELD_OUT)))]
    amp = float(rng.uniform(0.65, 1.35))
    def target(x):
        a, b = x[:, 0], x[:, 1]
        if truth == "sin(2*pi*x1)*x2":
            g = np.sin(2*np.pi*a)*b
        elif truth == "cos(pi*x1*x2)":
            g = np.cos(np.pi*a*b)
        elif truth == "exp(-3*(x1-x2)^2)":
            g = np.exp(-3*(a-b)**2)
        elif truth == "relu(x1*x2-0.15)":
            g = np.maximum(a*b-0.15, 0.0)
        else:
            g = np.sin(2*np.pi*a)*np.sin(2*np.pi*b)
        return 0.3*a - 0.2*b + amp*g
    return {"truth": truth, "amp": amp, "noise_sd": noise_sd, "target": target}

def run_benchmark(worlds=30, budget=36, initial=10, seed=20261018, noise_sd=0.08):
    rows = []
    for i in range(worlds):
        world_seed = seed + i*1009
        world = make_heldout_world(np.random.default_rng(world_seed), noise_sd)
        for arm in ("fixed", "passive", "active"):
            row = run_arm(world, world_seed, arm, budget=budget, initial=initial)
            rows.append({"seed": world_seed, "target_family": world["truth"], **row})
    summary = {}
    for arm in ("fixed", "passive", "active"):
        group = [r for r in rows if r["arm"] == arm]
        summary[arm] = {
            "mean_test_mse": float(np.mean([r["test_mse"] for r in group])),
            "median_test_mse": float(np.median([r["test_mse"] for r in group])),
            "n_worlds": len(group),
            "out_of_grammar_recovery_rate": float(np.mean([r["recovered_true_composition"] for r in group])),
        }
    by_seed = {}
    for row in rows:
        by_seed.setdefault(row["seed"], {})[row["arm"]] = row
    rng = np.random.default_rng(seed + 11011)
    contrasts = {}
    for left, right in (("passive", "active"), ("fixed", "passive"), ("fixed", "active")):
        d = np.array([v[left]["test_mse"]-v[right]["test_mse"] for v in by_seed.values()])
        boot = np.array([np.mean(rng.choice(d, size=len(d), replace=True)) for _ in range(3000)])
        contrasts[f"{left}_minus_{right}"] = {
            "mean_mse_difference": float(np.mean(d)),
            "bootstrap_95_ci": [float(np.quantile(boot, .025)), float(np.quantile(boot, .975))],
            "left_lower_error_worlds": int(np.sum(d < 0)),
            "right_lower_error_worlds": int(np.sum(d > 0)),
        }
    return {
        "config": {"worlds": worlds, "budget": budget, "initial": initial, "seed": seed, "noise_sd": noise_sd,
                   "target_families": list(HELD_OUT)},
        "summary": summary, "contrasts": contrasts, "rows": rows,
        "interpretation_note": "All target families are outside Exp10's candidate grammar. Zero exact-recovery is expected; predictive MSE is the primary metric.",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", type=int, default=30)
    p.add_argument("--budget", type=int, default=36)
    p.add_argument("--initial", type=int, default=10)
    p.add_argument("--seed", type=int, default=20261018)
    p.add_argument("--noise-sd", type=float, default=0.08)
    p.add_argument("--out", default="exp11_results.json")
    a = p.parse_args()
    if a.worlds < 2 or a.initial < 2 or a.budget < a.initial or a.noise_sd < 0:
        p.error("require worlds >= 2, initial >= 2, budget >= initial, and noise-sd >= 0")
    result = run_benchmark(a.worlds, a.budget, a.initial, a.seed, a.noise_sd)
    Path(a.out).write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"config": result["config"], "summary": result["summary"], "contrasts": result["contrasts"]}, indent=2))
    print(f"Wrote {a.out}")

if __name__ == "__main__":
    main()
