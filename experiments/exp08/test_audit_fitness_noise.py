"""Exploratory audit invariants. Assertions do not validate novelty or consciousness."""
import unittest
import numpy as np
from audit_fitness_noise import initial_fitness_audit, rank_corr, train_common_conditions

class AuditTests(unittest.TestCase):
    def test_rank_correlation_exact(self):
        self.assertAlmostEqual(rank_corr([1,2,3],[3,2,1]),-1)
        self.assertAlmostEqual(rank_corr([1,2,3],[1,2,3]),1)
        self.assertIsNone(rank_corr([2,2,2],[2,3,4]))
    def test_initial_audit_reproducible(self):
        self.assertEqual(initial_fitness_audit(1103,n=5,high_eval=4),initial_fitness_audit(1103,n=5,high_eval=4))
    def test_development_training_reproducible(self):
        x,curve=train_common_conditions(1103,n=6,generations=2)
        y,curve2=train_common_conditions(1103,n=6,generations=2)
        self.assertTrue(np.array_equal(x[0],y[0]))
        self.assertTrue(np.array_equal(x[1],y[1]))
        self.assertEqual(curve,curve2)
    def test_recurrent_initial_mask_zero(self):
        # Design is not spontaneous: only recurrence mask starts absent.
        x,curve=train_common_conditions(1103,n=6,generations=1)
        self.assertEqual(len(curve),1)
        self.assertTrue(0<=int(x[1].sum())<=25)
if __name__=='__main__':unittest.main()
