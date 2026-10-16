import unittest
import numpy as np
from engine09 import BASE_NAMES, DISCOVERY_NAMES, feature_values, make_world, run_arm, run_benchmark

class Experiment09Tests(unittest.TestCase):
    def test_discovery_grammar_has_finite_features(self):
        x=np.array([[-1.0,0.2],[0.0,0.0],[0.3,-0.7],[1.0,1.0]])
        vals=feature_values(x)
        self.assertTrue(set(BASE_NAMES).issubset(vals))
        self.assertTrue(set(DISCOVERY_NAMES).issubset(vals))
        for value in vals.values():
            self.assertEqual(value.shape,(4,))
            self.assertTrue(np.isfinite(value).all())

    def test_world_truth_is_outside_original_feature_family(self):
        allowed={"x1","x2","x1*x2","x1^2","x2^2","abs(x1-x2)"}
        for seed in range(20):
            w=make_world(np.random.default_rng(seed))
            self.assertNotIn(w["truth"],allowed)

    def test_arms_respect_observation_budget(self):
        w=make_world(np.random.default_rng(22))
        for arm in ("fixed_original","passive_expand","active_expand"):
            result=run_arm(w,55,arm,budget=14,initial=6,test_n=64)
            self.assertEqual(result["observations"],14)
            self.assertGreaterEqual(result["test_mse"],0)
            self.assertTrue(result["selected_features"])

    def test_benchmark_paired_results(self):
        r=run_benchmark(n_worlds=3,budget=12,initial=5,base_seed=44)
        self.assertEqual(r["summary"]["active_expand"]["n_worlds"],3)
        self.assertIn("passive_expand_minus_active_expand",r["contrasts"])

if __name__=="__main__":
    unittest.main()
