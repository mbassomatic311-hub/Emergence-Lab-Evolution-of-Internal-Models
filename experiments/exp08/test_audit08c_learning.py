"""Software invariants for developmental supervised motor-state identifiability audit."""
import unittest
import numpy as np
from audit08c_learning import (generate_data,offline_action_outcome_reference,
    offline_reference_diagnostics, initialize,loss_and_grad,fit,accuracy,
    inputs_for, TrainedEstimator, T)
from world2d import OBS_DIM

class Audit08CTests(unittest.TestCase):
    def test_lifetimes_never_stitched(self):
        x,y,m=generate_data(8,'stable')
        self.assertEqual(x.shape,(8,T,OBS_DIM))
        self.assertTrue(np.all((y>=0)&(y<4)))
        self.assertTrue(np.all(m.sum(axis=1)<=T))
        for seq,mask in zip(x,m):
            death=int(mask.sum())
            self.assertTrue(np.all(mask[:death]))
            self.assertFalse(np.any(mask[death:]))
            self.assertTrue(np.all(seq[death:]==0))

    def test_development_splits_are_separate(self):
        a,_,_=generate_data(4,'train')
        b,_,_=generate_data(4,'shift')
        self.assertFalse(np.array_equal(a,b))

    def test_reproducible_traces(self):
        a=generate_data(3,'shift');b=generate_data(3,'shift')
        for x,y in zip(a,b):self.assertTrue(np.array_equal(x,y))

    def test_parameter_budgets_within_seven_percent(self):
        counts=[]
        for k in ('memoryless','history','recurrent'):
            p=initialize(k,np.random.default_rng(42))
            counts.append(sum(t.size for t in p.values()))
        self.assertEqual(counts,[232,235,220])
        self.assertLess(max(counts)/min(counts),1.07)

    def test_history_access_only_past_and_present(self):
        x,_,_=generate_data(3,'train')
        h=inputs_for('history',x)
        self.assertTrue(np.array_equal(h[:,:,:OBS_DIM],x))
        self.assertTrue(np.all(h[:,0,OBS_DIM:]==0))
        self.assertTrue(np.array_equal(h[:,1:,OBS_DIM:],x[:,:-1]))

    def test_gradients_match_finite_differences(self):
        X,Y,W=generate_data(2,'train')
        X=X[:,:5,:];Y=Y[:,:5];W=W[:,:5]
        for name in ('memoryless','history','recurrent'):
            p=initialize(name,np.random.default_rng(33))
            loss,grad=loss_and_grad(name,p,X,Y,W)
            self.assertTrue(np.isfinite(loss))
            for key in p:
                ix=(0,)*p[key].ndim
                original=p[key][ix]; eps=1e-5
                p[key][ix]=original+eps
                a,_=loss_and_grad(name,p,X,Y,W)
                p[key][ix]=original-eps
                b,_=loss_and_grad(name,p,X,Y,W)
                p[key][ix]=original
                self.assertAlmostEqual(grad[key][ix],(a-b)/(2*eps),places=5,
                    msg=f'{name}.{key}')

    def test_deterministic_training(self):
        X,Y,W=generate_data(6,'train')
        for name in ('memoryless','history','recurrent'):
            a,_=fit(name,X,Y,W,91,epochs=2,batch=3)
            b,_=fit(name,X,Y,W,91,epochs=2,batch=3)
            for k in a:self.assertTrue(np.array_equal(a[k],b[k]))

    def test_offline_evidence_needs_action_copy(self):
        X,Y,W=generate_data(18,'shift')
        r=offline_reference_diagnostics(X,Y,W,seed=85002)
        self.assertGreater(r['intact_accuracy'],.65)
        self.assertGreater(r['intact_accuracy']-r['scrambled_action_copy_accuracy'],.2)

    def test_deployment_controller_no_hidden_mapping_argument(self):
        p=initialize('recurrent',np.random.default_rng(8))
        obs=np.zeros(OBS_DIM);obs[-1]=1;obs[0]=.5
        agent=TrainedEstimator('recurrent',p)
        command=agent.act(obs,np.random.default_rng(3))
        self.assertIn(command,(0,1,2,3))

if __name__=='__main__':unittest.main()
