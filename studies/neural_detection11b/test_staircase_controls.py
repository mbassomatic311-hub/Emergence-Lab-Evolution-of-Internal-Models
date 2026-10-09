"""Synthetic-only checks of lag information and time splitting."""
import unittest
import numpy as np
import staircase_controls as s

def build():
    rng=np.random.default_rng(9)
    rows=[]
    for i in range(250):
        stim=i%5!=0
        yes=bool(rng.random()<(.7 if stim else .2))
        kind="hit" if stim and yes else "miss" if stim else "fa" if yes else "cr"
        rows.extend([dict(trial_type="stim-adapt",stimamp=str(1+i/10000),confidence=str(rng.uniform(.4,.95))),
                     dict(trial_type=kind),dict(trial_type="conf"),dict(trial_type="conf-resp")])
    return rows

class Tests(unittest.TestCase):
    def test_lag_columns_from_previous_trial(self):
        tr=s.add_staircase_covariates(build())
        self.assertEqual(tr[1]["previous_report"],tr[0]["yes"])
        self.assertEqual(tr[1]["prev_amp"],tr[0]["amp"])
        self.assertEqual(tr[1]["prev_present"],tr[0]["present"])
        self.assertEqual(tr[1]["prev_dose"],tr[0]["dose"])
    def test_time_split_and_shapes(self):
        X,y,c,a,b=s.get_matrices(s.add_staircase_covariates(build()))
        self.assertEqual(X.shape,(250,12))
        self.assertLess(a.max(),b.min())
    def test_models_produce_finite_predictions(self):
        r=s.evaluate(s.add_staircase_covariates(build()))
        self.assertEqual(r["n_train"]+r["n_test"],250)
        self.assertTrue(np.isfinite([v for k,v in r.items() if "logloss" in k or "mse" in k]).all())

if __name__=="__main__":unittest.main()
