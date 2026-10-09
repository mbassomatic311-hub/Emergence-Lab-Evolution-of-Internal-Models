"""Synthetic software tests only. NO human EEG analyzed by these tests."""
import unittest
import numpy as np
import pandas as pd
from evaluate import check_data, evaluate, paired_interval

AUDIT={
 'source_doi':'10.18112/openneuro.ds006648.v1.0.0',
 'events_to_stimuli_alignment_verified':True,
 'rating_to_stimuli_alignment_verified':True,
 'eeg_precedes_rating_response':True,
 'preprocessing_train_test_safe':True,
 'auditor_note':'TEST ONLY: synthetic trials are generated with exact known alignment and no EEG processing.'
}

def synthetic(n_subjects=10,n_stimuli=20,seed=44):
    rng=np.random.default_rng(seed)
    rows=[]
    for s in range(n_subjects):
      for t in range(n_stimuli):
        latent=rng.normal()
        obs=rng.normal(0,.1,12)
        obs[:4]+=latent
        rating=float(np.clip(4.+.9*latent+rng.normal(0,.5),1,7))
        row=dict(subject_id=f'sub-{s:02d}',trial_id=str(t),stimulus_id=f'stim-{t:02d}',vividness_rating=rating)
        row.update({f'eeg_{i:02d}':z for i,z in enumerate(obs)})
        rows.append(row)
    return pd.DataFrame(rows)

class Tests(unittest.TestCase):
    def test_missing_audit_fails(self):
        with self.assertRaisesRegex(ValueError,'Audit gate'):check_data(synthetic(),{**AUDIT,'rating_to_stimuli_alignment_verified':False})
    def test_missing_rating_fails(self):
        df=synthetic();df.loc[0,'vividness_rating']=np.nan
        with self.assertRaisesRegex(ValueError,'Missing required'):check_data(df,AUDIT)
    def test_duplicate_subject_trials_fail(self):
        df=synthetic();df.loc[0,'trial_id']=df.loc[1,'trial_id']
        with self.assertRaisesRegex(ValueError,'Repeated'):check_data(df,AUDIT)
    def test_reproducible_predictions(self):
        df=synthetic()
        a,p,s=evaluate(df,AUDIT);b,q,t=evaluate(df,AUDIT)
        pd.testing.assert_frame_equal(a,b)
        pd.testing.assert_frame_equal(p,q)
        self.assertEqual(s,t)
    def test_each_subject_prediction_only_once_per_model(self):
        df=synthetic();a,p,s=evaluate(df,AUDIT)
        self.assertEqual(len(a),len(df)*6)
        self.assertEqual(len(p),df.subject_id.nunique()*6)
        self.assertEqual(set(a.model.unique()),set(s))
    def test_paired_bootstrap_reports_subjects_not_trials(self):
        df=synthetic();_,per,_=evaluate(df,AUDIT)
        c=paired_interval(per,'pca4_eeg_stimulus',B=40)
        self.assertEqual(c['n_subjects'],10)
    def test_held_out_rating_cannot_change_own_fold_predictions(self):
        df=synthetic()
        before,_,_=evaluate(df,AUDIT)
        changed=df.copy()
        changed.loc[changed.subject_id=='sub-00','vividness_rating']=1.0
        after,_,_=evaluate(changed,AUDIT)
        left=before[before.subject_id=='sub-00'][['model','trial_id','predicted']].reset_index(drop=True)
        right=after[after.subject_id=='sub-00'][['model','trial_id','predicted']].reset_index(drop=True)
        pd.testing.assert_frame_equal(left,right)

    def test_unseen_stimulus_unseen_subject(self):
        df=synthetic();df['stimulus_id']=df.subject_id+df.stimulus_id
        a,_,_=evaluate(df,AUDIT)
        self.assertEqual(len(a),len(df)*6)

if __name__=='__main__':unittest.main()
