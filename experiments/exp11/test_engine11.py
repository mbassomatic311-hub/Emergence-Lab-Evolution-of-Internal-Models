import unittest
import numpy as np
from engine11 import HELD_OUT, make_heldout_world, run_benchmark

class Experiment11Tests(unittest.TestCase):
    def test_targets_are_outside_exp10_grammar(self):
        from engine10 import CANDIDATES
        self.assertTrue(set(HELD_OUT).isdisjoint(CANDIDATES))

    def test_heldout_targets_are_finite_and_vectorized(self):
        rng = np.random.default_rng(11)
        x = rng.uniform(-1, 1, (32, 2))
        for seed in range(len(HELD_OUT)):
            world = make_heldout_world(np.random.default_rng(seed))
            y = world["target"](x)
            self.assertEqual(y.shape, (32,))
            self.assertTrue(np.isfinite(y).all())

    def test_benchmark_keeps_equal_budgets_and_all_arms(self):
        result = run_benchmark(worlds=2, budget=12, initial=6, seed=42)
        self.assertEqual(set(result["summary"]), {"fixed", "passive", "active"})
        self.assertTrue(all(row["observations"] == 12 for row in result["rows"]))
        self.assertEqual(len(result["rows"]), 6)
        self.assertIn("target_families", result["config"])

if __name__ == "__main__":
    unittest.main()
