"""Emergence Lab post-hoc Experiment 07 audit: one-step sensorimotor comparator.

This is a deliberately hand-designed benchmark, NOT evolved behavior or evidence
for phenomenal consciousness. Independent simulator with the published 07 dynamics.
Uses only available observations and its own preceding motor command; it never
receives the hidden motor polarity. Openly post-hoc exploratory analysis.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np

STEPS = 40
EPISODES = 768   # 6 selected controllers x 128 tests in Experiment 07
SEEDS = tuple(870000 + i * 71 for i in range(32))


def rollout(seed: int, *, reversal: bool, sensor_noise: float = .04,
            controller: str = 'comparator', n: int = EPISODES):
    """World dynamics copied independently from protocol 07.

    Each trial starts with hidden random polarity and a target 3–6 units away.
    Controllers access only noisy target bearing and their previous actions.
    They never see position, target position, actual movement or polarity.
    """
    if controller not in {'comparator', 'naive'}:
        raise ValueError('unknown controller')
    rng = np.random.default_rng(seed + (200_000_000 if reversal else 100_000_000))
    x = np.zeros(n, dtype=float)
    target = rng.choice(np.array([-1., 1.]), size=n) * rng.integers(3, 7, size=n)
    hidden_polarity = rng.choice(np.array([-1., 1.]), size=n)
    energy = np.full(n, 20., dtype=float)
    alive = np.ones(n, dtype=bool)
    food = np.zeros(n, dtype=float)
    alive_steps = np.zeros(n, dtype=float)
    last_obs = np.zeros(n, dtype=float)
    last_action = np.zeros(n, dtype=float)
    # Prior guess is 50% correct, and subsequent movement calibrates it.
    estimated_polarity = np.ones(n, dtype=float)
    for t in range(STEPS):
        if reversal and t == 20:
            hidden_polarity = -hidden_polarity
        obs = (target-x)/6. + rng.normal(0, sensor_noise, size=n)
        if t > 0 and controller == 'comparator':
            signed_action_effect = -(obs-last_obs) * last_action * 6.
            can_update = (last_action != 0) & alive & (np.abs(signed_action_effect) > .25)
            estimated_polarity = np.where(can_update,
                                          np.where(signed_action_effect >= 0, 1., -1.),
                                          estimated_polarity)
        desired_direction = np.where(obs >= 0, 1., -1.)
        action = desired_direction * estimated_polarity
        x = np.where(alive, x + hidden_polarity * action, x)
        energy = np.where(alive, energy-1, energy)
        eaten = alive & (np.abs(target-x) < .5)
        food += eaten.astype(float)
        energy = np.where(eaten, np.minimum(27., energy+12.), energy)
        next_target = x + rng.choice(np.array([-1., 1.]), size=n) * rng.integers(3, 7, size=n)
        target = np.where(eaten, next_target, target)
        # New target is a discontinuous exogenous event, not a motor consequence.
        last_obs = np.where(eaten, (target-x)/6., obs)
        last_action = np.where(eaten, 0., action)
        alive_steps += alive.astype(float)
        alive &= energy > 0
    return {'food': float(np.mean(food)), 'survival': float(np.mean(alive_steps/STEPS))}


def bootstrap_diff(differences, resamples=10000, seed=81908):
    rng = np.random.default_rng(seed)
    arr = np.array(differences, dtype=float)
    bs = rng.choice(arr, size=(resamples, len(arr)), replace=True).mean(axis=1)
    return {'mean_difference': float(arr.mean()),
            'ci95_percentile': [float(v) for v in np.quantile(bs, [.025, .975])],
            'n_positive': int(np.sum(arr > 0)),
            'n_negative': int(np.sum(arr < 0)),
            'n_tied': int(np.sum(arr == 0))}


def run(previous_csv: str | None = None):
    prior = {}
    if previous_csv:
        with open(previous_csv, newline='') as f:
            for row in csv.DictReader(f):
                if row['condition'] == 'full':
                    prior[int(row['seed'])] = float(row['reversal_food'])
        if set(prior) != set(SEEDS):
            raise ValueError('prior seed set does not match frozen Experiment 07')
    rows = []
    for seed in SEEDS:
        row = {'seed': seed}
        for c in ('comparator','naive'):
            for env in ('stable','reversal'):
                metrics = rollout(seed, reversal=env == 'reversal', controller=c)
                for k,v in metrics.items():
                    row[f'{c}_{env}_{k}'] = v
        if prior:
            row['evolved_reversal_food'] = prior[seed]
        rows.append(row)
    summary = {'analysis_type':'POST-HOC exploratory benchmark, not preregistered',
               'n_independent_seed_worlds': len(SEEDS),
               'evaluation_episodes_per_seed': EPISODES,
               'controllers': {'comparator':'one-step prediction-error motor polarity estimator (non-evolved)',
                               'naive':'fixed polarity assumption, reactive non-evolved'},
               'means': {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k != 'seed'},
               'paired_comparator_minus_naive_reversal': bootstrap_diff([
                   r['comparator_reversal_food'] - r['naive_reversal_food'] for r in rows])}
    if prior:
        summary['paired_evolved_minus_comparator_reversal'] = bootstrap_diff([
            r['evolved_reversal_food']-r['comparator_reversal_food'] for r in rows])
    return rows, summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--previous-csv', default=None)
    p.add_argument('--out', default='.')
    args = p.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, summary = run(args.previous_csv)
    with (out/'benchmark_per_seed.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    (out/'benchmark_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
