import unittest
import numpy as np
from audit08g_causal_attribution import world, infer, planned_actions, CLASS_NAMES, BASE_SEED, catalog, run

class AttributionTests(unittest.TestCase):
    def test_deterministic(self):
        a,b,*_=world(BASE_SEED,'actuator',active=True)
        c,d,*_=world(BASE_SEED,'actuator',active=True)
        np.testing.assert_array_equal(a,c);np.testing.assert_array_equal(b,d)
    def test_identical_passive_single_channel_counterfactual(self):
        readings=[world(BASE_SEED,cl,active=False,reference=False)[1] for cl in CLASS_NAMES]
        for r in readings[1:]:np.testing.assert_array_equal(r,readings[0])
    def test_passive_second_channel_equivalence_actuator_world(self):
        a=world(BASE_SEED,'actuator',active=False,reference=True)[1]
        b=world(BASE_SEED,'world',active=False,reference=True)[1]
        np.testing.assert_array_equal(a,b)
    def test_second_channel_can_separate_sensor(self):
        a=world(BASE_SEED,'world',active=False,reference=True)[1]
        b=world(BASE_SEED,'visual',active=False,reference=True)[1]
        self.assertGreater(np.linalg.norm(a-b),1)
    def test_active_noop_and_orthogonal_intervention(self):
        x=planned_actions((1.,0.),True)
        self.assertTrue(np.any(np.all(x==0,axis=1)))
        self.assertTrue(np.any(np.all(x==[0.,1.],axis=1)))
    def test_posterior_observation_indistinguishability(self):
        act,obs,_,_=world(BASE_SEED,'actuator',active=False,reference=False)
        x=infer(act,obs,reference=False)
        self.assertEqual(x['label'],'undetermined')
        for name in CLASS_NAMES:self.assertAlmostEqual(x['posterior'][name],1/3,places=9)
        self.assertLess(x['posterior']['no_change'],1e-8)
    def test_dual_passive_motor_vs_wind_ambiguity(self):
        act,obs,_,_=world(BASE_SEED,'actuator',active=False,reference=True)
        x=infer(act,obs,reference=True)
        self.assertEqual(x['label'],'undetermined')
        self.assertAlmostEqual(x['posterior']['actuator'],.5,places=8)
        self.assertAlmostEqual(x['posterior']['world'],.5,places=8)
    def test_no_oracle_cause_access(self):
        # Only acts + visible effect readings are passed to infer; not world seed/truth.
        act,obs,*_=world(BASE_SEED,'visual',active=True,reference=True)
        self.assertEqual(infer(act,obs)['label'],'visual')
    def test_reject_incompatible_sensor_shapes(self):
        with self.assertRaises(ValueError):infer(np.ones((2,2)),np.ones((2,2)),True)
    def test_reject_bad_world_config(self):
        with self.assertRaises(ValueError):world(BASE_SEED,'oracle')
    def test_small_full_design(self):
        rows,result=run(4)
        self.assertEqual(len(rows),4*3*4)
        self.assertEqual(set(result['conditions']),{'passive_single','passive_dual','active_single','active_dual'})
    def test_active_dual_attribution_high(self):
        rows,result=run(8)
        self.assertGreater(result['conditions']['active_dual']['mean_accuracy_with_abstention'],.90)
    def test_passive_single_not_identifiable(self):
        _,r=run(8)
        self.assertEqual(r['conditions']['passive_single']['fraction_resolved'],0)

if __name__=='__main__':unittest.main()
