"""Development invariants; testing the code is not testing consciousness."""
import unittest
import numpy as np
from study10 import (world_parameters,generate,fit_world,feature_maps,make_features,
                     paired_bootstrap,REGULARIZATIONS,MODEL_NAMES)

class TestStudy10(unittest.TestCase):
    def test_observations_have_correct_shape(self):
        for scenario in ('shared','independent'):
            x,a,y=generate(310007,scenario,21,1)
            self.assertEqual(x.shape,(21,48));self.assertEqual(a.shape,(21,2));self.assertEqual(y.shape,(21,48))
    def test_determinism(self):
        for first,second in zip(generate(310007,'shared',15,3),generate(310007,'shared',15,3)):
            np.testing.assert_array_equal(first,second)
    def test_train_test_rng_independence(self):
        for a,b in zip(generate(310007,'shared',15,1),generate(310007,'shared',15,2)):
            self.assertFalse(np.array_equal(a,b))
    def test_actual_shared_mechanism(self):
        _,_,W=world_parameters(310007,'shared')
        self.assertEqual(np.linalg.matrix_rank(W),3)
    def test_private_mechanism(self):
        _,_,W=world_parameters(310007,'independent')
        self.assertEqual(np.linalg.matrix_rank(W),9)
        self.assertTrue(np.all(W[:16,3:]==0))
    def test_projection_budgets_match(self):
        x=np.random.default_rng(200).normal(size=(60,48))
        for name in ('joint_pca4','split_pca4','random_projection4'):
            P=feature_maps(x,name,310007)
            self.assertEqual(P.shape,(48,4))
            np.testing.assert_allclose(P.T@P,np.eye(4),atol=1e-12)
    def test_observer_sees_no_hidden_state(self):
        rows=fit_world(310007,'shared',120,False)
        self.assertEqual(set(r['model'] for r in rows),set(MODEL_NAMES))
        self.assertEqual(rows[0]['feature_dimensions_excluding_bias'],2)
    def test_corruption_changes_scores(self):
        a=fit_world(310007,'shared',120,False)
        b=fit_world(310007,'shared',120,True)
        self.assertTrue(any(abs(x['mse']-y['mse'])>0.0001 for x,y in zip(a,b)))
    def test_bootstrap(self):
        d=paired_bootstrap([1.,2.,3.],[0.,0.,0.])
        self.assertEqual(d['mean_difference'],2.)
        self.assertTrue(d['ci95'][0]>=1 and d['ci95'][1]<=3)
    def test_training_uses_only_train_pca(self):
        x=np.random.default_rng(200).normal(size=(30,48))
        y=x.copy();y[0,0]+=100.
        self.assertFalse(np.allclose(feature_maps(x,'joint_pca4',310007),feature_maps(y,'joint_pca4',310007)))
    def test_validation_alpha_choices(self):
        rows=fit_world(310007,'independent',120,False)
        self.assertTrue(all(r['ridge_alpha'] in REGULARIZATIONS for r in rows))

if __name__=='__main__':unittest.main()
