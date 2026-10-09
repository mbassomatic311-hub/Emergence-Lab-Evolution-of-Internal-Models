"""Development-only invariants for action-selection and counterfactual evaluation."""
import unittest
import numpy as np
from experiment08j import (ACTIONS,CAUSES,TOTAL,PROBE_STEPS,TEST_TIMES,
                           fixed_test_battery,train_one,policy_action,run,score_model)
from experiment08i import OnlineRLS

class TestActiveProbing(unittest.TestCase):
    def test_deterministic_battery(self):
        a=fixed_test_battery(11800041,'motor',.025)
        b=fixed_test_battery(11800041,'motor',.025)
        self.assertEqual(len(a),len(TEST_TIMES))
        for (_,x,z),(_,y,w) in zip(a,b):
            np.testing.assert_array_equal(x,y)
            for (ac,out),(bc,oo) in zip(z,w):
                self.assertEqual(ac,bc)
                np.testing.assert_array_equal(out,oo)
    def test_missing_hidden_labels(self):
        model=OnlineRLS('nonlinear')
        rng=np.random.default_rng(1)
        a=policy_action('uncertainty',0,model,np.ones(4)*6.,np.zeros(5,int),rng)
        self.assertIn(a,(1,2,3,4))
    def test_budget_and_actions(self):
        for policy in ('uncertainty','random','cycle','least_seen','single_action','no_probes'):
            _,_,x=train_one(11800041,'motor',policy)
            self.assertEqual(len(x['action_trace']),TOTAL)
            expected=0 if policy=='no_probes' else len(PROBE_STEPS)
            self.assertEqual(x['nonzero_probes'],expected)
            self.assertTrue(all(0<=a<=4 for a in x['action_trace']))
            self.assertTrue(all((a!=0)==(t in PROBE_STEPS and policy!='no_probes') for t,a in enumerate(x['action_trace'])))
    def test_cycle_uses_all_actions(self):
        _,_,metrics=train_one(11800041,'sensor','cycle')
        self.assertEqual(metrics['distinct_probe_commands'],4)
    def test_single_uses_one_action(self):
        _,_,metrics=train_one(11800041,'sensor','single_action')
        self.assertEqual(metrics['distinct_probe_commands'],1)
    def test_no_probe_learns_on_free_environmental_motion(self):
        _,_,x=train_one(11800041,'external','no_probes')
        self.assertEqual(x['action_counts'][0],TOTAL)
    def test_no_test_outcomes_used_in_training(self):
        a= fixed_test_battery(11800041,'motor_external',.025)
        learner,knn,_=train_one(11800041,'motor_external','random')
        pred_before=learner.w.copy()
        n_before=knn.n
        score_model(learner,a)
        score_model(knn,a)
        np.testing.assert_array_equal(pred_before,learner.w)
        self.assertEqual(n_before,knn.n)
    def test_all_five_action_queries(self):
        battery=fixed_test_battery(11800041,'unknown_nonlinear',.025)
        for _,_,test in battery:
            self.assertEqual([u for u,_ in test],list(range(5)))
    def test_world_reproducibility(self):
        a,b=run(1),run(1)
        self.assertEqual(a,b)
    def test_world_clusters_not_steps(self):
        rows,summary=run(2)
        self.assertEqual(summary['n_seed_clusters'],2)
        self.assertEqual(len(rows),2*len(CAUSES)*6)
    def test_no_probe_when_not_slot(self):
        model=OnlineRLS('nonlinear')
        for t in (1,2,3,4,6,99,149):
            self.assertEqual(policy_action('uncertainty',t,model,np.ones(4)*6.,np.zeros(5,int),np.random.default_rng(2)),0)
    def test_reject_bad_policy(self):
        with self.assertRaises(ValueError):
            policy_action('wrong',0,OnlineRLS('nonlinear'),np.ones(4),np.zeros(5,int),np.random.default_rng(2))

if __name__=='__main__':unittest.main()
