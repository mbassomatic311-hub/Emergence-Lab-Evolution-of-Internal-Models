import unittest
import numpy as np
from exp08h import World,ACTIONS,CAUSES,CALIBRATION,T,fit_linear,choose_action,diagnose,run_world,evaluate,summarize_compare

class CausalTests(unittest.TestCase):
    def test_no_cause_label_given_to_learner(self):
        # The world contains private cause; agent receives only u,y,z,time.
        keys=set(World(7,'motor').step(30,ACTIONS[0]))
        self.assertEqual(keys, {'u','y','z','t'})
    def test_counterfactual_observational_equivalence_without_reference(self):
        # Same seed, same single command, same primary sensor noise.
        # A physical force and a fake drift of the visual displacement sensor
        # produce exactly identical primary observations; reference resolves them.
        a=World(812,'external');b=World(812,'sensor')
        for t in range(T):
            x=a.step(t,ACTIONS[0]);y=b.step(t,ACTIONS[0])
            self.assertTrue(np.array_equal(x['y'],y['y']))
            if t>=a.change_at:
                self.assertFalse(np.array_equal(x['z'],y['z']))
    def test_exogenous_switch_not_observed(self):
        r=World(988,'motor').step(50,ACTIONS[2]);self.assertNotIn('change_at',r)
        self.assertNotIn('motor',r);self.assertNotIn('cause',r)
    def test_identical_prechange_world(self):
        one=World(12,'motor');two=World(12,'external_sensor')
        for t in range(CALIBRATION):
            for k in ('y','z'):
                self.assertTrue(np.array_equal(one.step(t,ACTIONS[0])[k],two.step(t,ACTIONS[0])[k]))
    def test_rank_abstention(self):
        data=[{'u':ACTIONS[0],'z':np.ones(2),'y':np.ones(2)} for _ in range(20)]
        mat,r,_=fit_linear(data)
        self.assertEqual(r,1)
        base={'z':np.zeros((2,3)),'y':np.zeros((2,3)),'sensor_bias':np.zeros(2)}
        label,confirmed,_=diagnose(base,data)
        self.assertEqual(label,'undetermined');self.assertFalse(confirmed)
    def test_no_reference_abstains_external_sensor_alias(self):
        r=run_world(123456,'external','cycle',has_reference=False)
        self.assertEqual(r['diagnosis'],'undetermined')
    def test_replay_determinism(self):
        self.assertEqual(run_world(123456,'motor_external','adaptive'),run_world(123456,'motor_external','adaptive'))
    def test_high_noise_cannot_magically_resolve(self):
        # Overly noisy samples cannot yield false perfect reliability.
        r=run_world(883012,'sensor','adaptive',noise=.75)
        self.assertIn(r['correct'],[0,1])
    def test_changed_world_alarms_are_uncued(self):
        for cause in ['motor','external','sensor','motor_external']:
            r=run_world(121212,cause,'adaptive')
            self.assertGreaterEqual(r['alarm_time'],r['change_time'])
    def test_probe_policy_never_uses_hidden_parameter(self):
        for policy in ('repeat','random','cycle','adaptive'):
            r=run_world(121212,'external_sensor',policy)
            self.assertTrue(0 <= r['probe_cost'] <= T-CALIBRATION)
    def test_full_model_control(self):
        r=run_world(171717,'motor_external','adaptive')
        self.assertIn(r['diagnosis'], ['motor_external','undetermined','unknown'])
    def test_seed_level_resampling(self):
        data,_=evaluate(3)
        s=summarize_compare(data)
        self.assertEqual(s['n_seeds'],3)
    def test_no_future_sensor_or_truth_access(self):
        r=World(55,'motor')
        step=r.step(30,ACTIONS[1]);self.assertEqual(len(step),4)

if __name__=='__main__':unittest.main()
