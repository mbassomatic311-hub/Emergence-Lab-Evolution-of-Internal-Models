"""Core invariants for the developmental nonlinear environment and predictors."""
import unittest
import numpy as np
from experiment08i import (ACTIONS,CAUSES,MODELS,NonlinearWorld,OnlineRLS,KNNPredictor,features,
                           run_world,bootstrap_paired,TOTAL)
class WorldTests(unittest.TestCase):
    def test_seed_determinism(self):
        for cause in CAUSES:
            a,b=NonlinearWorld(9_100_001,cause),NonlinearWorld(9_100_001,cause)
            self.assertTrue(np.array_equal(a.begin(),b.begin()))
            for i in range(20):
                y,z=a.step(i%5);Y,Z=b.step(i%5)
                self.assertTrue(np.array_equal(y,Y))
                self.assertTrue(np.array_equal(z,Z))
    def test_no_privileged_change_cue_in_observation(self):
        a=NonlinearWorld(9_100_001,'motor');b=NonlinearWorld(9_100_001,'none')
        np.testing.assert_array_equal(a.begin(),b.begin())
        for t in range(min(a.change_at,b.change_at)):
            y,z=a.step(t%5);Y,Z=b.step(t%5)
            np.testing.assert_array_equal(y,Y)
            np.testing.assert_array_equal(z,Z)
    def test_sensor_only_shift_does_not_change_inertial_motion(self):
        a=NonlinearWorld(9_100_001,'sensor');b=NonlinearWorld(9_100_001,'none')
        for t in range(TOTAL):
            _,z=a.step(t%5);_,Z=b.step(t%5)
            np.testing.assert_array_equal(z,Z)
    def test_motor_shift_changes_inertial_motion(self):
        a=NonlinearWorld(9_100_001,'motor');b=NonlinearWorld(9_100_001,'none')
        differs=False
        for t in range(TOTAL):
            _,z=a.step((t%4)+1);_,Z=b.step((t%4)+1)
            if t>=a.change_at and not np.allclose(z,Z):differs=True
        self.assertTrue(differs)
    def test_reference_off(self):
        w=NonlinearWorld(9_100_001,'external',reference=False)
        w.begin();_,z=w.step(1);self.assertIsNone(z)
    def test_actions_are_validated(self):
        w=NonlinearWorld(9_100_001,'none')
        with self.assertRaises(ValueError):w.step(5)
    def test_trajectory_has_no_learning_feedback(self):
        a,_=run_world(9_100_001,'motor','cycle')
        b,_=run_world(9_100_001,'motor','cycle')
        self.assertEqual(a,b)
    def test_prequential_scores_nonnegative(self):
        r,_=run_world(9_100_001,'motor','random')
        self.assertEqual(len(r),len(MODELS)*(35+19+35+5))
        self.assertTrue(all(x['range_sqerr']>=0 for x in r))
    def test_feature_length(self):
        for x in MODELS:
            if x.startswith('knn_'): continue
            p=OnlineRLS(x)
            self.assertEqual(len(features(x,np.ones(4)*7,ACTIONS[0])),len(p.w))
    def test_action_blind_feature_not_changed_by_motor_command(self):
        ranges=np.array([2.,3.,4.,5.])
        np.testing.assert_array_equal(features('action_blind',ranges,ACTIONS[0]),features('action_blind',ranges,ACTIONS[4]))
    def test_counterfactual_probe_does_not_change_main_trajectory(self):
        a=NonlinearWorld(9_100_001,'motor');b=NonlinearWorld(9_100_001,'motor')
        for t in range(TOTAL):
            if t==120:
                import copy
                alt=copy.deepcopy(a)
                alt.step(4)
            ya,za=a.step(t%5);yb,zb=b.step(t%5)
            np.testing.assert_array_equal(ya,yb)
            np.testing.assert_array_equal(za,zb)
    def test_knn_does_not_use_hidden_labels(self):
        model=KNNPredictor('knn_recent')
        u=ACTIONS[1];r=np.array([3.,4.,5.,6.]);out=np.array([1.,2.,3.,4.,5.,6.])
        np.testing.assert_array_equal(model.predict(r,u),np.zeros(6))
        model.update(r,u,out)
        np.testing.assert_allclose(model.predict(r,u),out)
        np.testing.assert_array_equal(model.predict(r,ACTIONS[2]),np.zeros(6))
    def test_no_reference_predictor_score_still_works(self):
        r,_=run_world(9_100_001,'sensor','cycle',reference=False)
        self.assertTrue(all(x['inertial_sqerr'] is None for x in r))
if __name__=='__main__':unittest.main()
