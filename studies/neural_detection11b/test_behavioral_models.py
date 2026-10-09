"""Synthetic fixtures only. Human behavioral data are fetched ONLY by behavioral_models.py."""
import unittest
import numpy as np
from behavioral_models import extract_trials,add_histories,matrices,fit_score,boot_contrast

def item(kind,confidence="0.8",amp="1.0",idx=0):
    return dict(trial_type=kind,confidence=confidence,stimamp=amp,onset=str(idx))

def sample():
    rng=np.random.default_rng(104)
    rows=[]
    for i in range(250):
        present=bool(i%5)
        yes=int((rng.random() <(.72 if present else .1)))
        kind="hit" if present and yes else "miss" if present else "fa" if yes else "cr"
        c=str(round(.6+rng.random()*.35,3))
        rows.extend([item("stim-adapt",c,idx=i),item(kind,c,idx=i),
                     item("conf",c,idx=i),item("conf-resp",c,idx=i)])
    return rows

class Tests(unittest.TestCase):
    def test_trial_detection_mapping(self):
        rows=[item("stim-adapt"),item("hit"),item("conf"),item("conf-resp"),
              item("stim-adapt"),item("cr"),item("conf"),item("conf-resp")]
        a=extract_trials(rows)
        self.assertEqual(len(a),2)
        self.assertEqual((a[0]["present"],a[0]["yes"]),(1.,1.))
        self.assertEqual((a[1]["present"],a[1]["yes"]),(0.,0.))
    def test_missing_outcome_not_guessed(self):
        rows=[item("stim-adapt"),item("conf"),item("conf-resp")]
        self.assertFalse(extract_trials(rows)[0]["valid"])
    def test_future_never_used_in_first_history(self):
        s=add_histories(extract_trials(sample()))
        self.assertEqual(s[0]["previous_report"],.5)
        self.assertEqual(s[1]["previous_report"],s[0]["yes"])
    def test_time_forward_split(self):
        _,_,_,_,train,test=matrices(extract_trials(sample()))
        self.assertLess(int(np.max(train)),int(np.min(test)))
    def test_behavioral_prediction_reproducible(self):
        a=fit_score(extract_trials(sample()))
        b=fit_score(extract_trials(sample()))
        self.assertEqual(a,b)
        self.assertGreater(a["n_train"],100)
    def test_participant_not_trial_bootstrap(self):
        rows=[{"A":.3,"B":.2},{"A":.1,"B":.4}]
        z=boot_contrast(rows,"A","B",B=50)
        self.assertEqual(z["number_of_independent_participants"],2)
    def test_no_eeg_predictor(self):
        x=extract_trials(sample())
        self.assertTrue(all(not any(k.startswith("eeg") for k in t) for t in x))
if __name__=="__main__":unittest.main()
