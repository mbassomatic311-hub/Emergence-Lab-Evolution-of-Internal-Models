"""Tests for the openly post-hoc Experiment 07 comparator benchmark."""
import unittest
from audit08a_independent_baseline import rollout, bootstrap_diff, SEEDS

class ComparatorBenchmarkTests(unittest.TestCase):
    def test_determinism(self):
        self.assertEqual(rollout(870000, reversal=True), rollout(870000, reversal=True))
    def test_valid_scores(self):
        for c in ('comparator', 'naive'):
            for env in (False, True):
                x=rollout(870000, reversal=env, controller=c, n=57)
                self.assertGreaterEqual(x['food'], 0)
                self.assertLessEqual(x['food'], 40)
                self.assertTrue(0 <= x['survival'] <= 1)
    def test_bad_controller_rejected(self):
        with self.assertRaises(ValueError):
            rollout(870000, reversal=False, controller='oracle')
    def test_comparator_benefits_from_action_history(self):
        a=rollout(870000, reversal=True, controller='comparator', n=512)
        b=rollout(870000, reversal=True, controller='naive', n=512)
        self.assertGreater(a['food'], b['food'])
    def test_bootstrap_unit(self):
        r=bootstrap_diff([1, 2, 3], resamples=1000)
        self.assertEqual(r['mean_difference'], 2.0)
    def test_seeds_32_distinct(self):
        self.assertEqual(len(set(SEEDS)), 32)

if __name__ == '__main__':
    unittest.main()
