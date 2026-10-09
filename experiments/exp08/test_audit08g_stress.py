import unittest
import numpy as np
from audit08g_stress import hybrid_world,profile_mse,run
from audit08g_causal_attribution import BASE_SEED,world

class StressTests(unittest.TestCase):
    def test_hybrids_repeatable(self):
        for cause in ('actuator_plus_wind','world_plus_visual','none'):
            a,b=hybrid_world(BASE_SEED,cause)
            c,d=hybrid_world(BASE_SEED,cause)
            np.testing.assert_array_equal(a,c);np.testing.assert_array_equal(b,d)
    def test_stress_dimensions(self):
        a,b,c=run(3)
        self.assertEqual(len(a),3*3*3*3)
        self.assertEqual(len(b),3*3)
        self.assertEqual(len(c['sweep']),9)
    def test_in_model_mse_small(self):
        a,b,*_=world(BASE_SEED,'actuator',active=True,reference=True)
        self.assertLess(profile_mse(a,b),.2)
    def test_out_of_family_not_guaranteed_identifiable(self):
        a,b=hybrid_world(BASE_SEED,'actuator_plus_wind')
        self.assertGreater(profile_mse(a,b),.2)
    def test_invalid_hybrid(self):
        with self.assertRaises(ValueError):hybrid_world(BASE_SEED,'supernatural')

if __name__=='__main__':unittest.main()
