import unittest
import numpy as np
from world2d import World,WorldConfig,ACT
from audit_world_controls import oracle_action,oracle_rollout

class WorldAuditTests(unittest.TestCase):
    def test_no_direct_motor_rotation_leak_to_sensor(self):
        c=WorldConfig(blockers=0,observation_noise=0,hazard_slip=0,gust_probability=0)
        a,b=World(123,c),World(123,c)
        b.rotation=(a.rotation+1)%4
        np.testing.assert_array_equal(a.observe(),b.observe())
        # Only after a command can the different action effect reveal mapping.
        a.step(0);b.step(0)
        self.assertFalse(np.array_equal(a.pos,b.pos))
    def test_no_absolute_coordinate_leak_given_same_local_input(self):
        c=WorldConfig(blockers=0,observation_noise=0,hazard_slip=0,gust_probability=0)
        a,b=World(442,c),World(442,c)
        # Two interior positions and targets, same relative displacement;
        # same local collision flags, energy and RNG state.
        a.pos=np.array([4,4],dtype=np.int16);a.target=np.array([6,6],dtype=np.int16)
        b.pos=np.array([7,7],dtype=np.int16);b.target=np.array([9,9],dtype=np.int16)
        np.testing.assert_array_equal(a.observe(),b.observe())
    def test_dropout_flag_and_bearing(self):
        a=World(101,WorldConfig(dropout_probability=1.,blockers=0))
        obs=a.observe()
        self.assertEqual(obs[-1],0)
        np.testing.assert_array_equal(obs[:2],[0,0])
    def test_food_is_not_coincident_with_start(self):
        for seed in (11,13,17,31):
            w=World(seed,WorldConfig())
            self.assertNotEqual(tuple(w.pos),tuple(w.target))
            self.assertFalse(w._blocked(w.target))
    def test_oracle_action_with_ideal_physics(self):
        c=WorldConfig(blockers=0,hazard_slip=0,gust_probability=0,reversal=False)
        w=World(99,c)
        old_dist=np.abs(w.target-w.pos).sum()
        w.step(oracle_action(w))
        self.assertEqual(np.abs(w.target-w.pos).sum(), old_dist-1)
    def test_privileged_reference_repeatable(self):
        a=oracle_rollout(1200,'shift+dropout')
        b=oracle_rollout(1200,'shift+dropout')
        self.assertEqual(a,b)
if __name__=='__main__':unittest.main()
