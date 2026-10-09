"""Study 11 DEVELOPMENT-ONLY neural-vividness predictive benchmark.

Input is a verified, explicitly joined trial table; this module NEVER infers
EEG/behavioral alignment from order alone. Not a consciousness measure.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

FIELDS = ('subject_id', 'trial_id', 'stimulus_id', 'vividness_rating')
MODELS = ('stimulus_only','full_eeg_stimulus','pca4_eeg_stimulus','pca8_eeg_stimulus',
          'random4_eeg_stimulus','shuffled4_eeg_stimulus')

def check_data(df: pd.DataFrame, manifest: dict):
    absent = set(FIELDS) - set(df.columns)
    if absent: raise ValueError(f'Missing required columns: {sorted(absent)}')
    eeg_cols = sorted(c for c in df.columns if c.startswith('eeg_'))
    if len(eeg_cols) < 8: raise ValueError('Need >=8 EEG features prefixed eeg_')
    if len(df) < 50 or df['subject_id'].nunique() < 5: raise ValueError('Too few trials/participants')
    if df[list(FIELDS)].isna().any().any() or df[eeg_cols].isna().any().any():
        raise ValueError('Missing required fields / EEG feature: predeclare exclusions')
    if df.duplicated(['subject_id','trial_id']).any(): raise ValueError('Repeated subject/trial keys')
    if not np.isfinite(df[eeg_cols].to_numpy(dtype=float)).all(): raise ValueError('Nonfinite EEG values')
    ratings=pd.to_numeric(df['vividness_rating'],errors='coerce')
    if ratings.isna().any() or not ratings.between(1,7).all():
        raise ValueError('Ratings must be observed 1–7 scale, no missing values')
    mandatory=('source_doi','events_to_stimuli_alignment_verified','rating_to_stimuli_alignment_verified',
               'eeg_precedes_rating_response','preprocessing_train_test_safe','auditor_note')
    if any(k not in manifest for k in mandatory): raise ValueError('Required manifest fields missing')
    for k in mandatory[1:5]:
        if manifest[k] is not True: raise ValueError(f'Audit gate not verified: {k}')
    if manifest['source_doi']!='10.18112/openneuro.ds006648.v1.0.0':
        raise ValueError('Unreviewed data source/version')
    if len(str(manifest['auditor_note']).strip())<30:
        raise ValueError('Describe how trial/stimulus/EEG alignment was verified')
    if df.groupby('subject_id')['stimulus_id'].nunique().lt(10).any():
        raise ValueError('Insufficient unique stimuli for a subject')
    return eeg_cols

def onehot_train(train_stim, test_stim):
    cats=pd.Index(pd.unique(train_stim.astype(str)))
    idx={v:i for i,v in enumerate(cats)}
    a=np.zeros((len(train_stim),len(cats)),float)
    b=np.zeros((len(test_stim),len(cats)),float)
    for i,v in enumerate(train_stim.astype(str)):
        a[i,idx[v]]=1.
    for i,v in enumerate(test_stim.astype(str)):
        if v in idx:b[i,idx[v]]=1.
    return a,b

def eeg_representations(tr_x,te_x,mode,seed=991):
    scaler=StandardScaler()
    a=scaler.fit_transform(tr_x)
    b=scaler.transform(te_x)
    if mode=='full':return a,b
    n=4 if '4' in mode else 8
    if mode.startswith('pca'):
        pca=PCA(n_components=n,svd_solver='full')
        return pca.fit_transform(a),pca.transform(b)
    if mode.startswith('random'):
        rng=np.random.default_rng(seed)
        projection=rng.normal(size=(a.shape[1],n))/np.sqrt(n)
        return a@projection,b@projection
    raise ValueError('unrecognized mode')

def fit_predict(xtr,ytr,xte,alpha=30.):
    reg=Ridge(alpha=alpha,solver='svd')
    reg.fit(xtr,ytr)
    return reg.predict(xte)

def evaluate(df, manifest, folds=5):
    eeg_cols=check_data(df,manifest)
    df=df.sort_values(['subject_id','trial_id']).reset_index(drop=True)
    subjects=df['subject_id'].astype(str).to_numpy()
    groups=GroupKFold(n_splits=min(folds,len(np.unique(subjects))))
    x=df[eeg_cols].to_numpy(dtype=float)
    y=df['vividness_rating'].to_numpy(dtype=float)
    stim=df['stimulus_id'].astype(str).to_numpy()
    predictions=[]
    for fold,(itr,ite) in enumerate(groups.split(x,y,groups=subjects),start=1):
        a,b=onehot_train(stim[itr],stim[ite])
        for model in MODELS:
            if model=='stimulus_only':
                tr,te=a,b
            else:
                k='full' if model.startswith('full') else 'pca4' if model.startswith('shuffled4') else model.split('_')[0]
                # Negative control shuffles EEG among *training subjects within the same stimulus*.
                # The test data remain unchanged; training brain-rating linkage is broken.
                train_eeg=x[itr].copy()
                if model.startswith('shuffled'):
                    rng=np.random.default_rng(31876+fold)
                    for stimid in np.unique(stim[itr]):
                        ix=np.where(stim[itr]==stimid)[0]
                        if len(ix)>1:
                            train_eeg[ix]=train_eeg[rng.permutation(ix)]
                e1,e2=eeg_representations(train_eeg,x[ite],k,seed=991+fold)
                # Normalize the dimensionality's impact with a fixed scale.
                tr=np.column_stack([a, e1/np.sqrt(e1.shape[1])]);te=np.column_stack([b,e2/np.sqrt(e2.shape[1])])
            pred=fit_predict(tr,y[itr],te)
            for index,z in zip(ite,pred):
                predictions.append({'subject_id':subjects[index],'trial_id':str(df.loc[index,'trial_id']),
                                    'stimulus_id':stim[index],'fold':fold,'model':model,
                                    'observed':y[index],'predicted':float(z)})
    pred_df=pd.DataFrame(predictions)
    fold_records=[]
    for (model,subject),sub in pred_df.groupby(['model','subject_id']):
        fold_records.append({'model':model,'subject_id':subject,'n_trials':len(sub),
            'mse':mean_squared_error(sub.observed,sub.predicted),
            'mae':mean_absolute_error(sub.observed,sub.predicted)})
    per_subject=pd.DataFrame(fold_records)
    # Participant-level unit, not 210 repeated trials or electrodes.
    summary={m:{'mean_subject_mse':float(sub.mse.mean()),'sd_subject_mse':float(sub.mse.std(ddof=1)),
                'subjects':len(sub)} for m,sub in per_subject.groupby('model')}
    return pred_df,per_subject,summary

def paired_interval(per_subject, candidate, reference='stimulus_only',B=2000,seed=202609):
    pivot=per_subject.pivot(index='subject_id',columns='model',values='mse')
    dif=(pivot[candidate]-pivot[reference]).dropna().to_numpy()
    rng=np.random.default_rng(seed)
    draws=rng.choice(dif,size=(B,len(dif)),replace=True).mean(axis=1)
    return {'contrast':f'{candidate} minus {reference}', 'mean_mse_difference':float(dif.mean()),
            '95pct_exploratory_subject_bootstrap':[float(z) for z in np.quantile(draws,[.025,.975])],
            'n_subjects':len(dif),'status':'EXPLORATORY; not adjusted for model selection'}

def run(input_csv,manifest_json,out):
    source=Path(input_csv);audit=Path(manifest_json)
    df=pd.read_csv(source,low_memory=False)
    manifest=json.loads(audit.read_text())
    pp,ps,ss=evaluate(df,manifest)
    contrasts=[paired_interval(ps,k) for k in ('full_eeg_stimulus','pca4_eeg_stimulus',
                  'pca8_eeg_stimulus','random4_eeg_stimulus','shuffled4_eeg_stimulus')]
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    pp.to_csv(out/'predictions.csv',index=False,float_format='%.10g')
    ps.to_csv(out/'per_subject.csv',index=False,float_format='%.10g')
    provenance={'status':'EXPLORATORY human EEG predictive-model comparison; no consciousness measurement',
                'source_dataset_doi':manifest['source_doi'],
                'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                'manifest_sha256':hashlib.sha256(audit.read_bytes()).hexdigest(),
                'n_subjects':int(df.subject_id.nunique()),'n_trials':len(df),
                'summary':ss,'contrasts':contrasts,'information_leakage_controls':'GroupKFold by participant; all EEG scalers, PCA, and regressions fit to training participants only.'}
    (out/'summary.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return provenance

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--manifest',required=True)
    p.add_argument('--out',required=True)
    args=p.parse_args()
    print(json.dumps(run(args.input,args.manifest,args.out),indent=2))
if __name__=='__main__':main()
