"""Tests for the developmental 08E *unlabeled* prediction/control pilot."""
import inspect
import unittest
import numpy as np
from world2d import World,WorldConfig
from audit08e_selfsupervised import OnlineSensorimotor,open_loop_probe,run_episode,study,DEV_BASE

class Test08ESelfSupervision(unittest.TestCase):
    def test_exact_reproducibility(self):
        for variant in ('action_model','shuffled_action','action_blind','reset_memory'):
            a=open_loop_probe(23001103,kind=variant)
            b=open_loop_probe(23001103,kind=variant)
            self.assertEqual(a,b)
            c=run_episode(23001003,variant)
            d=run_episode(23001003,variant)
            self.assertEqual(c,d)

    def test_no_hidden_world_state_in_agent(self):
        # Deliberately limit online policy to the public vector passed to act().
        src=inspect.getsource(OnlineSensorimotor)
        for forbidden in ('world.rotation','world.pos','world.blocked','world.target','world._last_obs'):
            self.assertNotIn(forbidden,src)
        agent=OnlineSensorimotor()
        obs=np.zeros(14);obs[-1]=1;obs[:2]=[.7,-.2]
        self.assertIn(agent.act(obs,np.random.default_rng(1)),range(4))

    def test_starts_without_motor_mapping(self):
        a=OnlineSensorimotor('action_model')
        self.assertTrue(np.all(a.vectors==0.))
        self.assertTrue(np.all(a.counts==0))

    def test_supervision_is_prediction_error_from_observations(self):
        a=OnlineSensorimotor('action_model',learning_rate=1.,epsilon=0)
        rng=np.random.default_rng(5)
        old=np.zeros(14);old[:2]=[.5,.5];old[-1]=1
        a.act(old,rng)
        previous_cmd=a.last_action
        obs=old.copy();obs[:2]=old[:2]-np.array([1.,0.])/6
        a.act(obs,rng)
        self.assertTrue(np.allclose(a.vectors[previous_cmd],[1.,0.]))
        self.assertEqual(a.n_valid,1)

    def test_food_respawn_prevents_spurious_update(self):
        a=OnlineSensorimotor('action_model')
        rng=np.random.default_rng(5)
        old=np.zeros(14);old[:2]=[.2,.6];old[-1]=1
        a.act(old,rng)
        obs=old.copy();obs[:2]=[-.6,-.4];obs[-3]=1
        a.act(obs,rng)
        self.assertEqual(a.n_valid,0)
        self.assertEqual(a.counts.sum(),0)

    def test_collision_and_dropout_block_update(self):
        for mode in ('collision','dropout'):
            a=OnlineSensorimotor('action_model')
            rng=np.random.default_rng(5)
            old=np.zeros(14);old[:2]=[.2,.6];old[-1]=1
            a.act(old,rng)
            obs=old.copy();obs[:2]=[.1,.4]
            if mode=='collision':obs[-2]=1
            else:obs[-1]=0
            a.act(obs,rng)
            self.assertEqual(a.n_valid,0)

    def test_actions_have_same_open_loop_physics(self):
        seed=23001103
        results=[open_loop_probe(seed,kind=x) for x in ('action_model','shuffled_action','action_blind','reset_memory')]
        for r in results[1:]:
            self.assertEqual(r['n_valid'],results[0]['n_valid'])
            self.assertEqual([x['t'] for x in r['events']],[x['t'] for x in results[0]['events']])
        self.assertGreater(results[0]['n_valid'],5)

    def test_action_permutation_effect_in_fixed_world(self):
        r=open_loop_probe(23001103,kind='action_model')
        s=open_loop_probe(23001103,kind='shuffled_action')
        self.assertNotEqual(r['pre_mse'],s['pre_mse'])

    def test_mutually_disjoint_development_seed_blocks(self):
        self.assertEqual(len(DEV_BASE),len(set(DEV_BASE)))
        self.assertTrue(all(x>20_000_000 for x in DEV_BASE))

    def test_study_summary_shape(self):
        probes,nav,result=study(seeds_per_group=1,nav_per_group=1)
        self.assertEqual(len(probes),6*4)
        self.assertEqual(len(nav),6*2*7)
        self.assertIn('action_model',result['probe'])
        self.assertNotIn('consciousness_measure',result)

if __name__=='__main__':unittest.main()
