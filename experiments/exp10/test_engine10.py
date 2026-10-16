import unittest
import numpy as np
from engine10 import BASE, CANDIDATES, design, feature_values, make_world, run_arm, screen_by_residual

class Experiment10Tests(unittest.TestCase):
    def test_feature_library_is_finite_and_consistent(self):
        x = np.array([[0.1, -0.2], [0.7, 0.4]])
        values = feature_values(x)
        self.assertTrue(set(BASE).issubset(values))
        self.assertTrue(set(CANDIDATES).issubset(values))
        self.assertTrue(np.isfinite(design(x, list(BASE + CANDIDATES))).all())

    def test_truth_is_a_composition(self):
        world = make_world(np.random.default_rng(8))
        self.assertIn("*", world["truth"])
        self.assertIn(world["truth"], CANDIDATES)

    def test_residual_screen_returns_unique_candidates(self):
        rng = np.random.default_rng(9)
        x = rng.uniform(-1, 1, (40, 2))
        y = x[:, 0] * np.sin(np.pi*x[:, 1])
        beta = np.linalg.lstsq(design(x, BASE), y, rcond=None)[0]
        residual = y - design(x, BASE) @ beta
        screened = screen_by_residual(x, residual, limit=8)
        self.assertEqual(len(screened), 8)
        self.assertEqual(len(set(screened)), 8)

    def test_arm_respects_observation_budget(self):
        world = make_world(np.random.default_rng(10))
        result = run_arm(world, 10, "passive", budget=20, initial=8, test_n=128)
        self.assertEqual(result["observations"], 20)
        self.assertTrue(np.isfinite(result["test_mse"]))

if __name__ == "__main__":
    unittest.main()
