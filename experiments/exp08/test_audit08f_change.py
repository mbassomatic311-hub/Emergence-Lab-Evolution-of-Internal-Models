"""Scientific invariants for Experiment 08F developmental change detection."""
import unittest
import numpy as np
from audit08f_change import ActionPredictor,probe,navigate,valid_displacement,phase,run

class ChangeModelTests(unittest.TestCase):
    def test_initially_blank(self):
        m=ActionPredictor('slow')
        self.assertTrue(np.all(m.vectors==0))
        self.assertTrue(np.all(m.counts==0))
    def test_models_deterministic(self):
        for mode in ('slow','fast','adaptive_gain','surprise_reset','memoryless'):
            self.assertEqual(probe(31000001,mode)[0],probe(31000001,mode)[0])
    def test_open_loop_same_physical_observation_counts(self):
        # Valid-event counts should match for every estimator in each seeded world.
        lengths=[len(probe(31000001,m)[0]) for m in ('slow','fast','adaptive_gain','surprise_reset','memoryless')]
        self.assertEqual(len(set(lengths)),1)
    def test_ablation_update(self):
        m=ActionPredictor('memoryless')
        for i in range(12):m.observe_effect(0,[1.,0.],i)
        self.assertTrue(np.all(m.vectors==0))
    def test_update_on_active_action_only(self):
        m=ActionPredictor('slow')
        m.observe_effect(2,[1.,0.],1)
        self.assertTrue(np.all(m.vectors[[0,1,3]]==0))
        self.assertAlmostEqual(m.vectors[2,0],.25)
    def test_no_oracle_reversal_step(self):
        # Predictor receives only action and measured displacement, not phase or rotation.
        m=ActionPredictor('adaptive_gain')
        m.observe_effect(0,[1.,0.],12)
        self.assertEqual(m.counts[0],1)
    def test_reset_requires_two_surprises(self):
        m=ActionPredictor('surprise_reset')
        for i in range(8):m.observe_effect(i%4,[1.,0.],i)
        self.assertEqual(m.alarms,0)
        m.observe_effect(0,[-2.,0.],9)
        self.assertEqual(m.alarms,0)
        m.observe_effect(1,[-2.,0.],10)
        self.assertEqual(m.alarms,1)
        self.assertTrue(np.all(m.counts[:1]==0))
    def test_prediction_is_prequential(self):
        m=ActionPredictor('slow')
        p=m.predict(3)
        m.observe_effect(3,[0.,1.],1)
        self.assertTrue(np.array_equal(p,np.zeros(2)))
        self.assertFalse(np.array_equal(p,m.predict(3)))
    def test_valid_flags(self):
        a=np.zeros(14);b=np.zeros(14)
        a[-1]=b[-1]=1
        self.assertTrue(valid_displacement(a,b))
        b[-3]=1
        self.assertFalse(valid_displacement(a,b))
        b[-3]=0;b[-2]=1
        self.assertFalse(valid_displacement(a,b))
    def test_post_change_phase(self):
        self.assertEqual(phase(24),'before_change')
        self.assertEqual(phase(25),'after_change_early')
        self.assertEqual(phase(33),'after_change_late')
    def test_pair_world_seed(self):
        rows=probe(31000000,'fast',True)[0]
        self.assertTrue(all(1<=r['t']<48 for r in rows))
        self.assertTrue(all(r['squared_error']>=0 for r in rows))
    def test_navigation_valid(self):
        for k in ('slow','fast','adaptive_gain','surprise_reset','memoryless','greedy','comparator','bayesian'):
            r=navigate(31000000,k)
            self.assertGreaterEqual(r['food'],0)
            self.assertTrue(0<=r['fraction_alive']<=1)
    def test_stable_and_shifted_worlds_match_before_intervention(self):
        x,_=probe(31000000,'slow',shifted=True)
        y,_=probe(31000000,'slow',shifted=False)
        x=[(r['t'],r['squared_error']) for r in x if r['t']<=24]
        y=[(r['t'],r['squared_error']) for r in y if r['t']<=24]
        self.assertEqual(x,y)
    def test_alarm_timestamp_does_not_determine_decision(self):
        x=ActionPredictor('surprise_reset')
        y=ActionPredictor('surprise_reset')
        for i in range(12):
            data=[1.,0.] if i < 8 else [-2.,0.]
            x.observe_effect(i%4,data,i)
            y.observe_effect(i%4,data,i+1000)
        self.assertTrue(np.array_equal(x.vectors,y.vectors))
        self.assertEqual(x.alarms,y.alarms)
    def test_study_units(self):
        events,alarms,nav,summary=run(1,include_navigation=False)
        self.assertEqual(summary['n_independent_seed_worlds'],6)
        self.assertEqual(len(alarms),6*2*5)
        self.assertFalse(nav)
        self.assertGreater(len(events),0)

if __name__=='__main__':unittest.main()
