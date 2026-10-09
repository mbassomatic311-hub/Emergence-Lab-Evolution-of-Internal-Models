"""Exploratory test of report-history gain after adaptive staircase controls.
Public trial tables only; no EEG or individual human outcomes persisted.
"""
from __future__ import annotations
import json
import numpy as np
from sklearn.linear_model import LogisticRegression,Ridge
from sklearn.metrics import log_loss,mean_squared_error
from behavioral_models import read_tsv,ROOT,extract_trials,add_histories,finite,boot_contrast

MODELS={
  "physical":[0,1],
  "staircase":[0,1,2,3,4,5,6,7],
  "staircase_plus_reports":[0,1,2,3,4,5,6,7,8,9,10],
  "staircase_plus_reports_and_time":[0,1,2,3,4,5,6,7,8,9,10,11]
}

def add_staircase_covariates(raw_rows):
    trials=add_histories(extract_trials(raw_rows))
    starts=[r for r in raw_rows if r["trial_type"]=="stim-adapt"]
    if len(starts)!=len(trials):raise RuntimeError("Trial row mismatch")
    amp=[finite(r.get("stimamp")) for r in starts]
    for i,t in enumerate(trials):
        prev=trials[i-1] if i else {}
        good=[r for r in trials[max(0,i-5):i] if r.get("valid")]
        prior_amp=[x for x in amp[max(0,i-5):i] if x is not None]
        t["amp"]=amp[i]
        t["prev_present"]=prev.get("present",.5)
        t["prev_dose"]=prev.get("dose",0.)
        t["prev_amp"]=amp[i-1] if i and amp[i-1] is not None else (amp[i] if amp[i] is not None else 0.)
        t["prev5_amp"]=float(np.mean(prior_amp)) if prior_amp else t["prev_amp"]
        t["prev5_present"]=float(np.mean([r["present"] for r in good])) if good else .5
    return trials

def get_matrices(trials):
    valid=[t for t in trials if t.get("valid") and t["amp"] is not None]
    if len(valid)<150:raise ValueError("Insufficient complete trial rows")
    X=np.array([[t["present"],t["dose"],t["amp"],t["prev_present"],t["prev_dose"],
                 t["prev_amp"],t["prev5_amp"],t["prev5_present"],
                 t["previous_report"],t["previous_confidence"],t["prior_5_report_rate"],
                 t["index_scaled"]] for t in valid])
    y=np.array([t["yes"] for t in valid])
    c=np.array([t["conf"] for t in valid])
    idx=np.array([t["idx"] for t in valid])
    a=np.where(idx<int(.65*len(trials)))[0]
    b=np.where(idx>=int(.65*len(trials)))[0]
    if len(a)<100 or len(b)<50 or a.max()>=b.min():raise RuntimeError("Unsafe split")
    return X,y,c,a,b

def evaluate(trials):
    X,y,c,train,test=get_matrices(trials)
    scores={}
    for name,cols in MODELS.items():
        a,b=X[train][:,cols],X[test][:,cols]
        mu,sd=a.mean(axis=0),np.maximum(a.std(axis=0),1e-6)
        a,b=(a-mu)/sd,(b-mu)/sd
        model=LogisticRegression(C=1.,max_iter=600)
        model.fit(a,y[train])
        p=np.clip(model.predict_proba(b)[:,1],1e-5,1-1e-5)
        scores[name+"_logloss"]=float(log_loss(y[test],p,labels=[0,1]))
        reg=Ridge(alpha=20.)
        reg.fit(a,c[train])
        scores[name+"_confidence_mse"]=float(mean_squared_error(c[test],np.clip(reg.predict(b),0,1)))
    scores["n_train"]=len(train);scores["n_test"]=len(test)
    return scores

def assemble(results):
    comp=[
        ("staircase_plus_reports_logloss","staircase_logloss"),
        ("staircase_plus_reports_confidence_mse","staircase_confidence_mse"),
        ("staircase_plus_reports_and_time_logloss","staircase_logloss"),
        ("staircase_plus_reports_and_time_confidence_mse","staircase_confidence_mse")
    ]
    return {
        "source":"OpenNeuro ds001785 v1.1.1",
        "research_status":"EXPLORATORY behavioral-only staircase control; NO EEG and no consciousness measurement",
        "independent_participants":len(results),
        "n_training_trials":sum(r["n_train"] for r in results),
        "n_heldout_trials":sum(r["n_test"] for r in results),
        "mean_per_participant":{k:float(np.mean([r[k] for r in results]))
                                 for k in results[0] if k not in ("n_train","n_test")},
        "contrasts":[boot_contrast(results,a,b) for a,b in comp],
        "limitations":"Staircase and preceding reports are endogenous; this observational control cannot identify causal history effects. Hyperparameters and model selection were not prospectively registered."
    }

def main():
    subjects=read_tsv(ROOT+"/participants.tsv")
    results=[]
    for row in subjects:
        sub=row["participant_id"]
        if not sub.startswith("sub-") or not sub[4:].isdigit():raise ValueError("Invalid public subject id")
        source=ROOT+f"/{sub}/ses-01/eeg/{sub}_ses-01_task-adapt_run-01_events.tsv"
        results.append(evaluate(add_staircase_covariates(read_tsv(source))))
    out=assemble(results)
    from pathlib import Path
    Path("staircase_control_aggregate.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":main()
