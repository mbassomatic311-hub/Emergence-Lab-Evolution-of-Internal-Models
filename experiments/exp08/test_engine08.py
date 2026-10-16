import unittest
import numpy as np
from engine08 import MODEL_NAMES, features, make_world, run_arm, run_benchmark

class Experiment08Tests(unittest.TestCase):
    def test_feature_dimensions_and_finiteness(self):
        x=np.array([[0.2,-0.4],[1.0,0.5]])
        expected={"linear":3,"interaction":4,"quadratic":5,"difference":4}
        for name in MODEL_NAMES:
            z=features(x,name)
            self.assertEqual(z.shape,(2,expected[name]))
            self.assertTrue(np.isfinite(z).all())

    def test_world_reproducible(self):
        a=make_world(np.random.default_rng(12))
        b=make_world(np.random.default_rng(12))
        self.assertEqual(a.name,b.name)
        np.testing.assert_allclose(a.coeff,b.coeff)

    def test_arms_return_valid_metrics(self):
        world=make_world(np.random.default_rng(99))
        for arm in ("fixed_linear","passive","active"):
            r=run_arm(world,123,arm,budget=16,initial=6,test_n=64)
            self.assertEqual(r["observations"],16)
            self.assertGreaterEqual(r["test_mse"],0)
            self.assertIn(r["selected_model"],MODEL_NAMES)

    def test_benchmark_reports_paired_contrasts(self):
        r=run_benchmark(n_worlds=4,budget=12,initial=5,base_seed=77)
        self.assertEqual(r["summary"]["active"]["n_worlds"],4)
        self.assertIn("passive_minus_active_mse",r["contrasts"])

if __name__ == "__main__":
    unittest.main()
