"""Deterministic invariant checks. Pass/fail does not imply ecological validity."""
import unittest
import numpy as np
from world2d import World,WorldConfig,OBS_DIM,ACT
from controllers import random_genome,mutate,NeuralController,RandomController,ComparatorController,BayesianController
from engine import simulate,train_population,DEV_SEEDS

class WorldTests(unittest.TestCase):
    def test_observation_has_no_true_rotation_or_absolute_position(self):
        w=World(10,WorldConfig())
        a=w.observe()
        self.assertEqual(a.shape,(OBS_DIM,))
        self.assertTrue(np.all(np.isfinite(a)))
        self.assertNotEqual(len(a),len(np.r_[w.pos,w.rotation]))
    def test_determinism(self):
        a=simulate(RandomController(),12345,'shift+dropout')
        b=simulate(RandomController(),12345,'shift+dropout')
        self.assertEqual(a,b)
        a=simulate(ComparatorController(),12345,'shift+dropout')
        b=simulate(ComparatorController(),12345,'shift+dropout')
        self.assertEqual(a,b)
    def test_motor_rotation_changes_effect_on_reversal(self):
        c=WorldConfig(blockers=0,hazard_slip=0,gust_probability=0,reversal=True,steps=4)
        w=World(7,c);w.rotation=0
        old=w.pos.copy()
        w.step(0);self.assertTrue(np.array_equal(w.pos, old+ACT[0]))
        w.step(0);self.assertTrue(np.array_equal(w.pos,old+2*ACT[0]))
        w.step(0);self.assertTrue(np.array_equal(w.pos,old+2*ACT[0]+ACT[2]))
    def test_fresh_genomes_have_no_recurrent_edges(self):
        g=random_genome(np.random.default_rng(1))
        self.assertEqual(np.count_nonzero(g[1]),0)
    def test_mutations_can_create_recurrent_edges(self):
        rng=np.random.default_rng(7)
        g=random_genome(rng)
        for i in range(40): g=mutate(rng,g)
        self.assertGreater(np.count_nonzero(g[1]),0)
    def test_recurrent_off_ignores_incoming_hidden_feedback(self):
        rng=np.random.default_rng(4)
        g=random_genome(rng)
        g2=(g[0].copy(),np.ones_like(g[1],dtype=bool))
        a=NeuralController(g2,recurrent=False)
        b=NeuralController(g,recurrent=False)
        w=World(3,WorldConfig())
        for _ in range(3):
            obs=w.observe()
            self.assertEqual(a.act(obs,np.random.default_rng(1)),b.act(obs,np.random.default_rng(1)))
            w.step(0)
    def test_comparator_better_than_random_on_one_dev_seed(self):
        good=np.mean([simulate(ComparatorController(),4000+i)[0] for i in range(16)])
        poor=np.mean([simulate(RandomController(),4000+i)[0] for i in range(16)])
        self.assertGreater(good,poor)
    def test_bayesian_controller_repeatability(self):
        self.assertEqual(simulate(BayesianController(),7340,'shift+dropout'),simulate(BayesianController(),7340,'shift+dropout'))
    def test_bayesian_beats_random_on_development_distribution(self):
        seeds=range(7400,7415)
        b=np.mean([simulate(BayesianController(),k,'shift+dropout')[0] for k in seeds])
        r=np.mean([simulate(RandomController(),k,'shift+dropout')[0] for k in seeds])
        self.assertGreater(b,r)
    def test_separate_development_seed_ids(self):
        self.assertEqual(len(set(DEV_SEEDS)),len(DEV_SEEDS))
        self.assertTrue(all(x<10000 for x in DEV_SEEDS))

if __name__=='__main__':unittest.main()
