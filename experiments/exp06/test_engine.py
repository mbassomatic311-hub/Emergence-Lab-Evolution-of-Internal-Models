import unittest
import numpy as np
from dataclasses import replace
from engine import *

class Tests(unittest.TestCase):
 def test_theoretical_upper_bound(self):
  self.assertAlmostEqual(analytic_bound(.92),.21,places=12)
  self.assertAlmostEqual(analytic_bound(.5),0,places=12)
 def test_no_environment_signal(self):
  rng=np.random.default_rng(42); c=Settings(population=17)
  p,r,m=initialize(rng,c)
  # Even with arbitrary recurrence no payoff is possible when source is unrelated.
  r=rng.normal(size=r.shape);m[:]=True
  self.assertTrue(np.allclose(expected_payoff(p,r,m,q=.5,recurrent_cost=0),0,atol=1e-12))
 def test_without_history(self):
  rng=np.random.default_rng(43); c=Settings(population=17)
  p,r,m=initialize(rng,c)
  r=rng.normal(size=r.shape);m[:]=True
  self.assertTrue(np.allclose(expected_payoff(p,r,m,q=.92,retained=False),0,atol=1e-12))
 def test_initially_no_recurrence(self):
  p,r,m=initialize(np.random.default_rng(54),Settings())
  self.assertEqual(int(m.sum()),0)
 def test_reproducible(self):
  c=Settings(population=40,generations=10)
  a=evolve(77,c); b=evolve(77,c)
  self.assertTrue(np.array_equal(a['plain'],b['plain']))
  self.assertTrue(np.array_equal(a['rec'],b['rec']))
  self.assertTrue(np.array_equal(a['mask'],b['mask']))
 def test_heldout_generator_is_independent(self):
  c=Settings(population=40,generations=10)
  a=evolve(1,c)
  d=test_agent(a,.92,833,N=1000)
  self.assertEqual(len(d['source']),1000)
  self.assertTrue(np.all(np.isin(d['event'],[-1,1])))

if __name__=='__main__':unittest.main(verbosity=2)
