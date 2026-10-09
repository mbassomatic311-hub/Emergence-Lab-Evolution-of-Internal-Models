"""Parity checks for the independently written Experiment 07 environment.

When both models use the same sensor-only reactive rule, their simulated
food and survival averages must match exactly for the same RNG seeds.
"""
import unittest
import numpy as np
from engine07 import episodes
from audit08a_independent_baseline import rollout

class ParityTests(unittest.TestCase):
    def test_exact_naive_physics_matches_frozen_experiment07(self):
        n = 768
        params = np.zeros((n, 8), dtype=float)
        params[:, 4] = 1.0  # Controller in original engine: action = sign(noisy bearing).
        for seed in (870000, 870071, 871420):
            for reversal in (False, True):
                rng = np.random.default_rng(
                    seed + (200_000_000 if reversal else 100_000_000))
                food, survival = episodes(params, rng, 1, reversal, 'reactive')
                independent = rollout(seed, reversal=reversal, controller='naive', n=n)
                self.assertEqual(float(food.mean()), independent['food'])
                self.assertEqual(float(survival.mean()), independent['survival'])

if __name__ == '__main__':
    unittest.main()
