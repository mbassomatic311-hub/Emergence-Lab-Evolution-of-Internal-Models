"""Study 11B: exploratory REAL human behavioral prediction with a prospective time split.

Source: publicly released OpenNeuro ds001785 v1.1.1 event metadata, exact
upstream revision, 18 volunteers. NO EEG signal used. Reported detection
and confidence are distinct outcomes, NOT degrees of consciousness.
No person/trial-level records are written or published.
"""
from __future__ import annotations
import csv, io, json, urllib.request
import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, brier_score_loss, mean_squared_error

REV="53be0167e7068aba693d57923eb4c9c037878159"
ROOT=f"https://raw.githubusercontent.com/OpenNeuroDatasets/ds001785/{REV}"
RESULTS={"hit","miss","cr","fa"}

def read_tsv(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"EmergenceLab-Study11B-exploratory/1"}),timeout=50) as r:
        b=r.read(250001)
    if len(b)>250000:raise ValueError("Oversized public event table refused")
    return list(csv.DictReader(io.StringIO(b.decode("utf-8-sig")),delimiter="\t"))

def finite(x):
    try:
        n=float(x)
        return n if np.isfinite(n) else None
    except (TypeError,ValueError):
        return None

def extract_trials(rows):
    starts=[i for i,r in enumerate(rows) if r["trial_type"]=="stim-adapt"]
    data=[]
    for t,i in enumerate(starts):
        block=rows[i:starts[t+1] if t+1<len(starts) else len(rows)]
        outcome=[r["trial_type"] for r in block if r["trial_type"] in RESULTS]
        confidence=finite(block[0].get("confidence"))
        stim=finite(block[0].get("stimamp"))
        valid=(len(outcome)==1 and confidence is not None and 0<=confidence<=1
               and stim is not None and stim>=0
               and sum(r["trial_type"]=="conf" for r in block)==1
               and sum(r["trial_type"]=="conf-resp" for r in block)==1)
        if valid:
            code=outcome[0]
            presented=float(code in ("hit","miss"))
            yes=float(code in ("hit","fa"))
            data.append({"idx":t,"valid":True,"present":presented,
                         "dose":presented*stim,"yes":yes,"conf":confidence,
                         "accurate":float(code in ("hit","cr"))})
        else:
            data.append({"idx":t,"valid":False})
    return data

def add_histories(trials):
    for i,tr in enumerate(trials):
        prior=trials[:i]
        latest=prior[-1] if prior else {}
        good=[p for p in prior[-5:] if p.get("valid")]
        tr["previous_report"]=latest["yes"] if latest.get("valid") else 0.5
        tr["previous_confidence"]=latest["conf"] if latest.get("valid") else 0.5
        tr["prior_5_report_rate"]=sum(p["yes"] for p in good)/len(good) if good else 0.5
        tr["index_scaled"]=i / max(1,len(trials)-1)
    return trials

def matrices(trials):
    good=[t for t in add_histories(trials) if t.get("valid")]
    if len(good)<150:raise ValueError("Too few complete trials")
    ntrials=len(trials)
    X=np.array([[t["present"],t["dose"],t["previous_report"],
                 t["previous_confidence"],t["prior_5_report_rate"],t["index_scaled"]]
                for t in good])
    y=np.array([t["yes"] for t in good])
    conf=np.array([t["conf"] for t in good])
    accuracy=np.array([t["accurate"] for t in good])
    seq=np.array([t["idx"] for t in good])
    itr=np.where(seq<int(ntrials*.65))[0]
    ite=np.where(seq>=int(ntrials*.65))[0]
    if len(itr)<100 or len(ite)<50:raise ValueError("Insufficient chronological holdout")
    return X,y,conf,accuracy,itr,ite

