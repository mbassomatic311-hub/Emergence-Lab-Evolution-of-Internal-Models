import unittest, numpy as np
from engine07 import episodes, init_pop, train_one, evaluate
class EngineTests(unittest.TestCase):
    def test_repeatability(self):
        p=init_pop(np.random.default_rng(9),7)
        a=episodes(p,np.random.default_rng(8),2,True,'full')
        b=episodes(p,np.random.default_rng(8),2,True,'full')
        self.assertTrue(np.array_equal(a[0],b[0]));self.assertTrue(np.array_equal(a[1],b[1]))
    def test_shapes(self):
        p=init_pop(np.random.default_rng(9),9)
        food, survival=episodes(p,np.random.default_rng(4),1)
        self.assertEqual(food.shape,(9,));self.assertEqual(survival.shape,(9,))
        self.assertTrue(np.all((survival>=0)&(survival<=1)))
        self.assertTrue(np.all(food>=0))
    def test_reactive_makes_memory_weights_irrelevant(self):
        p=init_pop(np.random.default_rng(9),5)
        changed=p.copy(); changed[:,:4]=100; changed[:,5:7]=100
        a=episodes(p,np.random.default_rng(3),1,False,'reactive')
        b=episodes(changed,np.random.default_rng(3),1,False,'reactive')
        self.assertTrue(np.array_equal(a[0],b[0]))
    def test_test_environment_differs(self):
        p=np.tile([0,0.2,5,0,0.2,5,0,0],(10,1)).astype(float)
        a=episodes(p,np.random.default_rng(3),2,False,'full')
        b=episodes(p,np.random.default_rng(3),2,True,'full')
        self.assertTrue(np.any(a[0]!=b[0]))
    def test_sensor_scramble_intervenes(self):
        p=init_pop(np.random.default_rng(9),20)
        p[:,2]=4; p[:,5]=5;p[:,4]=0
        a=episodes(p,np.random.default_rng(3),2,True,'full')
        b=episodes(p,np.random.default_rng(3),2,True,'scrambled')
        self.assertTrue(np.any(a[0]!=b[0]))
if __name__=='__main__':unittest.main()