def fit_score(trials,seed=7):
    X,y,conf,accuracy,train,test=matrices(trials)
    if len(set(y[train]))!=2:raise ValueError("Training data lack both response classes")
    scores={}
    def detection(kind, cols):
        if kind=="constant":
            p=np.full(len(test),(sum(y[train])+1)/(len(train)+2))
        else:
            # standardization performed on TRAINING period only
            a=X[train][:,cols].copy();b=X[test][:,cols].copy()
            mu=a.mean(axis=0);sd=np.maximum(a.std(axis=0),1e-6)
            if kind=="history_shuffled":
                rng=np.random.default_rng(seed)
                a[:,2:]=a[rng.permutation(len(a)),2:]
            clf=LogisticRegression(C=1.0,max_iter=600)
            clf.fit((a-mu)/sd,y[train])
            p=clf.predict_proba((b-mu)/sd)[:,1]
        p=np.clip(p,1e-5,1-1e-5)
        return float(log_loss(y[test],p,labels=[0,1])),float(brier_score_loss(y[test],p))
    for name,cols in [("constant",[]),("stimulus",[0,1]),
                      ("stimulus_history",[0,1,2,3,4,5]),
                      ("history_shuffled",[0,1,2,3,4,5])]:
        ll,br=detection(name,cols)
        scores[name+"_logloss"]=ll
        scores[name+"_brier"]=br

    for name,cols in [("constant",[]),("stimulus",[0,1]),
                      ("stimulus_history",[0,1,2,3,4,5])]:
        if name=="constant":predict=np.full(len(test),np.mean(conf[train]))
        else:
            a=X[train][:,cols];b=X[test][:,cols]
            mu=a.mean(axis=0);sd=np.maximum(a.std(axis=0),1e-6)
            reg=Ridge(alpha=20.0)
            reg.fit((a-mu)/sd,conf[train])
            predict=np.clip(reg.predict((b-mu)/sd),0,1)
        scores[name+"_confidence_mse"]=float(mean_squared_error(conf[test],predict))
    scores["n_train"]=len(train);scores["n_test"]=len(test)
    scores["heldout_accuracy"]=float(np.mean(accuracy[test]))
    scores["heldout_mean_confidence"]=float(np.mean(conf[test]))
    scores["heldout_report_yes_rate"]=float(np.mean(y[test]))
    scores["n_total_complete"]=len(y)
    return scores

def boot_contrast(results,name_a,name_b,B=2000,seed=3432):
    dif=np.array([r[name_a]-r[name_b] for r in results])
    rng=np.random.default_rng(seed)
    draws=np.mean(rng.choice(dif,size=(B,len(dif)),replace=True),axis=1)
    return {"comparison":f"{name_a} minus {name_b} (lower is better)",
            "average_participant_difference":float(np.mean(dif)),
            "descriptive_95pct_bootstrap":[float(x) for x in np.quantile(draws,[.025,.975])],
            "number_of_independent_participants":len(dif),
            "confirmatory":False}

def main():
    participants=read_tsv(ROOT+"/participants.tsv")
    all_results=[]
    for row in participants:
        sub=row["participant_id"]
        if not sub.startswith("sub-") or not sub[4:].isdigit():raise ValueError("Unsafe subject id")
        rows=read_tsv(ROOT+f"/{sub}/ses-01/eeg/{sub}_ses-01_task-adapt_run-01_events.tsv")
        all_results.append(fit_score(extract_trials(rows)))
    keys=[k for k in all_results[0] if k not in ("n_train","n_test","n_total_complete")]
    out={
        "research_status":"EXPLORATORY human behavior only; NO EEG analyzed; not consciousness measurement",
        "source":"OpenNeuro ds001785 v1.1.1 public task event tables",
        "upstream_commit":REV,
        "train_test":"within participant earliest 65% starts trained, latest 35% untouched test",
        "n_independent_participants":len(all_results),
        "n_training_trials":sum(r["n_train"] for r in all_results),
        "n_heldout_trials":sum(r["n_test"] for r in all_results),
        "mean_per_participant":{k:float(np.mean([r[k] for r in all_results])) for k in keys},
        "contrasts":[
            boot_contrast(all_results,"stimulus_logloss","constant_logloss"),
            boot_contrast(all_results,"stimulus_history_logloss","stimulus_logloss"),
            boot_contrast(all_results,"history_shuffled_logloss","stimulus_logloss"),
            boot_contrast(all_results,"stimulus_confidence_mse","constant_confidence_mse"),
            boot_contrast(all_results,"stimulus_history_confidence_mse","stimulus_confidence_mse")
        ],
        "caveats":"Stimulus intensity adjusted by adaptive staircase; past choices are correlated with experimental stimulus adjustments. Predictive association is not a causal memory effect. Catch flags inferred from behavioral SDT coding. Model hyperparameters and design not preregistered."
    }
    from pathlib import Path
    p=Path("behavioral_aggregate.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":main()
